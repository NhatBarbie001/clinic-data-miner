"""P2R I1-I2 - sách IASP: hồ sơ sách + luật đọc trang (L2-L4, L7, L10, L14).

Phần lớn dùng dòng TỰ DỰNG (không cần file sách). Test cuối chạy trên PDF thật nếu máy có file
`data/books/iasp/raw/…` (git bỏ qua) - không có thì tự bỏ qua.
"""

from pathlib import Path
from typing import Any

import pytest

from dataminer.books.iasp import layout
from dataminer.books.iasp.rules import RULES
from dataminer.books.registry import rules_for
from dataminer.core.config import BlocksCfg
from dataminer.model.line import Line
from dataminer.pdf.reader import body_font_size, read_lines
from dataminer.pipeline.p1 import resolve_pages
from dataminer.text import blocks as text_blocks
from dataminer.text.blocks import join_text
from tests.unit.llm_fakes import ROOT, make_settings

PDF = ROOT / "data" / "books" / "iasp" / "raw" / "classification_of_chronic_pain.pdf"


def item(text: str, x0: float, y: float, x1: float | None = None) -> dict[str, Any]:
    return {
        "text_raw": text,
        "bbox": (x0, y, x1 if x1 is not None else x0 + 220, y + 10),
        "size": 10.0,
    }


def line(
    text: str, *, x0: float = 65, y: float = 100, size: float = 10.0, bold: bool = False,
    page: int = 137, x1: float | None = None,
) -> Line:  # fmt: skip
    return Line(
        id=f"l{page}-{x0}-{y}",
        page=page,
        index=int(y),
        text=text,
        bbox=(x0, y, x1 if x1 is not None else x0 + 220, y + 10),
        size=size,
        font="TimesNewRoman,Bold" if bold else "TimesNewRoman",
        bold=bold,
        zone="body",
    )


# ---------------------------------------------------------------- I1: hồ sơ sách


def test_iasp_profile(tmp_path: Path) -> None:
    from dataminer.core.config import load_settings

    make_settings(tmp_path)
    s = load_settings(tmp_path, env={"OPENROUTER_API_KEY": "x"}, book="iasp")
    assert rules_for(s) is RULES
    assert s.project.book_file == "classification_of_chronic_pain.pdf"
    assert s.project.content_pages == (53, 222)  # L1: Part II
    assert (s.pilot.page_start, s.pilot.page_end) == (137, 143)  # GROUP XI
    assert s.p1.fix.enabled is False and s.p1.blocks.detect_tables is False
    assert s.p1.blocks.dehyphenate is True and "—" in s.p1.blocks.bullet_markers
    assert s.paths.raw_dir == (tmp_path / "data" / "books" / "iasp" / "raw").resolve()
    assert resolve_pages(s, "all", None, 238) == (53, 222)
    assert resolve_pages(s, "pilot", None, 238) == (137, 143)


# ---------------------------------------------------------------- L4: thứ tự đọc 2 cột


def test_column_order_reads_left_column_then_right() -> None:
    page = [
        item("Page 121", 510, 33, 545),
        item("Phạm vi phải 1", 318, 120),
        item("Trái 1", 65, 120),
        item("Phạm vi phải 2", 318, 131),
        item("Trái 2", 65, 131),
        item("GROUP XI:  PAIN IN THE SHOULDER, ARM, AND HAND", 65, 200, 470),  # vắt ngang
        item("Trái 3", 65, 220),
        item("Phải 3", 318, 220),
        item("Page 120 is BLANK", 200, 400, 420),  # L3: rác
    ]
    order = [it["text_raw"] for it in layout.column_order(page)]
    assert order == [
        "Trái 1", "Trái 2", "Page 121", "Phạm vi phải 1", "Phạm vi phải 2",
        "GROUP XI:  PAIN IN THE SHOULDER, ARM, AND HAND", "Trái 3", "Phải 3",
    ]  # fmt: skip
    assert [layout.column_of(it) for it in page[:3]] == ["right", "right", "left"]


