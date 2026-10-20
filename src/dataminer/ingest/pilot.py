"""P0.6 - Kiểm tra chương mẫu (pilot) bằng kết quả khảo sát (P0.5).

Pilot = phạm vi trang PDF + danh sách bệnh mà mọi phase chạy trước khi chạy toàn sách.
Kiểm tra rằng cấu hình pilot khớp với sách thật sự: trang tồn tại, có text, và mỗi bệnh
có tiêu đề nằm TRONG phạm vi trang.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dataminer.core.config import PilotCfg
from dataminer.core.io import DataFileError, read_json
from dataminer.core.text_vi import nfc, strip_diacritics


def name_key(text: str) -> str:
    """Khóa so khớp tên bệnh chịu được lỗi OCR mất/sai dấu: bỏ dấu, chữ thường, gộp khoảng trắng."""
    return " ".join(strip_diacritics(nfc(text)).casefold().split())


@dataclass
class PilotReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    found: dict[str, int] = field(default_factory=dict)  # tên bệnh → trang PDF của tiêu đề
    page_range: tuple[int, int] | None = None

    @property
    def ok(self) -> bool:
        return not self.errors


def check_pilot(pilot: PilotCfg, survey_dir: Path) -> PilotReport:
    report = PilotReport()
    if pilot.page_start is None or pilot.page_end is None or not pilot.diseases:
        report.errors.append(
            "Chưa khai báo pilot: cần pilot.page_start, pilot.page_end (số trang PDF) và "
            "pilot.diseases trong configs/default.yaml (hoặc local.yaml)."
        )
        return report
    start, end = pilot.page_start, pilot.page_end
    report.page_range = (start, end)

    try:
        stats: dict[str, Any] = read_json(survey_dir / "stats.json")
        headings: dict[str, Any] = read_json(survey_dir / "heading_candidates.json")
    except DataFileError:
        report.errors.append(
            f"Chưa có kết quả khảo sát trong {survey_dir} - chạy `dm survey` trước."
        )
        return report

    n_pages = int(stats["pages"])
    if end > n_pages:
        report.errors.append(f"Phạm vi trang {start}-{end} vượt quá số trang PDF ({n_pages}).")
        return report
    blank = [p for p in stats["pages_without_text"] if start <= p <= end]
    if blank:
        report.errors.append(f"Trang không có lớp text nằm trong pilot: {blank}.")

    pages_by_key: dict[str, list[int]] = defaultdict(list)
    for cand in headings["candidates"]:
        pages_by_key[name_key(cand["text"])].append(int(cand["page"]))

    wanted = {name_key(d) for d in pilot.diseases}
    for disease in pilot.diseases:
        pages = sorted(set(pages_by_key.get(name_key(disease), [])))
        inside = [p for p in pages if start <= p <= end]
        if inside:
            report.found[disease] = inside[0]
        elif pages:
            report.errors.append(
                f"Bệnh '{disease}' nằm NGOÀI phạm vi {start}-{end}: tiêu đề ở trang {pages}."
            )
        else:
            report.errors.append(
                f"Không tìm thấy tiêu đề bệnh '{disease}' (kiểm tra chính tả, hoặc tiêu đề bị lỗi "
                "OCR nặng - xem data/p0_survey/heading_candidates.json)."
            )

    for cand in headings["candidates"]:
        page = int(cand["page"])
        if (
            start <= page <= end
            and cand["level_guess"] == "disease_or_title"
            and name_key(cand["text"]) not in wanted
        ):
            report.warnings.append(
                f"Trang {page} có tiêu đề cấp bệnh '{cand['text']}' không nằm trong pilot.diseases."
            )
    return report


def format_pilot_report(report: PilotReport) -> str:
    lines = []
    if report.page_range:
        start, end = report.page_range
        lines.append(f"Pilot: trang PDF {start}-{end}")
    for disease, page in report.found.items():
        lines.append(f"  ✓ {disease}: tiêu đề ở trang {page}")
    lines += [f"  ✗ {e}" for e in report.errors]
    lines += [f"  ⚠ {w}" for w in report.warnings]
    lines.append("KẾT LUẬN: " + ("pilot HỢP LỆ" if report.ok else "pilot KHÔNG hợp lệ"))
    return "\n".join(lines)
