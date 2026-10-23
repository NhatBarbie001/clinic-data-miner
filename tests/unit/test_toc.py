"""P2.1 - Mục lục. Số (#) khớp mục 5 của docs/phases/P2/P2.1_plan.md.

Sách mẫu chỉ có 1 trang mục lục, 5 dòng, chấm dẫn đều - phần "không dựa trên sách mẫu" (dòng tự
dựng) là BẮT BUỘC: ngắt 2 dòng, nhiều trang, chấm kiểu khác, số trang giảm, không có mục lục.
"""

import json
import shutil
from pathlib import Path

import pymupdf
import pytest
from typer.testing import CliRunner

from dataminer.books.book01.toc import (
    build_toc,
    extract_toc,
    find_toc_pages,
    parse_entry_line,
    parse_toc,
)
from dataminer.cli import app
from dataminer.core.config import TocCfg
from dataminer.devtools.sample_book import SampleBook
from dataminer.evaluation.truth.p2_eval import all_pass, eval_toc
from dataminer.model.line import Line, Zone
from dataminer.structure.toc_match import match_key, norm_title
from tests.conftest import SampleBookFor
from tests.unit.llm_fakes import copy_configs

runner = CliRunner()
_counter = iter(range(100_000))


def mk(
    text: str, y: float, x: float = 48, *, page: int = 3, size: float = 10.5, zone: Zone = "body"
) -> Line:
    """Dòng tự dựng: cao 13pt; các mục mục lục cách nhau 16pt."""
    n = next(_counter)
    return Line(
        id=f"t{n}",
        page=page,
        index=n,
        text=text,
        bbox=(x, y, x + 280, y + 13),
        size=size,
        font="f",
        bold=False,
        zone=zone,
    )


def toc_page(rows: list[tuple[str, float]], page: int = 3, start: float = 100) -> list[Line]:
    """Trang mục lục: tiêu đề "MỤC LỤC" + các dòng (text, x0) cách nhau 16pt."""
    out = [mk("MỤC LỤC", 60, 170, page=page, size=14)]
    out += [mk(text, start + 16 * i, x, page=page) for i, (text, x) in enumerate(rows)]
    return out


def content_pages(first_pdf: int, n: int, offset: int) -> list[Line]:
    """n trang nội dung, mỗi trang 1 dòng thân bài + footer "– số trang in –"."""
    out: list[Line] = []
    for pdf in range(first_pdf, first_pdf + n):
        out.append(mk(f"Nội dung trang {pdf}.", 100, page=pdf, size=10))
        out.append(mk(f"– {pdf - offset} –", 560, 200, page=pdf, size=8.5, zone="bottom"))
    return out


@pytest.fixture(scope="module")
def book(sample_book_for: SampleBookFor) -> SampleBook:
    return sample_book_for(7)


# ---------------------------------------------------------------- #1-3 trên sách mẫu


@pytest.mark.parametrize("seed", [7, 1, 4])
def test_01_sample_book_matches_truth(sample_book_for: SampleBookFor, seed: int) -> None:
    """Seed 7: lỗi dấu 'hỏa'; seed 1: 'Cbương 2' (OCR phá chữ Chương); seed 4: dính từ."""
    sample = sample_book_for(seed)
    result = extract_toc(sample.pdf_path, book_id="book01")
    report = eval_toc(result, sample.truth)
    assert all_pass(report), report
    assert result.toc_pages == [3]
    assert result.source == "auto"
    assert result.page_offset == 3
    assert [e.level for e in result.entries] == [
        "chapter",
        "disease",
        "disease",
        "chapter",
        "disease",
    ]
    assert [(e.printed_page, e.pdf_page) for e in result.entries] == [
        (1, 4),
        (1, 4),
        (3, 6),
        (5, 8),
        (5, 8),
    ]


def test_01b_ocr_broken_chapter_word_uses_indent(sample_book_for: SampleBookFor) -> None:
    """Seed 1: OCR đọc 'Chương 2' thành 'Cbương 2' → mẫu chữ trượt, thụt lề vẫn cho chapter."""
    entry = extract_toc(sample_book_for(1).pdf_path, book_id="book01").entries[3]
    assert entry.title.startswith("Cbương 2")
    assert entry.level == "chapter"
    assert entry.flags == ["level_conflict"]