def test_single_column_page_keeps_vertical_order() -> None:
    page = [item("Dòng 2 dài cả trang", 65, 130, 550), item("Dòng 1 dài cả trang", 65, 110, 550)]
    assert [it["text_raw"] for it in layout.column_order(page)] == [
        "Dòng 1 dài cả trang",
        "Dòng 2 dài cả trang",
    ]


def test_table_page_reads_by_rows() -> None:
    """L14: bảng đối chiếu - cột mã IHS bắt đầu ở x≈306 (trùng khe giữa) → đọc theo HÀNG."""
    rows = [("1-6", "Central Pain", "12.7.2"), ("II-1", "Trigeminal neuralgia", "12.2.1")]
    page = [
        item(cell, x, 300 + 18 * r, x + 30)
        for r, row in enumerate(rows * 3)
        for cell, x in zip(row, (60, 98, 306), strict=True)
    ]
    assert layout.is_table_page(page)
    assert [it["text_raw"] for it in layout.column_order(page)][:3] == [
        "1-6",
        "Central Pain",
        "12.7.2",
    ]
    assert not layout.is_table_page(page[:6])  # < 5 ô mã


# ---------------------------------------------------------------- L2, L7, L10, L14: từng dòng


@pytest.mark.parametrize(
    ("text", "number"),
    [("Page 121", 121), ("121", 121), ("PAGE 7", 7), ("Page 120 is BLANK", None), ("xvi", None)],
)
def test_page_number(text: str, number: int | None) -> None:
    assert RULES.page_number(text) == number


def test_classify_line_by_bold_and_size() -> None:
    cfg = BlocksCfg(bullet_markers=["-", "—"])
    body = 10.0
    assert (
        RULES.classify_line(line("Tumors of the Brachial Plexus", size=13.5, bold=True), body, cfg)
        == "heading"
    )
    assert RULES.classify_line(line("Definition", bold=True), body, cfg) == "heading"
    assert (
        RULES.classify_line(
            line("Summary of Essential Features and Diagnostic", bold=True), body, cfg
        )
        == "heading"
    )
    assert RULES.classify_line(line("Pain is severe.", bold=True), body, cfg) == "body"  # câu đậm
    assert RULES.classify_line(line("Definition"), body, cfg) == "body"  # không đậm
    assert (
        RULES.classify_line(line("Central Pain", bold=True, page=106), body, cfg) == "body"
    )  # L14
    assert (
        RULES.classify_line(line("HEADACHE CROSSWALK", size=13.5, bold=True, page=106), body, cfg)
        == "heading"
    )
    assert RULES.classify_line(line("— prevalence, sex ratio"), body, cfg) == "bullet_start"
    assert RULES.classify_line(line("Table 1 Codes"), body, cfg) == "caption"
    assert RULES.classify_line(line("1. Burning pain"), body, cfg) == "numbered_item"
    assert RULES.classify_line(line("ordinary text"), body, cfg) == "body"  # fmt: skip


@pytest.mark.parametrize(
    ("text", "number"),
    [
        ("GROUP XI:  PAIN IN THE SHOULDER, ARM, AND HAND", "GROUP XI"),
        ("E.", "E"),
        ("A. RELATIVELY GENERALIZED SYNDROMES", "A"),
        ("(XI-1)", None),  # mã đứng riêng dòng phải NỐI vào tên hội chứng (L7)
        ("Tumors of the Brachial Plexus (XI-1)", None),
        ("Definition", None),
    ],
)
def test_numbering(text: str, number: str | None) -> None:
    assert RULES.numbering(text) == number


# ---------------------------------------------------------------- ghép dòng (phần dùng chung)


def test_dehyphenate_uses_the_books_own_vocabulary() -> None:
    vocab = text_blocks.Vocab(
        ["the symptoms present early in life", "with anti-inflammatory drugs and rest"]
    )
    assert join_text("may pre-", "sent with", True, vocab) == "may present with"  # "pre" là tiền tố
    assert join_text("non-", "steroidal", True, vocab) == "non-steroidal"  # không bằng chứng
    assert (
        join_text("using anti-", "inflammatory drugs", True, vocab)
        == "using anti-inflammatory drugs"
    )


