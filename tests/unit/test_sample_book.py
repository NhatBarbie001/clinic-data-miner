"""P0.5a - Sách mẫu tổng hợp: 2 lớp (ảnh + text OCR ẩn), đáp án khớp PDF, sinh xác định."""

import json
import unicodedata
from collections import Counter
from pathlib import Path

import pymupdf
import pytest

from dataminer.devtools.sample_book import FRONT_PAGES, SampleBook, make_sample_book


@pytest.fixture(scope="module")
def book(tmp_path_factory: pytest.TempPathFactory) -> SampleBook:
    return make_sample_book(tmp_path_factory.mktemp("book"), seed=7)


def _words(text: str) -> Counter[str]:
    return Counter(unicodedata.normalize("NFC", text).split())


def test_pdf_has_image_layer_on_every_page_and_text_except_blank(book: SampleBook) -> None:
    doc = pymupdf.open(book.pdf_path)
    assert doc.page_count == len(book.truth["pages"])
    for i in range(doc.page_count):
        page = doc[i]
        assert page.get_images(), f"trang {i + 1} thiếu lớp ảnh"
        has_text = bool(page.get_text().strip())
        assert has_text == book.truth["pages"][i]["has_text"]
    assert [p["pdf_page"] for p in book.truth["pages"] if not p["has_text"]] == [2]


def test_extracted_text_matches_truth_ocr_layer(book: SampleBook) -> None:
    doc = pymupdf.open(book.pdf_path)
    for page in book.truth["pages"]:
        n = page["pdf_page"]
        expected: Counter[str] = Counter()
        for ln in book.truth["lines"]:
            if ln["pdf_page"] == n:
                expected += _words(ln["ocr"])
        assert _words(doc[n - 1].get_text()) == expected, f"trang {n}"


def test_ocr_layer_loses_bold(book: SampleBook) -> None:
    doc = pymupdf.open(book.pdf_path)
    fonts = {
        span["font"]
        for i in range(doc.page_count)
        for block in doc[i].get_text("dict")["blocks"]
        if block["type"] == 0
        for line in block["lines"]
        for span in line["spans"]
    }
    assert fonts == {"Noto Sans Regular"}


def test_every_error_kind_present(book: SampleBook) -> None:
    kinds = Counter(e["kind"] for e in book.truth["ocr_errors"])
    for kind in (
        "drop_diacritics",
        "wrong_tone",
        "char_confusion",
        "merge_words",
        "digit_confusion",
        "nfd_line",
    ):
        assert kinds[kind] >= 1, kind


def test_dose_errors_injected_where_intended(book: SampleBook) -> None:
    errors = {e["corrupted"]: e for e in book.truth["ocr_errors"] if e["kind"] == "digit_confusion"}
    assert set(errors) == {"Paracetamol 5OO mg", "l g"}
    assert errors["l g"]["line_clean"] == "1 g"  # đúng ô liều trong bảng, không phải "1 giờ"
    text = "".join(pymupdf.open(book.pdf_path)[i].get_text() for i in range(9))
    assert "5OO mg" in text
    assert "Paracetamol 500 mg" not in text


def test_header_footer_never_corrupted(book: SampleBook) -> None:
    for ln in book.truth["lines"]:
        if ln["role"] in ("header", "footer"):
            assert ln["ocr"] == ln["text"]


def test_page_numbering_and_toc(book: SampleBook) -> None:
    pages = book.truth["pages"]
    assert [p["printed_page"] for p in pages[:FRONT_PAGES]] == [None] * FRONT_PAGES
    for p in pages[FRONT_PAGES:]:
        assert p["printed_page"] == p["pdf_page"] - FRONT_PAGES
        assert p["footer"] == f"– {p['printed_page']} –"
        assert (p["header"] is None) == p["chapter_start"]
    headings = book.truth["headings"]
    for entry in book.truth["toc"]:
        assert entry["pdf_page"] == entry["printed_page"] + FRONT_PAGES
        on_page = [h for h in headings if h["pdf_page"] == entry["pdf_page"]]
        assert any(h["level"] == entry["level"] for h in on_page), entry
    levels = Counter(h["level"] for h in headings)
    assert levels["chapter"] == 2
    assert levels["disease"] == 3


def test_table_recorded(book: SampleBook) -> None:
    (table,) = book.truth["tables"]
    assert table["caption"].startswith("Bảng 2.1.")
    assert table["rows"][0] == ["Thuốc", "Liều mỗi lần", "Số lần/ngày", "Thời gian"]
    assert len(table["rows"]) == 4


def test_deterministic_same_seed(book: SampleBook, tmp_path: Path) -> None:
    again = make_sample_book(tmp_path, seed=7)
    assert again.truth == book.truth
    a, b = pymupdf.open(book.pdf_path), pymupdf.open(again.pdf_path)
    assert [a[i].get_text() for i in range(a.page_count)] == [
        b[i].get_text() for i in range(b.page_count)
    ]


def test_different_seed_different_errors(book: SampleBook, tmp_path: Path) -> None:
    other = make_sample_book(tmp_path, seed=8)
    assert other.truth["ocr_errors"] != book.truth["ocr_errors"]
    assert [h["text"] for h in other.truth["headings"]] == [
        h["text"] for h in book.truth["headings"]
    ]  # cấu trúc giữ nguyên, chỉ lỗi OCR thay đổi


def test_truth_file_written(book: SampleBook) -> None:
    on_disk = json.loads(book.truth_path.read_text(encoding="utf-8"))
    assert on_disk == book.truth
    assert book.pdf_path.stat().st_size < 1_000_000


def test_ocr_text_composes_to_real_vietnamese_letters(book: SampleBook) -> None:
    """Sau NFC không được còn dấu rời (vd. "đá̆c" - sắc chồng trăng không ghép được).
    Lỗi sai dấu phải cho ra chữ có thật ("đắc"), như phần mềm OCR thật sinh ra."""
    for ln in book.truth["lines"]:
        composed = unicodedata.normalize("NFC", ln["ocr"])
        leftovers = [c for c in composed if unicodedata.combining(c)]
        assert not leftovers, (ln["ocr"], leftovers)


@pytest.mark.parametrize("word", ["đặc", "ặ", "Thuốc", "quyết"])
def test_swap_tone_keeps_vowel_marks(word: str) -> None:
    import random

    from dataminer.devtools.sample_book import _swap_tone

    for seed in range(10):
        out = _swap_tone(word, random.Random(seed))
        assert out is not None
        assert out != word
        assert not any(unicodedata.combining(c) for c in out)  # đã ghép thành 1 ký tự
        assert len(out) == len(word)
