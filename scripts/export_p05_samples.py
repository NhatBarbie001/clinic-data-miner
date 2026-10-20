"""Xuất dữ liệu mẫu P0.5 (samples/P0.5) và fixture trang (tests/fixtures/pages) từ sách mẫu.

Chạy sau `dm dev make-sample-book` và `dm survey`:
    uv run python scripts/export_p05_samples.py
"""

import json
import shutil
import sys
import unicodedata
from typing import Any

import pymupdf

from dataminer.core.config import get_settings
from dataminer.ingest.survey import _page_detail

# Trang đại diện: mục lục, đầu chương (nhiều lỗi OCR), có lỗi liều thuốc "5OO mg", có bảng.
FIXTURE_PAGES = {3: "muc_luc", 4: "dau_chuong", 7: "loi_lieu_thuoc", 9: "co_bang"}
IMAGE_PAGES = (3, 4, 9)


def text_vs_truth(truth: dict[str, Any]) -> str:
    errors_by_line: dict[tuple[int, str], list[str]] = {}
    for e in truth["ocr_errors"]:
        key = (e["pdf_page"], e["line_clean"])
        label = f"{e['kind']}: `{e['original']}` → `{e['corrupted']}`"
        errors_by_line.setdefault(key, []).append(label)
    out = [
        "# Sách mẫu: văn bản sạch ↔ lớp OCR",
        "",
        "Mỗi dòng có lỗi OCR đã cài được liệt kê; dòng ⚠️ là lỗi số liệu (nguy hiểm nhất).",
        "Header/footer không bị cài lỗi (để P1 nhận ra và bỏ được). Trang 4 in đủ mọi dòng;",
        "các trang khác chỉ in dòng có lỗi.",
        "",
    ]
    for page in truth["pages"]:
        n = page["pdf_page"]
        printed = page["printed_page"]
        out.append(
            f"## Trang PDF {n}" + (f" (trang in {printed})" if printed else " (không đánh số)")
        )
        lines = [ln for ln in truth["lines"] if ln["pdf_page"] == n]
        if not lines:
            out.append("_(trang trắng - không có lớp text)_\n")
            continue
        rows = []
        for ln in lines:
            errs = errors_by_line.get((n, ln["text"]), [])
            if not errs and n != 4:  # trang 4: in đủ mọi dòng; trang khác: chỉ dòng có lỗi
                continue
            ocr = ln["ocr"]
            if not unicodedata.is_normalized("NFC", ocr):
                ocr = unicodedata.normalize("NFC", ocr) + " _(NFD)_"
            flag = "⚠️ " if any(x.startswith("digit") for x in errs) else ""
            rows.append(f"| {ln['role']} | {ln['text']} | {flag}{ocr} | {'<br>'.join(errs)} |")
        if rows:
            out += ["", "| vai trò | văn bản sạch | lớp OCR | lỗi đã cài |", "|---|---|---|---|"]
            out += rows
        else:
            out.append("_(không có lỗi OCR trên trang này)_")
        out.append("")
    return "\n".join(out)


def main() -> int:
    s = get_settings()
    root = s.paths.data_dir.parent
    pdf = s.paths.raw_dir / s.project.book_file
    truth_path = pdf.with_suffix(".truth.json")
    survey = s.paths.data_dir / "p0_survey"
    samples = root / "samples" / "P0.5"
    fixtures = root / "tests" / "fixtures" / "pages"
    samples.mkdir(parents=True, exist_ok=True)
    fixtures.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open(pdf)
    for page_no, label in FIXTURE_PAGES.items():
        detail = {
            "label": label,
            "source": "sách mẫu tổng hợp seed 7 (dm dev make-sample-book)",
            **_page_detail(doc[page_no - 1]),
        }
        (fixtures / f"book01_page_{page_no:03d}.json").write_text(
            json.dumps(detail, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
    for page_no in IMAGE_PAGES:
        pix = doc[page_no - 1].get_pixmap(dpi=80, colorspace=pymupdf.csGRAY)
        (samples / f"book01_page_{page_no:03d}.jpg").write_bytes(pix.tobytes("jpg", jpg_quality=70))

    truth = json.loads(truth_path.read_text(encoding="utf-8"))
    (samples / "book01_text_vs_truth.md").write_text(text_vs_truth(truth), encoding="utf-8")
    shutil.copy(truth_path, samples / "book01.truth.json")
    for name in (
        "survey_report.md",
        "stats.json",
        "header_footer.json",
        "heading_candidates.json",
        "ocr_signals.json",
        "survey_vs_truth.txt",
        "manifest.json",
    ):
        shutil.copy(survey / name, samples / name)
    print(f"✓ samples: {samples}\n✓ fixtures: {fixtures}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
