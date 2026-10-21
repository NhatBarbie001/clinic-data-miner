"""P1.2 - Header/footer/số trang. Số (#) khớp mục 5 của docs/phases/P1/P1.2_plan.md."""

from pathlib import Path

import pytest

from dataminer.core.config import FurnitureCfg
from dataminer.core.io import read_json
from dataminer.devtools.sample_book import SampleBook
from dataminer.evaluation.p1_eval import eval_furniture
from dataminer.ingest.page_furniture import (
    page_number_of,
    save_furniture,
    strip_furniture,
)
from dataminer.ingest.pdf_reader import Line, body_font_size, read_lines
from tests.conftest import SampleBookFor

ALL_PAGES = list(range(1, 10))


def run(book: SampleBook, lines: list[Line] | None = None):  # type: ignore[no-untyped-def]
    lines = lines if lines is not None else read_lines(book.pdf_path)
    return strip_furniture(lines, body_font_size(lines), pdf_pages=ALL_PAGES)


@pytest.fixture(scope="module")
def book(sample_book_for: SampleBookFor) -> SampleBook:
    return sample_book_for(7)


def line(
    text: str,
    *,
    page: int = 5,
    zone: str = "body",
    size: float = 10.5,
    index: int = 0,
    y: float = 300,
) -> Line:
    return Line(
        id=f"l{page}_{index}",
        page=page,
        index=index,
        text=text,
        bbox=(48, y, 300, y + 12),
        size=size,
        font="f",
        bold=False,
        zone=zone,
    )  # type: ignore[arg-type]


# ---------------------------------------------------------------- trên sách mẫu


@pytest.mark.parametrize("seed", [7, 2, 6])
def test_01_all_furniture_removed_nothing_else(sample_book_for: SampleBookFor, seed: int) -> None:
    sample = sample_book_for(seed)
    result = run(sample)
    report = eval_furniture(result, sample.truth)
    assert report["G1_furniture"]["pass"], report["G1_furniture"]
    assert report["G1_furniture"]["truth"] == 10
    assert len(result.content) + len(result.removed) == len(read_lines(sample.pdf_path))


def test_02_printed_page_mapping(book: SampleBook) -> None:
    result = run(book)
    report = eval_furniture(result, book.truth)
    assert report["G2_printed_pages"]["pass"], report
    assert [result.printed(p) for p in ALL_PAGES] == [None, None, None, 1, 2, 3, 4, 5, 6]
    assert all(p.source == "page_number" for p in result.pages if p.printed_page)
    assert result.warnings == []


def test_03_single_occurrence_chapter_header_removed(book: SampleBook) -> None:
    result = run(book)
    chapter_head = [r for r in result.removed if r.text.startswith("Chương 1.")]
    assert len(chapter_head) == 1  # chỉ xuất hiện ở 1 trang
    assert chapter_head[0].confidence == "medium"
    assert "chữ nhỏ" in chapter_head[0].reason


def test_04_missing_page_number_is_inferred(book: SampleBook) -> None:
    lines = [ln for ln in read_lines(book.pdf_path) if not (ln.page == 6 and ln.zone == "bottom")]
    result = run(book, lines)
    info = next(p for p in result.pages if p.page == 6)
    assert info.printed_page == 3
    assert info.source == "inferred"
    assert info.flags == ["printed_page_inferred"]


def test_05_conflicting_page_number(book: SampleBook) -> None:
    lines = read_lines(book.pdf_path)
    for ln in lines:
        if ln.page == 7 and ln.zone == "bottom":
            ln.text = "– 9 –"  # OCR đọc nhầm số trang
    result = run(book, lines)
    info = next(p for p in result.pages if p.page == 7)
    assert info.printed_page == 4
    assert info.flags == ["printed_page_conflict"]
    assert any("Trang PDF 7" in w and "đọc được là 9" in w for w in result.warnings)
    assert any("không nhất quán" in w for w in result.warnings)


# ---------------------------------------------------------------- không dựa trên sách mẫu


def test_06_body_sized_margin_line_kept() -> None:
    lines = [
        line("– 1 –", page=1, zone="bottom", size=9),
        line("– 2 –", page=2, zone="bottom", size=9),
        line(
            "vẫn là nội dung của đoạn văn dài chạm lề dưới.",
            page=2,
            zone="bottom",
            size=10.5,
            index=1,
        ),
    ]
    result = strip_furniture(lines, body_size=10.5)
    assert [ln.text for ln in result.content] == ["vẫn là nội dung của đoạn văn dài chạm lề dưới."]
    assert {r.kind for r in result.removed} == {"page_number"}


@pytest.mark.parametrize(
    ("text", "number"),
    [
        ("12", 12),
        ("- 12 -", 12),
        ("– 12 –", 12),
        ("Trang 12", 12),
        ("trang 7", 7),
        ("[12]", 12),
        ("12 tuổi", None),
        ("Bảng 12", None),
        ("1.2", None),
        ("", None),
        ("Chương 3", None),
    ],
)
def test_07_page_number_formats(text: str, number: int | None) -> None:
    assert page_number_of(text) == number


def test_07b_running_heads_differing_only_by_number_match() -> None:
    lines = [
        line("Bài 3 - Hô hấp", page=10, zone="top", size=10.5),
        line("Bài 4 - Hô hấp", page=11, zone="top", size=10.5),
    ]
    result = strip_furniture(lines, body_size=10.5)
    assert result.content == []
    assert all(r.reason == "lặp lại ở 2 trang" for r in result.removed)


def test_no_page_numbers_at_all() -> None:
    result = strip_furniture([line("Nội dung", page=3)], body_size=10.5)
    assert [p.printed_page for p in result.pages] == [None]
    assert "Không tìm thấy số trang in" in result.warnings[0]


def test_min_repeat_pages_from_config() -> None:
    lines = [line("Đầu trang", page=p, zone="top", size=10.5) for p in (1, 2)]
    assert strip_furniture(lines, 10.5, FurnitureCfg(min_repeat_pages=3)).removed == []
    assert len(strip_furniture(lines, 10.5, FurnitureCfg(min_repeat_pages=2)).removed) == 2


def test_save_furniture_traceable(book: SampleBook, tmp_path: Path) -> None:
    result = run(book)
    path = tmp_path / "furniture.json"
    save_furniture(result, path)
    data = read_json(path)
    assert "content" not in data
    assert len(data["removed"]) == 10
    assert all(item["line_id"].startswith("ln_") and item["reason"] for item in data["removed"])
    assert [p["printed_page"] for p in data["pages"]] == [None, None, None, 1, 2, 3, 4, 5, 6]
