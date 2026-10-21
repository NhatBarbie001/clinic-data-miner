"""Đánh giá P1 so với đáp án sách mẫu (`*.truth.json`). Mỗi task P1 thêm phần của mình.

Chỉ tiêu gate xem docs/phases/P1/plan.md mục 8.
"""

import difflib
import re
from collections import Counter
from typing import Any

from dataminer.core.text_vi import is_nfc, nfc
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


def _line_key_map(lines: list[Any]) -> dict[str, tuple[int, str, int]]:
    seen: dict[tuple[int, str], int] = {}
    key_of: dict[str, tuple[int, str, int]] = {}
    for ln in lines:
        text = _norm(ln.text)
        occ = seen.get((ln.page, text), 0)
        seen[(ln.page, text)] = occ + 1
        key_of[ln.id] = (ln.page, text, occ)
    return key_of


def _expected_tokens(
    block: Any,
    clean_of: dict[tuple[int, str, int], str],
    key_of: dict[str, tuple[int, str, int]],
    truth_rows: dict[int, list[list[str]]],
) -> list[str] | None:
    """Token văn bản SẠCH (đáp án) tương ứng với block; None nếu không đối chiếu được."""
    from dataminer.ingest.blocks import join_text  # tránh vòng import ở mức module

    if block.kind == "table":
        grid = truth_rows.get(block.page_start)
        return [t for row in grid for cell in row for t in cell.split()] if grid else None
    parts = [clean_of.get(key_of.get(lid, (0, "", 0))) for lid in block.line_ids]
    if any(p is None for p in parts):
        return None
    text = parts[0] or ""
    for part in parts[1:]:
        text = join_text(text, part or "")
    if block.marker and text.startswith(block.marker):
        text = text[len(block.marker) :].strip()
    return _norm(text).split()


def _block_tokens(block: Any, field: str) -> list[str]:
    if block.kind == "table":
        rows = block.rows or []
        if field == "text_rules":  # rows hiện tại là bản đã sửa; bản gốc nằm trong text_rules
            rows = [r.split(" | ") for r in block.text_rules.split("\n")]
        return [t for row in rows for cell in row for t in cell.split()]
    return _norm(getattr(block, field)).split()


def _edits(ref: list[str], hyp: list[str]) -> tuple[int, set[int]]:
    """(số lỗi kiểu WER, vị trí token đáp án được khớp đúng)."""
    ops = difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_opcodes()
    errors = 0
    matched: set[int] = set()
    for tag, i1, i2, j1, j2 in ops:
        if tag == "equal":
            matched.update(range(i1, i2))
        else:
            errors += max(i2 - i1, j2 - j1)
    return errors, matched


def _count_token(text: str, token: str) -> int:
    toks = [t.strip(".,;:!?()[]\"'“”") for t in _norm(text).split()]
    target = _norm(token).split()
    if len(target) == 1:
        return toks.count(target[0].strip(".,;:!?()[]\"'“”"))
    return _norm(text).count(_norm(token))


RE_NUMBER = re.compile(r"\d[\d.,/%×x–\-]*")


def _is_number(token: str) -> bool:
    """Token SỐ LIỆU: 500, 7,5-15, 6/10, 70%, 14 - không tính chữ bị nhận nhầm như "1à"."""
    return RE_NUMBER.fullmatch(token.strip(".,;:!?()[]\"'“”")) is not None