@pytest.mark.parametrize(
    ("a", "b", "joined"),
    [
        ("underlying dis-", "ease.", "underlying disease."),
        ("of the bra-", "chial plexus", "of the brachial plexus"),
        ("rectum (rec-", "tal pain)", "rectum (rectal pain)"),  # mảnh sau dấu ngoặc
        ("side-to-", "side asymmetry", "side-to-side asymmetry"),  # từ ghép: giữ gạch
        ("non-", "steroidal", "non-steroidal"),  # tiền tố viết có gạch
        ("anti-", "inflammatory", "anti-inflammatory"),
        ("type-", "II pattern", "type-II pattern"),  # sau là chữ hoa: giữ gạch
        ("end of sentence -", "next", "end of sentence - next"),
    ],
)
def test_dehyphenate(a: str, b: str, joined: str) -> None:
    assert join_text(a, b, dehyphenate=True) == joined
    if a.endswith("-") and a[-2:-1].isalpha():
        assert join_text(a, b) == a + b  # mặc định (sách mẫu): giữ nguyên hành vi cũ


def _blocks(rows: list[Line]) -> list[Any]:
    cfg = BlocksCfg(dehyphenate=True, detect_tables=False)
    return text_blocks.build_blocks(
        rows, 10.0, cfg, classify=RULES.classify_line, numbering=RULES.numbering
    )


def test_paragraph_continues_into_next_column() -> None:
    rows = [
        line("Definition", y=100, bold=True),
        line("Signs are loss of reflexes, sensation, and", y=111),
        line("muscle strength in the distribution of the", y=122),
        line("involved portion of the plexus.", y=50, x0=318),  # đầu cột phải, cao hơn
    ]
    out = _blocks(rows)
    assert [b.kind for b in out] == ["heading", "paragraph"]
    assert out[1].text.endswith("involved portion of the plexus.")
    assert "joined_across_columns" in out[1].flags


def test_finished_sentence_does_not_continue_into_next_column() -> None:
    rows = [
        line("The first paragraph ends here.", y=111),
        line("A new paragraph starts at the top of the right column.", y=50, x0=318),
    ]
    assert [b.text[:9] for b in _blocks(rows)] == ["The first", "A new par"]


def test_side_by_side_columns_are_not_a_table() -> None:
    rows = [line(f"Left {i}", y=100 + 11 * i) for i in range(4)] + [
        line(f"Right {i}", y=100 + 11 * i, x0=318) for i in range(4)
    ]
    assert all(b.kind != "table" for b in _blocks(rows))


# ---------------------------------------------------------------- trên PDF thật (nếu có)


@pytest.mark.skipif(not PDF.is_file(), reason="không có file sách IASP trên máy này")
def test_real_pdf_page_137_reading_order() -> None:
    page = read_lines(PDF, book_id="iasp", pages=(137, 137), order=RULES.order_lines)
    content = [ln for ln in page if RULES.page_number(ln.text) is None]
    cfg = BlocksCfg(dehyphenate=True, detect_tables=False, bullet_markers=["-", "—"])
    built = text_blocks.build_blocks(
        content, body_font_size(page), cfg, classify=RULES.classify_line, numbering=RULES.numbering
    )
    heads = [b.text for b in built if b.kind == "heading"]
    assert heads[:6] == [
        "E.",
        "LOCAL SYNDROMES OF THE UPPER LIMBS AND RELATIVELY GENERALIZED SYNDROMES OF THE UPPER "
        "AND LOWER LIMBS",
        "GROUP XI: PAIN IN THE SHOULDER, ARM, AND HAND",
        "Tumors of the Brachial Plexus (XI-1)",
        "Definition",
        "Site",
    ]
    assert "Chemical Irritation of the Brachial Plexus (XI-2)" in heads
    assert all(b.kind != "table" for b in built)
    assert any("underlying disease." in b.text for b in built)  # "dis-" + "ease"
