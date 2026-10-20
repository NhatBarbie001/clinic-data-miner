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


def _truth_keys(truth: dict[str, Any], pages: set[int]) -> list[dict[str, Any]]:
    """Dòng nội dung của đáp án trong `pages`, kèm khóa so khớp (trang, văn bản OCR, lần xuất
    hiện), nhóm block, và số thứ tự mục (tăng sau mỗi tiêu đề) để phát hiện gộp nhầm."""
    seen: dict[tuple[int, str], int] = {}
    section = 0
    out = []
    for i, ln in enumerate(truth["lines"]):
        if ln["pdf_page"] not in pages or ln["role"] in ("header", "footer"):
            continue
        text = _norm(ln["ocr"])
        occ = seen.get((ln["pdf_page"], text), 0)
        seen[(ln["pdf_page"], text)] = occ + 1
        if ln["role"] == "heading":
            section += 1
        if ln.get("block"):
            group = ln["block"]
        elif ln["role"] == "table":
            group = f"table@{ln['pdf_page']}"
        else:  # mục lục, bìa, tiêu đề "MỤC LỤC": mỗi dòng là một block
            group = f"{ln['role']}@{ln['pdf_page']}#{i}"
        out.append(
            {
                "key": (ln["pdf_page"], text, occ),
                "group": group,
                "section": section,
                "role": ln["role"],
                "text": text,
            }
        )
    return out


def eval_blocks(blocks: list[Any], lines: list[Any], truth: dict[str, Any]) -> dict[str, Any]:
    """G3 (block dựng đúng tập dòng, không gộp nhầm qua tiêu đề) và G4 (bảng đúng hàng × cột).

    `blocks`: Block (P1.3); `lines`: các Line nội dung đã dùng để dựng block.
    """
    pages = {ln.page for ln in lines}
    tlines = _truth_keys(truth, pages)
    by_key = {t["key"]: t for t in tlines}
    seen: dict[tuple[int, str], int] = {}
    key_of: dict[str, tuple[int, str, int]] = {}
    for ln in lines:
        text = _norm(ln.text)
        occ = seen.get((ln.page, text), 0)
        seen[(ln.page, text)] = occ + 1
        key_of[ln.id] = (ln.page, text, occ)
    unmatched_lines = [lid for lid, key in key_of.items() if key not in by_key]

    truth_groups: dict[str, set[tuple[int, str, int]]] = {}
    for t in tlines:
        truth_groups.setdefault(t["group"], set()).add(t["key"])
    predicted = [frozenset(key_of[lid] for lid in b.line_ids if lid in key_of) for b in blocks]
    predicted_set = set(predicted)
    wrong = [
        sorted(keys)[0][1][:70]
        for keys in truth_groups.values()
        if frozenset(keys) not in predicted_set
    ]
    merged = [
        b.text[:70]
        for b, keys in zip(blocks, predicted, strict=True)
        if len({by_key[k]["section"] for k in keys if k in by_key}) > 1
    ]
    exact = len(truth_groups) - len(wrong)
    recall = round(exact / len(truth_groups), 4) if truth_groups else 1.0

    # G4: bảng - so ô (bản OCR của đáp án) theo hàng × cột
    tables_truth: dict[int, list[list[str]]] = {}
    for ln in truth["lines"]:
        if ln["role"] == "table" and ln["pdf_page"] in pages:
            grid = tables_truth.setdefault(ln["pdf_page"], [])
            while len(grid) <= ln["row"]:
                grid.append([])
            row = grid[ln["row"]]
            while len(row) <= ln["col"]:
                row.append("")
            row[ln["col"]] = _norm(ln["ocr"])
    tables_got = {
        b.page_start: [[_norm(c) for c in r] for r in b.rows or []]
        for b in blocks
        if b.kind == "table"
    }
    table_errors = [
        f"trang {page}: {tables_got.get(page)} ≠ {grid}"
        for page, grid in tables_truth.items()
        if tables_got.get(page) != grid
    ]
    extra_tables = sorted(set(tables_got) - set(tables_truth))
    return {
        "G3_blocks": {
            "truth_blocks": len(truth_groups),
            "exact": exact,
            "recall": recall,
            "target": 0.97,
            "wrong": wrong,
            "merged_across_headings": merged,
            "unmatched_lines": unmatched_lines,
            "pass": recall >= 0.97 and not merged and not unmatched_lines,
        },
        "G4_tables": {
            "truth_tables": len(tables_truth),
            "found_tables": len(tables_got),
            "errors": table_errors,
            "extra_tables": [f"trang {p}" for p in extra_tables],
            "pass": not table_errors and not extra_tables,
        },
    }