def test_02_ocr_tone_error_still_matches(book: SampleBook) -> None:
    chapter2 = extract_toc(book.pdf_path, book_id="book01").entries[3]
    assert chapter2.title == "Chương 2. Bệnh tiêu hỏa"  # nguyên văn OCR, không sửa
    assert chapter2.title_norm == "chuong 2. benh tieu hoa"
    assert match_key(chapter2.title) == match_key("CHƯƠNG 2. BỆNH TIÊU HÓA")


def test_02b_match_key_tolerates_merged_words() -> None:
    assert match_key("Thoái hóa khớpgối") == match_key("THOÁI HÓA KHỚP GỐI")
    assert norm_title("  Viêm   KHỚṔ ") == "viem khop"  # NFD + khoảng trắng thừa
    assert match_key("Viêm gan B") != match_key("Viêm gan C")


def test_03_config_pages_skips_detection(book: SampleBook) -> None:
    auto = extract_toc(book.pdf_path, book_id="book01")
    fixed = extract_toc(book.pdf_path, book_id="book01", cfg=TocCfg(pages=(3, 3)))
    assert fixed.source == "config"
    assert fixed.entries == auto.entries
    # trang chỉ định sai → không có mục, có cảnh báo (không đoán mò)
    wrong = extract_toc(book.pdf_path, book_id="book01", cfg=TocCfg(pages=(5, 5)))
    assert wrong.entries == []
    assert any("không có dòng nào" in w for w in wrong.warnings)


def test_03b_config_pages_validated() -> None:
    with pytest.raises(ValueError, match="1 ≤ a ≤ b"):
        TocCfg(pages=(5, 3))


# ---------------------------------------------------------------- #4-7 không dựa sách mẫu


def test_04_wrapped_title_is_joined() -> None:
    lines = [
        mk("MỤC LỤC", 60, 170, size=14),
        mk("Viêm phổi mắc phải ở cộng đồng do", 100, 62),
        mk("phế cầu khuẩn ........................ 42", 114, 72),  # dòng 2, sát dòng 1
        mk("Hen phế quản .......................... 57", 130, 62),
    ]
    entries, _ = parse_toc(lines, [3])
    assert [(e.title, e.printed_page) for e in entries] == [
        ("Viêm phổi mắc phải ở cộng đồng do phế cầu khuẩn", 42),
        ("Hen phế quản", 57),
    ]
    assert entries[0].line_id == lines[1].id  # truy vết về dòng ĐẦU
    assert entries[0].x0 == 62  # thụt lề theo dòng đầu


def test_04b_toc_title_and_distant_lines_not_joined() -> None:
    lines = [
        mk("MỤC LỤC", 86, 170, size=14),
        mk("Chương 1. Hô hấp .............. 1", 100, 48),  # ngay sau "MỤC LỤC"
        mk("PHẦN PHỤ LỤC", 140, 48),  # không có số trang, cách xa dòng sau
        mk("Bảng tra cứu ................. 90", 170, 48),
    ]
    entries, _ = parse_toc(lines, [3])
    assert [e.title for e in entries] == ["Chương 1. Hô hấp", "Bảng tra cứu"]


def test_05_multi_page_toc_and_isolated_page() -> None:
    lines = (
        toc_page([("Chương 1. Hô hấp ....... 1", 48), ("Hen phế quản ....... 1", 62)], page=2)
        + toc_page([("Chương 2. Tim mạch ....... 9", 48), ("Tăng huyết áp ....... 9", 62)], page=3)
        + toc_page([("Phụ lục A ........ 90", 48), ("Phụ lục B ........ 95", 48)], page=7)
    )
    assert find_toc_pages(lines, search_pages=15, min_entries=2) == [2, 3]
    assert find_toc_pages(lines, search_pages=1, min_entries=2) == []
    entries, _ = parse_toc(lines, [2, 3])
    assert [(e.title, e.toc_pdf_page) for e in entries] == [
        ("Chương 1. Hô hấp", 2),
        ("Hen phế quản", 2),
        ("Chương 2. Tim mạch", 3),
        ("Tăng huyết áp", 3),
    ]


