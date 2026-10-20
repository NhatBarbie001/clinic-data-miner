"""Đánh giá P1 so với đáp án sách mẫu (`*.truth.json`). Mỗi task P1 thêm phần của mình.

Chỉ tiêu gate xem docs/phases/P1/plan.md mục 8.
"""

from typing import Any

from dataminer.core.text_vi import nfc
from dataminer.ingest.page_furniture import FurnitureResult


def _norm(text: str) -> str:
    return " ".join(nfc(text).split())


def eval_furniture(result: FurnitureResult, truth: dict[str, Any]) -> dict[str, Any]:
    """G1 (header/footer bỏ đủ, không bỏ nhầm) và G2 (số trang in) trên các trang đã xử lý."""
    scope = {p.page for p in result.pages}
    truth_hf = {
        (ln["pdf_page"], _norm(ln["ocr"]))
        for ln in truth["lines"]
        if ln["role"] in ("header", "footer") and ln["pdf_page"] in scope
    }
    removed = {(item.page, _norm(item.text)) for item in result.removed}
    missed = sorted(truth_hf - removed)
    wrongly_removed = sorted(removed - truth_hf)

    printed_truth = {
        p["pdf_page"]: p["printed_page"] for p in truth["pages"] if p["pdf_page"] in scope
    }
    printed_got = {p.page: p.printed_page for p in result.pages}
    wrong_pages = sorted(p for p in printed_truth if printed_got.get(p) != printed_truth[p])
    return {
        "G1_furniture": {
            "truth": len(truth_hf),
            "removed": len(removed),
            "missed": missed,
            "wrongly_removed": wrongly_removed,
            "pass": not missed and not wrongly_removed,
        },
        "G2_printed_pages": {
            "pages": len(printed_truth),
            "wrong": [(p, printed_got.get(p), printed_truth[p]) for p in wrong_pages],
            "pass": not wrong_pages,
        },
    }


def format_eval(report: dict[str, Any]) -> str:
    lines = []
    for key, item in report.items():
        mark = "✓" if item.get("pass") else "✗"
        detail = ", ".join(
            f"{k}={v}" for k, v in item.items() if k != "pass" and not isinstance(v, list)
        )
        lines.append(f"{mark} {key}: {detail}")
        for k, v in item.items():
            if isinstance(v, list) and v:
                lines.extend(f"    {k}: {x}" for x in v)
    return "\n".join(lines)
