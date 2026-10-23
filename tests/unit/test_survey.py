"""P0.5b - Khảo sát PDF: đối chiếu với đáp án sách mẫu + unit test từng bộ phát hiện."""

import json
import unicodedata
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dataminer.cli import app
from dataminer.core.io import read_json
from dataminer.devtools.survey_check import check_survey
from dataminer.survey.survey import (
    SurveyLine,
    find_header_footer,
    find_heading_candidates,
    find_ocr_signals,
    survey_pdf,
)
from tests.conftest import SampleBookFor
from tests.unit.llm_fakes import make_settings

runner = CliRunner()


def line(
    text: str, *, page: int = 5, size: float = 10.5, zone: str = "body", index: int = 0
) -> SurveyLine:
    return SurveyLine(
        id=f"l{page}_{index}",
        page=page,
        index=index,
        text=text,
        bbox=(48, 100, 300, 112),
        size=size,
        font="Noto Sans Regular",
        bold=False,
        zone=zone,
    )  # type: ignore[arg-type]


# ---------------------------------------------------------------- so với đáp án


@pytest.mark.parametrize("seed", [7, 2, 6])
def test_survey_meets_all_targets_vs_truth(
    tmp_path: Path, sample_book_for: SampleBookFor, seed: int
) -> None:
    """Chỉ tiêu ở P0.5_plan mục 4 - chạy với nhiều seed để tránh khớp quá mức một sách."""
    book = sample_book_for(seed)
    result = survey_pdf(book.pdf_path, tmp_path / "survey")
    checks = check_survey(result, book.truth)
    failed = [k for k, v in checks.items() if isinstance(v, dict) and v.get("pass") is False]
    failed += [k for k, v in checks["ocr_errors"].items() if not v["pass"]]
    assert checks["all_pass"], failed