def test_06_decreasing_page_warns_not_fails() -> None:
    rows = [("Bệnh A ....... 12", 48), ("Bệnh B ....... 9", 48), ("Bệnh C ....... 15", 48)]
    entries, warnings = parse_toc(toc_page(rows), [3])
    assert [e.printed_page for e in entries] == [12, 9, 15]
    assert entries[1].flags == ["page_decreasing"]
    assert len(warnings) == 1 and "12 → 9" in warnings[0]


@pytest.mark.parametrize(
    ("text", "plain", "expected"),
    [
        ("Chương 1. Bệnh cơ xương khớp ....... 1", False, ("Chương 1. Bệnh cơ xương khớp", 1)),
        ("Viêm gan B . . . . . . 12", False, ("Viêm gan B", 12)),
        ("Gout …… 9", False, ("Gout", 9)),
        ("Gout……9", False, ("Gout", 9)),
        ("Hen phế quản 57", False, None),  # không chấm dẫn: chỉ chấp nhận trong trang mục lục
        ("Hen phế quản 57", True, ("Hen phế quản", 57)),
        ("Đái tháo đường type 2 61", True, ("Đái tháo đường type 2", 61)),
        ("2026", True, None),
        ("MỤC LỤC", True, None),
    ],
)
def test_07_leader_variants(text: str, plain: bool, expected: tuple[str, int] | None) -> None:
    assert parse_entry_line(text, allow_plain=plain) == expected


def test_07b_toc_page_without_leaders_needs_config() -> None:
    """Không có chấm dẫn thì không tự tìm được trang (tránh nhận nhầm trang thân bài), nhưng
    chỉ định trang trong cấu hình thì đọc được."""
    rows = [("Chương 1. Hô hấp 1", 48), ("Hen phế quản 1", 62), ("Viêm phổi 4", 62)]
    lines = toc_page(rows) + content_pages(4, 5, offset=3)
    assert build_toc(lines).source == "none"
    result = build_toc(lines, TocCfg(pages=(3, 3)))
    assert [(e.title, e.level, e.pdf_page) for e in result.entries] == [
        ("Chương 1. Hô hấp", "chapter", 4),
        ("Hen phế quản", "disease", 4),
        ("Viêm phổi", "disease", 7),
    ]


def test_level_rules_single_indent_and_conflict() -> None:
    # Một mức thụt lề → chỉ dựa mẫu chữ, không cờ.
    flat, _ = parse_toc(toc_page([("CHƯƠNG I. HÔ HẤP ....... 1", 48), ("Hen ....... 1", 48)]), [3])
    assert [(e.level, e.flags) for e in flat] == [("chapter", []), ("disease", [])]
    # Mẫu "Chương" ở vị trí thụt lề của bệnh → vẫn chapter (bằng chứng mạnh) nhưng gắn cờ.
    rows = [
        ("Phần 1. Nội khoa ....... 1", 48),
        ("Hen ....... 1", 62),
        ("Chương 2. Tim ....... 5", 62),
    ]
    entries, warnings = parse_toc(toc_page(rows), [3])
    assert [(e.level, e.flags) for e in entries] == [
        ("chapter", []),
        ("disease", []),
        ("chapter", ["level_conflict"]),
    ]
    assert len(warnings) == 1


def test_page_mapping_and_out_of_range() -> None:
    rows = [("Bệnh A ....... 1", 48), ("Bệnh B ....... 4", 48), ("Bệnh C ....... 40", 48)]
    result = build_toc(toc_page(rows) + content_pages(4, 5, offset=3))
    assert result.page_offset == 3
    assert [e.pdf_page for e in result.entries] == [4, 7, None]
    assert result.entries[2].flags == ["page_out_of_range"]
    assert any("trang in 40 không có trong sách" in w for w in result.warnings)


