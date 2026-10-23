"""P1.1 - Đọc PDF thành dòng. Số (#) khớp mục 5 của docs/phases/P1/P1.1_plan.md."""

import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

import pymupdf
import pytest

from dataminer.devtools.sample_book import SampleBook
from dataminer.ingest.pdf_reader import detect_columns, read_lines, reading_order
from dataminer.model.line import Line
from tests.conftest import SampleBookFor


@pytest.fixture(scope="module")
def book(sample_book_for: SampleBookFor) -> SampleBook:
    return sample_book_for(7)


@pytest.fixture(scope="module")
def lines(book: SampleBook) -> list[Line]:
    return read_lines(book.pdf_path, book_id="book01")


def _nfc_words(text: str) -> Counter[str]:
    return Counter(unicodedata.normalize("NFC", text).split())


def test_01_words_per_page_match_truth(book: SampleBook, lines: list[Line]) -> None:
    for page in book.truth["pages"]:
        n = page["pdf_page"]
        expected: Counter[str] = Counter()
        for ln in book.truth["lines"]:
            if ln["pdf_page"] == n:
                expected += _nfc_words(ln["ocr"])
        got: Counter[str] = Counter()
        for ln in lines:
            if ln.page == n:
                got += Counter(ln.text.split())
        assert got == expected, f"trang {n}"


def test_02_reading_order_table_row_major(book: SampleBook, lines: list[Line]) -> None:
    """16 ô bảng ra liền nhau, đúng thứ tự hàng → cột (so với bản OCR trong đáp án,
    vì ô có thể bị cài lỗi, vd. "Thuốc" → "Thuộc")."""
    cells = sorted(
        (ln for ln in book.truth["lines"] if ln["role"] == "table"),
        key=lambda ln: (ln["row"], ln["col"]),
    )
    expected = [unicodedata.normalize("NFC", c["ocr"]) for c in cells]
    page9 = [ln.text for ln in lines if ln.page == 9]
    start = page9.index(expected[0])
    assert page9[start : start + len(expected)] == expected
    assert len(expected) == 16
    assert expected[9] == "l g"  # lỗi liều cài sẵn - vẫn đúng ô (hàng 2, cột 2)


def test_02b_body_top_to_bottom(lines: list[Line]) -> None:
    for page in {ln.page for ln in lines}:
        on_page = [ln for ln in lines if ln.page == page]
        assert [ln.index for ln in on_page] == list(range(len(on_page)))
        centers = [(ln.bbox[1] + ln.bbox[3]) / 2 for ln in on_page]
        for prev, cur, ln in zip(centers, centers[1:], on_page[1:], strict=False):
            assert cur >= prev - 0.4 * ln.size, f"trang {page}: {ln.text}"


def test_03_nfd_normalized_and_flagged(book: SampleBook, lines: list[Line]) -> None:
    flagged = [ln for ln in lines if "nfd_fixed" in ln.flags]
    n_nfd = sum(e["kind"] == "nfd_line" for e in book.truth["ocr_errors"])
    assert len(flagged) == n_nfd == 2
    for ln in flagged:
        assert unicodedata.is_normalized("NFC", ln.text)
        assert not unicodedata.is_normalized("NFC", ln.text_raw)
        assert unicodedata.normalize("NFC", ln.text_raw) == ln.text
    assert all(unicodedata.is_normalized("NFC", ln.text) for ln in lines)


def test_04_page_filter(book: SampleBook) -> None:
    pilot = read_lines(book.pdf_path, pages=(4, 9))
    assert {ln.page for ln in pilot} == {4, 5, 6, 7, 8, 9}
    assert not any("MỤC LỤC" in ln.text for ln in pilot)


def test_05_blank_page(book: SampleBook) -> None:
    assert read_lines(book.pdf_path, pages=(2, 2)) == []


