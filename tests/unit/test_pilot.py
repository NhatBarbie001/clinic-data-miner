"""P0.6 - Kiểm tra chương mẫu (pilot). Mục 4 của docs/phases/P0/P0.6_plan.md."""

import shutil
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from dataminer.cli import app
from dataminer.core.config import PilotCfg
from dataminer.core.io import write_json
from dataminer.ingest.pilot import check_pilot, format_pilot_report, name_key
from dataminer.ingest.survey import survey_pdf
from tests.conftest import SampleBookFor
from tests.unit.llm_fakes import make_settings

runner = CliRunner()
DISEASES = ["Viêm khớp dạng thấp", "Thoái hóa khớp gối", "Viêm loét dạ dày tá tràng"]


def cand(page: int, text: str, level: str = "disease_or_title") -> dict[str, Any]:
    return {
        "page": page,
        "index": 0,
        "text": text,
        "size": 13.5,
        "level_guess": level,
        "reasons": ["viết hoa toàn bộ"],
    }


@pytest.fixture
def survey_dir(tmp_path: Path) -> Path:
    """Kết quả khảo sát dựng tay - giống sách mẫu: 9 trang, trang 2 trắng."""
    out = tmp_path / "survey"
    write_json(out / "stats.json", {"pages": 9, "pages_without_text": [2]})
    write_json(
        out / "heading_candidates.json",
        {
            "candidates": [
                cand(1, "BỆNH HỌC NỘI KHOA"),
                cand(4, "CHƯƠNG 1. BỆNH CƠ XƯƠNG KHỚP", "chapter"),
                cand(4, "VIÊM KHỚP DẠNG THẤP"),
                cand(4, "1. ĐẠI CƯƠNG", "section"),
                cand(6, "THOÁI HÓA KHỚP GỐI"),
                cand(8, "VIÊM LOÉT DẠ DÀY TÁ TRÀNG"),
            ],
            "toc_entries": [],
        },
    )
    return out


def pilot(
    start: int | None = 4, end: int | None = 9, diseases: list[str] | None = None
) -> PilotCfg:
    return PilotCfg(
        page_start=start, page_end=end, diseases=DISEASES if diseases is None else diseases
    )


def test_valid_pilot(survey_dir: Path) -> None:
    report = check_pilot(pilot(), survey_dir)
    assert report.ok, report.errors
    assert report.found == dict(zip(DISEASES, [4, 6, 8], strict=True))
    assert report.warnings == []
    assert "pilot HỢP LỆ" in format_pilot_report(report)


def test_name_matching_tolerates_lost_diacritics(survey_dir: Path) -> None:
    write_json(
        survey_dir / "heading_candidates.json",
        {"candidates": [cand(4, "VIEM KHOP DANG THAP")], "toc_entries": []},
    )
    report = check_pilot(pilot(diseases=["Viêm khớp dạng thấp"]), survey_dir)
    assert report.found == {"Viêm khớp dạng thấp": 4}


def test_name_key() -> None:
    assert name_key("VIÊM  KHỚP dạng THẤP") == name_key("viem khop dang thap")
    assert name_key("Viêm khớp") != name_key("Viêm gan")


def test_unknown_disease(survey_dir: Path) -> None:
    report = check_pilot(pilot(diseases=[*DISEASES, "Hen phế quản"]), survey_dir)
    assert not report.ok
    assert any("Không tìm thấy tiêu đề bệnh 'Hen phế quản'" in e for e in report.errors)


def test_disease_outside_range(survey_dir: Path) -> None:
    report = check_pilot(pilot(start=4, end=5), survey_dir)
    assert not report.ok
    assert any(
        "'Thoái hóa khớp gối' nằm NGOÀI phạm vi 4-5: tiêu đề ở trang [6]" in e
        for e in report.errors
    )
    assert report.found == {"Viêm khớp dạng thấp": 4}


def test_range_beyond_pdf(survey_dir: Path) -> None:
    report = check_pilot(pilot(end=12), survey_dir)
    assert report.errors == ["Phạm vi trang 4-12 vượt quá số trang PDF (9)."]


def test_blank_page_in_range(survey_dir: Path) -> None:
    report = check_pilot(pilot(start=1), survey_dir)
    assert any("Trang không có lớp text nằm trong pilot: [2]" in e for e in report.errors)


def test_warns_on_disease_missing_from_pilot(survey_dir: Path) -> None:
    report = check_pilot(pilot(diseases=DISEASES[:2]), survey_dir)
    assert report.ok  # chỉ là cảnh báo
    assert report.warnings == [
        "Trang 8 có tiêu đề cấp bệnh 'VIÊM LOÉT DẠ DÀY TÁ TRÀNG' không nằm trong pilot.diseases."
    ]


def test_not_configured(survey_dir: Path) -> None:
    for cfg in (pilot(start=None, end=None), pilot(diseases=[])):
        report = check_pilot(cfg, survey_dir)
        assert not report.ok
        assert "Chưa khai báo pilot" in report.errors[0]


def test_survey_missing(tmp_path: Path) -> None:
    report = check_pilot(pilot(), tmp_path / "chua_co")
    assert "chạy `dm survey` trước" in report.errors[0]


def test_on_real_sample_book_and_cli(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    """Đầu-cuối: sách mẫu thật → khảo sát → `dm pilot check` với cấu hình thật trong configs/."""
    make_settings(tmp_path)
    book = sample_book_for(7)
    (tmp_path / "data" / "raw").mkdir(parents=True)
    shutil.copy(book.pdf_path, tmp_path / "data" / "raw" / "book01.pdf")
    survey_pdf(tmp_path / "data/raw/book01.pdf", tmp_path / "data" / "p0_survey")
    ok = runner.invoke(app, ["pilot", "check", "--root", str(tmp_path)])
    assert ok.exit_code == 0, ok.output
    assert "Viêm loét dạ dày tá tràng: tiêu đề ở trang 8" in ok.output

    (tmp_path / "configs/local.yaml").write_text("pilot:\n  page_end: 5\n", encoding="utf-8")
    bad = runner.invoke(app, ["pilot", "check", "--root", str(tmp_path)])
    assert bad.exit_code == 1
    assert "NGOÀI phạm vi" in bad.output