def eval_ocr(blocks: list[Any], lines: list[Any], truth: dict[str, Any]) -> dict[str, Any]:
    """G5 (WER sau ≤ 1%), G6 (≥ 80% lỗi đã cài được sửa), G7 (lỗi tạo thêm ≤ 0.3%),
    G8 (số liệu không đổi, lỗi liều được gắn cờ), G9 (NFC). `lines`: Line nội dung (P1.2)."""
    pages = {ln.page for ln in lines}
    tlines = _truth_keys(truth, pages)
    clean_raw = {
        (ln["pdf_page"], _norm(ln["ocr"])): ln["text"]
        for ln in truth["lines"]
        if ln["pdf_page"] in pages
    }
    clean_of = {t["key"]: clean_raw[(t["key"][0], t["key"][1])] for t in tlines}
    key_of = _line_key_map(lines)
    truth_rows: dict[int, list[list[str]]] = {}
    for tbl in truth.get("tables", []):
        if tbl["pdf_page"] in pages:
            truth_rows[tbl["pdf_page"]] = tbl["rows"]

    words = before_err = after_err = introduced = 0
    unaligned: list[str] = []
    number_changes: list[str] = []
    for block in blocks:
        expected = _expected_tokens(block, clean_of, key_of, truth_rows)
        if expected is None:
            unaligned.append(block.id)
            continue
        before = _block_tokens(block, "text_rules")
        after = _block_tokens(block, "text")
        e_before, ok_before = _edits(expected, before)
        e_after, ok_after = _edits(expected, after)
        words += len(expected)
        before_err += e_before
        after_err += e_after
        introduced += len(ok_before - ok_after)
        num_before = sorted(t for t in before if _is_number(t))
        num_after = sorted(t for t in after if _is_number(t))
        # Thay đổi số liệu chỉ hợp lệ khi đi qua NGƯỜI DUYỆT (Fix rule="review", P1.5)
        reviewed = Counter(f.after for f in block.fixes if f.rule == "review")
        unexplained = Counter(num_after) - Counter(num_before) - reviewed
        if unexplained or Counter(num_before) - Counter(num_after) - Counter(
            f.before for f in block.fixes if f.rule == "review"
        ):
            number_changes.append(f"{block.id}: {num_before} → {num_after}")

    # lỗi đã cài: tìm block chứa dòng lỗi, so số lần xuất hiện bản lỗi/bản đúng trước và sau
    block_of_key = {key_of[lid]: b for b in blocks for lid in b.line_ids if lid in key_of}
    key_by_clean = {(t["key"][0], _norm(clean_of[t["key"]])): t["key"] for t in tlines}
    per_kind: dict[str, list[int]] = {}
    dose: list[dict[str, Any]] = []
    unfixed: list[str] = []
    unmatched_errors: list[str] = []
    miscorrected: list[str] = []
    for err in truth["ocr_errors"]:
        if err["pdf_page"] not in pages:
            continue
        key = key_by_clean.get((err["pdf_page"], _norm(err["line_clean"])))
        block = block_of_key.get(key) if key else None
        if block is None:  # KHÔNG bỏ qua im lặng: đối chiếu hỏng → chỉ tiêu không đạt
            unmatched_errors.append(f"tr.{err['pdf_page']} {err['kind']}: {err['corrupted']}")
            continue
        stats = per_kind.setdefault(err["kind"], [0, 0])
        stats[1] += 1
        if err["kind"] == "nfd_line":
            stats[0] += all(is_nfc(t) for t in _block_tokens(block, "text"))
            continue
        if err["kind"] == "digit_confusion":
            bad = err["corrupted"].replace(err["original"], "").strip() or err["corrupted"]
            bad_tok = next(
                (t for t in err["corrupted"].split() if t not in err["original"].split()), bad
            )
            still = _count_token(block.text, bad_tok) > 0
            flagged = "dose_suspect" in block.flags
            good_tok = err["original"].split()[err["corrupted"].split().index(bad_tok)]
            by_review = any(
                f.rule == "review" and f.before == bad_tok and f.after == good_tok
                for f in block.fixes
            )
            dose.append(
                {
                    "error": f"{err['original']} → {err['corrupted']}",
                    "kept": still,
                    "flagged": flagged,
                    "fixed_by_review": by_review,
                }
            )
            # đạt khi: chưa duyệt → giữ nguyên + gắn cờ; đã duyệt → sửa đúng qua người duyệt
            stats[0] += (still and flagged) or by_review
            continue
        fewer_bad = _count_token(block.text, err["corrupted"]) < _count_token(
            block.text_rules, err["corrupted"]
        )
        more_good = _count_token(block.text, err["original"]) > _count_token(
            block.text_rules, err["original"]
        )
        stats[0] += fewer_bad and more_good
        if not (fewer_bad and more_good):
            label = f"tr.{err['pdf_page']} {err['kind']}: {err['original']} → {err['corrupted']}"
            unfixed.append(label)
            if fewer_bad:  # bản lỗi đã bị đổi nhưng KHÔNG thành bản đúng → sửa sai
                miscorrected.append(label)

    fixable = {k: v for k, v in per_kind.items() if k not in ("digit_confusion", "nfd_line")}
    fixed = sum(v[0] for v in fixable.values())
    total = sum(v[1] for v in fixable.values())
    wer_b = round(before_err / words, 4) if words else 0.0
    wer_a = round(after_err / words, 4) if words else 0.0
    not_nfc = [b.id for b in blocks if not is_nfc(b.text)]
    return {
        "G5_wer": {
            "words": words,
            "before": wer_b,
            "after": wer_a,
            "target": 0.01,
            "unaligned_blocks": unaligned,
            "pass": wer_a <= 0.01 and not unaligned,
        },
        "G6_errors_fixed": {
            "fixed": fixed,
            "total": total,
            "rate": round(fixed / total, 4) if total else 1.0,
            "by_kind": {k: f"{v[0]}/{v[1]}" for k, v in sorted(per_kind.items())},
            "unfixed": unfixed,
            "miscorrected": miscorrected,  # đổi bản lỗi thành một từ sai khác (vd. dien → diễn)
            "unmatched_errors": unmatched_errors,
            "target": 0.8,
            "pass": not unmatched_errors and (total == 0 or fixed / total >= 0.8),
        },
        "G7_introduced": {
            "tokens": introduced,
            "rate": round(introduced / words, 4) if words else 0.0,
            "target": 0.003,
            "pass": words == 0 or introduced / words <= 0.003,
        },
        "G8_numbers": {
            "number_changes": number_changes,
            "dose_errors": dose,
            "pass": not number_changes
            and all((d["kept"] and d["flagged"]) or d["fixed_by_review"] for d in dose),
        },
        "G9_nfc": {"not_nfc": not_nfc, "pass": not not_nfc},
    }


def evaluate_p1(out_dir: Any, truth: dict[str, Any]) -> dict[str, Any]:
    """Đánh giá trọn P1 từ các file trong `data/p1_clean/` (G1-G9)."""
    from pathlib import Path

    from dataminer.core.io import read_json, read_jsonl
    from dataminer.ingest.blocks import Block
    from dataminer.ingest.page_furniture import FurnitureItem, PageInfo
    from dataminer.ingest.pdf_reader import Line

    out = Path(out_dir)
    content = list(read_jsonl(out / "content_lines.jsonl", Line))
    furn = read_json(out / "furniture.json")
    furniture = FurnitureResult(
        content=content,
        removed=[FurnitureItem.model_validate(x) for x in furn["removed"]],
        pages=[PageInfo.model_validate(x) for x in furn["pages"]],
        warnings=furn.get("warnings", []),
    )
    rules = list(read_jsonl(out / "blocks_rules.jsonl", Block))
    final = list(read_jsonl(out / "blocks.jsonl", Block))
    report: dict[str, Any] = {}
    report.update(eval_furniture(furniture, truth))
    report.update(eval_blocks(rules, content, truth))
    report.update(eval_ocr(final, content, truth))
    return report


def all_pass(report: dict[str, Any]) -> bool:
    return all(item.get("pass") for item in report.values())