def test_06_stable_ids(book: SampleBook, lines: list[Line]) -> None:
    again = read_lines(book.pdf_path, book_id="book01")
    assert [ln.id for ln in again] == [ln.id for ln in lines]
    assert len({ln.id for ln in lines}) == len(lines)
    other_book = read_lines(book.pdf_path, book_id="book02", pages=(4, 4))
    assert other_book[0].id != next(ln.id for ln in lines if ln.page == 4)


def test_06b_zones_and_page_size(lines: list[Line]) -> None:
    footer = [ln for ln in lines if ln.text.startswith("– ")]
    assert footer
    assert all(ln.zone == "bottom" for ln in footer)
    assert all(ln.page_width == 420.0 and ln.page_height == 595.0 for ln in lines)


def _two_column_pdf(path: Path) -> Path:
    doc = pymupdf.open()
    page = doc.new_page(width=420, height=595)
    for i in range(10):
        y = 80 + i * 16
        page.insert_text((40, y), f"left column line {i}", fontsize=10)
        page.insert_text((230, y), f"right column line {i}", fontsize=10)
    doc.save(path)
    return path


def test_07_detect_columns(tmp_path: Path, lines: list[Line]) -> None:
    for page in {ln.page for ln in lines}:
        assert not detect_columns([ln for ln in lines if ln.page == page]), page
    assert not any("possible_two_columns" in ln.flags for ln in lines)

    two = read_lines(_two_column_pdf(tmp_path / "two.pdf"))
    assert detect_columns(two)
    assert all("possible_two_columns" in ln.flags for ln in two)


def _item(text: str, x: float, y: float, size: float = 10) -> dict[str, Any]:
    return {"text_raw": text, "bbox": (x, y, x + 50, y + size * 1.3), "size": size}


def test_reading_order_groups_jittered_rows() -> None:
    """Ô bảng cùng hàng lệch dọc 1pt vẫn cùng hàng; trả về trái → phải, hàng trên trước."""
    items = [
        _item("C2", 250, 101),
        _item("A1", 50, 80),
        _item("A2", 50, 100),
        _item("B1", 150, 79.2),
        _item("B2", 150, 100.6),
    ]
    assert [it["text_raw"] for it in reading_order(items)] == ["A1", "B1", "A2", "B2", "C2"]


def test_line_text_raw_defaults_to_text() -> None:
    ln = Line(
        id="x",
        page=1,
        index=0,
        text="đau",
        bbox=(0, 0, 1, 1),
        size=10,
        font="f",
        bold=False,
        zone="body",
    )
    assert ln.text_raw == "đau"
    assert ln.flags == []


def test_02c_reading_order_when_pdf_stores_text_out_of_order(tmp_path: Path) -> None:
    """Phần mềm OCR thật hay ghi text theo CỘT hoặc lộn xộn; sách mẫu thì ghi đúng thứ tự nên
    không kiểm được điều này. PDF ở đây ghi bảng theo cột, lệch dọc vài pt, và ghi dòng cuối
    trang TRƯỚC - read_lines phải trả về đúng thứ tự đọc."""
    rows = [["Thuốc", "Liều", "Số lần"], ["Omeprazol", "20 mg", "2"], ["Amoxicilin", "1 g", "2"]]
    doc = pymupdf.open()
    page = doc.new_page(width=420, height=595)
    page.insert_font(fontname="vi", fontbuffer=pymupdf.Font("notos").buffer)  # đủ chữ Việt
    page.insert_text((48, 300), "Dòng cuối trang.", fontsize=10, fontname="vi")
    for c, x in enumerate((48, 170, 260)):  # theo cột
        for r, y in enumerate((120, 136, 152)):
            page.insert_text(
                (x, y + (1.2 if c == 1 else 0)), rows[r][c], fontsize=10, fontname="vi"
            )
    page.insert_text((48, 90), "Dòng đầu trang.", fontsize=10, fontname="vi")
    path = tmp_path / "out_of_order.pdf"
    doc.save(path)

    texts = [ln.text for ln in read_lines(path)]
    assert texts == ["Dòng đầu trang.", *[c for row in rows for c in row], "Dòng cuối trang."]