# ---------------------------------------------------------------- #8 không có mục lục


def test_08_no_toc(tmp_path: Path) -> None:
    lines = content_pages(1, 4, offset=0)
    result = build_toc(lines)
    assert (result.source, result.entries, result.toc_pages) == ("none", [], [])
    assert "Không tìm thấy mục lục" in result.warnings[0]

    pdf = tmp_path / "no_toc.pdf"
    doc = pymupdf.open()
    for n in range(3):
        page = doc.new_page()
        page.insert_text((72, 100), f"Noi dung trang {n + 1}. Benh A, benh B.", fontsize=11)
    doc.save(pdf)
    doc.close()
    assert extract_toc(pdf, book_id="x").source == "none"


# ---------------------------------------------------------------- #9 đối chứng âm


def _altered(truth: dict, index: int, field: str, value: object) -> dict:
    wrong = json.loads(json.dumps(truth))
    wrong["toc"][index][field] = value
    return wrong


@pytest.mark.parametrize(
    ("field", "value"),
    [("level", "disease"), ("printed_page", 4), ("pdf_page", 7)],
)
def test_09_eval_fails_on_wrong_truth(book: SampleBook, field: str, value: object) -> None:
    result = extract_toc(book.pdf_path, book_id="book01")
    assert all_pass(eval_toc(result, book.truth))
    report = eval_toc(result, _altered(book.truth, 0, field, value))
    assert not all_pass(report)
    assert any(field in p for p in report["G1_toc"]["problems"])


def test_09b_eval_fails_on_wrong_title_missing_or_extra(book: SampleBook) -> None:
    result = extract_toc(book.pdf_path, book_id="book01")
    wrong = json.loads(json.dumps(book.truth))
    toc_lines = [ln for ln in wrong["lines"] if ln["role"] == "toc"]
    toc_lines[1]["ocr"] = toc_lines[1]["ocr"].replace("Viêm", "Viem", 1)
    assert not all_pass(eval_toc(result, wrong))

    missing = result.model_copy(update={"entries": result.entries[:-1]})
    assert "thiếu mục #5" in str(eval_toc(missing, book.truth)["G1_toc"]["problems"])
    extra = result.model_copy(update={"entries": [*result.entries, result.entries[0]]})
    assert not all_pass(eval_toc(extra, book.truth))
    empty = result.model_copy(update={"entries": [], "toc_pages": []})
    assert not all_pass(eval_toc(empty, book.truth))  # không được "đạt" im lặng
    wrong_page = result.model_copy(update={"toc_pages": [2, 3]})
    assert "trang mục lục [2, 3] ≠ [3]" in eval_toc(wrong_page, book.truth)["G1_toc"]["problems"]


# ---------------------------------------------------------------- CLI


def test_cli_toc(tmp_path: Path, book: SampleBook) -> None:
    copy_configs(tmp_path)
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    root = ["--root", str(tmp_path)]

    missing = runner.invoke(app, ["p2", "toc", *root])
    assert missing.exit_code == 1 and "Không có file sách" in missing.output

    raw = tmp_path / "data" / "books" / "book01" / "raw"
    raw.mkdir(parents=True)
    shutil.copy(book.pdf_path, raw / "book01.pdf")
    shutil.copy(book.truth_path, raw / "book01.truth.json")
    ok = runner.invoke(app, ["p2", "toc", *root, "--eval"])
    assert ok.exit_code == 0, ok.output
    assert "5 mục" in ok.output and "✓ G1_toc" in ok.output
    saved = json.loads(
        (tmp_path / "data" / "books" / "book01" / "p2_tree" / "toc.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(saved["entries"]) == 5

    bad_truth = tmp_path / "bad.truth.json"
    bad_truth.write_text(
        json.dumps(_altered(book.truth, 2, "printed_page", 9), ensure_ascii=False),
        encoding="utf-8",
    )
    bad = runner.invoke(app, ["p2", "toc", *root, "--eval", "--truth", str(bad_truth)])
    assert bad.exit_code == 1 and "✗ G1_toc" in bad.output