def test_survey_outputs_written(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    book = sample_book_for(7)
    out = tmp_path / "survey"
    result = survey_pdf(book.pdf_path, out, book_id="book01")
    for name in (
        "stats.json",
        "lines.jsonl",
        "header_footer.json",
        "heading_candidates.json",
        "ocr_signals.json",
        "survey_report.md",
    ):
        assert (out / name).is_file(), name
    assert set(result.sample_pages) == {"muc_luc", "dau_chuong", "co_bang", "nhieu_loi_ocr"}
    assert result.sample_pages["muc_luc"] == 3
    assert result.sample_pages["co_bang"] == 9  # trang có bảng phác đồ
    for page in result.sample_pages.values():
        assert (out / "pages" / f"page_{page:03d}.json").is_file()
        assert (out / "pages" / f"page_{page:03d}.png").is_file()
    stats = read_json(out / "stats.json")
    assert stats["bold_char_ratio"] == 0  # lớp OCR không giữ in đậm
    assert "không giữ thông tin in đậm" in (out / "survey_report.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------- header/footer


def test_header_footer_repeated_and_page_numbers() -> None:
    lines = [
        line("– 1 –", page=4, zone="bottom", size=9),
        line("– 2 –", page=5, zone="bottom", size=9),
        line("Bệnh học nội khoa", page=5, zone="top", size=8.5),
        line("Bệnh học nội khoa", page=7, zone="top", size=8.5),
        line("Chương 1. Một mình", page=6, zone="top", size=8.5),  # 1 lần nhưng chữ nhỏ
        line("Nội dung thân bài cỡ thường", page=6, zone="top", size=10.5),  # không phải header
    ]
    hf = find_header_footer(lines, body_size=10.5)
    found = {(i["page"], i["text"]): i for i in hf["instances"]}
    assert found[(4, "– 1 –")]["printed_page"] == 1
    assert found[(5, "Bệnh học nội khoa")]["confidence"] == "high"
    assert found[(6, "Chương 1. Một mình")]["confidence"] == "medium"
    assert (6, "Nội dung thân bài cỡ thường") not in found


# ---------------------------------------------------------------- tiêu đề


@pytest.mark.parametrize(
    ("text", "size", "level"),
    [
        ("CHƯƠNG 3. BỆNH HÔ HẤP", 14.0, "chapter"),
        ("HEN PHẾ QUẢN", 13.0, "disease_or_title"),
        ("2. NGUYÊN NHÂN", 10.6, "section"),  # cỡ chữ gần thân bài: dựa vào đánh số + in hoa
        ("3.1. Lâm sàng", 10.5, "subsection"),  # cùng cỡ, không in hoa: chỉ còn đánh số
    ],
)
def test_heading_detection(text: str, size: float, level: str) -> None:
    (cand,) = find_heading_candidates([line(text, size=size)], body_size=10.5)["candidates"]
    assert cand["level_guess"] == level
    assert cand["reasons"]


@pytest.mark.parametrize(
    "text",
    [
        "- Paracetamol 500 mg mỗi lần, không quá 3 g mỗi ngày.",
        "50 tuổi và là nguyên nhân hàng đầu gây đau khớp gối.",
        "Bảng 2.1. Phác đồ diệt Helicobacter pylori 3 thuốc",
        "2 lần mỗi ngày.",
    ],
)
def test_body_lines_not_headings(text: str) -> None:
    assert find_heading_candidates([line(text)], body_size=10.5)["candidates"] == []


def test_toc_lines_separated() -> None:
    res = find_heading_candidates(
        [line("Chương 1. Bệnh cơ xương khớp ................ 1", size=10.5)], body_size=10.5
    )
    assert res["candidates"] == []
    assert len(res["toc_entries"]) == 1


# ---------------------------------------------------------------- dấu hiệu lỗi OCR


@pytest.mark.parametrize(
    ("text", "kind", "token"),
    [
        ("- Paracetamol 5OO mg mỗi lần", "digit_lookalike", "5OO"),
        ("Amoxicilin l g 2 lần", "digit_lookalike", "l g"),
        ("cho 1à kết quả", "digit_in_word", "1à"),
        ("tình trạng viêrn màng hoạt dịch", "invalid_syllable", "viêrn"),
        ("kèm theo phảnứng của xương", "invalid_syllable", "phảnứng"),
        ("trong 14 ngày(Bảng 2.1).", "missing_space", "ngày(Bảng"),
    ],
)
def test_ocr_signal_detected(text: str, kind: str, token: str) -> None:
    signals = find_ocr_signals([line(text)])
    assert any(s["kind"] == kind and s["token"] == token for s in signals), signals


def test_nfd_line_detected() -> None:
    signals = find_ocr_signals([line(unicodedata.normalize("NFD", "Khớp sưng, đau, nóng"))])
    assert [s["kind"] for s in signals] == ["nfd_line"]


@pytest.mark.parametrize(
    "text",
    [
        "người mang kháng nguyên HLA-DR4 có nguy cơ cao hơn.",
        "kháng thể anti-CCP có độ đặc hiệu cao.",
        "methotrexat 7,5-15 mg mỗi tuần, kết hợp acid folic.",
        "Số lần/ngày",
        "protein phản ứng C (CRP) tăng.",
        "tiêu chuẩn ACR/EULAR 2010: đạt từ 6/10 điểm.",
        "– 12 –",
    ],
)
def test_no_false_alarm_on_clean_text(text: str) -> None:
    assert find_ocr_signals([line(text)]) == []


# ---------------------------------------------------------------- CLI


def test_cli_sample_book_survey_check(tmp_path: Path) -> None:
    make_settings(tmp_path)
    root = ["--root", str(tmp_path)]
    made = runner.invoke(app, ["dev", "make-sample-book", *root])
    assert made.exit_code == 0, made.output
    assert (tmp_path / "data/books/book01/raw/book01.pdf").is_file()

    surveyed = runner.invoke(app, ["survey", *root])
    assert surveyed.exit_code == 0, surveyed.output
    manifest = read_json(tmp_path / "data/books/book01/p0_survey/manifest.json")
    assert manifest["status"] == "success"
    assert manifest["inputs"][0]["path"] == "data/books/book01/raw/book01.pdf"
    assert manifest["counts"]["pages"] == 9

    checked = runner.invoke(app, ["dev", "check-survey", *root])
    assert checked.exit_code == 0, checked.output
    assert "ĐẠT mọi chỉ tiêu" in checked.output
    assert (tmp_path / "data/books/book01/p0_survey/survey_vs_truth.txt").is_file()


def test_cli_survey_missing_pdf(tmp_path: Path) -> None:
    make_settings(tmp_path)
    result = runner.invoke(app, ["survey", "--root", str(tmp_path)])
    assert result.exit_code == 1
    assert "make-sample-book" in result.output


def test_check_survey_fails_when_truth_disagrees(
    tmp_path: Path, sample_book_for: SampleBookFor
) -> None:
    """Đối chiếu phải biết nói KHÔNG: sửa đáp án cho sai → không đạt."""
    book = sample_book_for(7)
    result = survey_pdf(book.pdf_path, tmp_path / "survey")
    wrong = json.loads(json.dumps(book.truth))
    wrong["body_size"] = 14.0
    wrong["headings"].append({"pdf_page": 5, "ocr": "TIÊU ĐỀ KHÔNG TỒN TẠI", "level": "disease"})
    checks = check_survey(result, wrong)
    assert not checks["all_pass"]
    assert not checks["body_font_size"]["pass"]
    assert checks["headings"]["missed"] == [(5, "TIÊU ĐỀ KHÔNG TỒN TẠI")]


def test_cli_startup_does_not_load_pymupdf() -> None:
    """Nạp pymupdf mất ~2s - mọi lệnh `dm` (vd. `dm version`) không được phải chịu."""
    import subprocess
    import sys

    code = "import sys, dataminer.cli; print('pymupdf' in sys.modules)"
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "False"
