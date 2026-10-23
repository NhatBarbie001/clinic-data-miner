"""P1.5 - Hàng đợi duyệt tay (nguyên tắc N10): xuất CSV → người duyệt điền → nhập lại.

Những gì máy KHÔNG được tự quyết đi vào hàng đợi:
    1-SỐ LIỆU     số/liều nghi nhận nhầm (cờ dose_suspect) - kèm gợi ý của LLM
    2-BỊ TỪ CHỐI  thay đổi LLM đề xuất nhưng guard chặn; block LLM không trả về (fix_failed)
    3-NGHI LỖI    tín hiệu lỗi OCR còn sót sau khi sửa (ocr_suspect)
Quyết định lưu trong `decisions.jsonl` (theo item_id ổn định) → chạy lại pipeline thì tự áp lại,
người duyệt không phải duyệt lại. Quyết định không còn khớp văn bản → `stale`, quay lại hàng đợi.
Xem docs/phases/P1/P1.5_plan.md.
"""

import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel

from dataminer.core.io import read_jsonl, write_jsonl
from dataminer.core.schemas import BaseRecord, stable_id
from dataminer.core.text_vi import nfc
from dataminer.ingest.survey import text_ocr_signals
from dataminer.model.block import Block, Fix, Review

Priority = Literal["1-SỐ LIỆU", "2-BỊ TỪ CHỐI", "3-NGHI LỖI", "4-KIỂM TRA MẪU"]
DecisionKind = Literal["accept", "keep", "edit"]
RE_NUMBER_VALUE = re.compile(r"\d+(?:[.,]\d+)?(?:[-–]\d+(?:[.,]\d+)?)?%?")
COLUMNS = [
    "item_id",
    "priority",
    "page",
    "printed_page",
    "block_id",
    "kind",
    "cell",
    "position",
    "context",
    "current",
    "suggestion",
    "reason",
    "decision",
    "edited_value",
    "reviewer",
    "comment",
]
WHOLE = -1  # position cho mục cả block (fix_failed / fix_rejected)


class ReviewError(Exception):
    """File duyệt có dòng không hợp lệ (thông điệp liệt kê từng dòng CSV)."""


class ReviewItem(BaseModel):
    item_id: str
    priority: Priority
    page: int
    printed_page: int | None
    block_id: str
    kind: str
    cell: str | None
    position: int  # chỉ số token trong văn bản hiện tại (của ô nếu là bảng); -1 = cả block
    context: str
    current: str
    suggestion: str | None
    reason: str


class Decision(BaseRecord):
    """Quyết định của người duyệt, lưu bền trong decisions.jsonl (id = item_id)."""

    decision: DecisionKind
    value: str  # giá trị cuối cùng dùng thay cho `current` (keep → chính `current`)
    current: str
    block_id: str
    cell: str | None = None
    position: int
    priority: Priority
    reviewer: str = ""
    comment: str = ""
    at: str


# --------------------------------------------------------------------------- dựng hàng đợi


def _cell_text(block: Block, cell: str | None) -> str:
    if cell is None:
        return block.text
    r, c = (int(x) for x in cell[1:].split("c"))
    return (block.rows or [])[r][c]


def _locate(tokens: list[str], token: str, hint: int) -> int | None:
    """Vị trí của `token` trong `tokens`, gần `hint` nhất (văn bản có thể đã đổi số token)."""
    hits = [i for i, t in enumerate(tokens) if t == token]
    return min(hits, key=lambda i: abs(i - hint)) if hits else None


def _context(tokens: list[str], pos: int, width: int = 8) -> str:
    lo, hi = max(0, pos - width), min(len(tokens), pos + width + 1)
    marked = [f"«{t}»" if i == pos else t for i, t in enumerate(tokens[lo:hi], start=lo)]
    return ("… " if lo else "") + " ".join(marked) + (" …" if hi < len(tokens) else "")


def _item(
    block: Block,
    priority: Priority,
    cell: str | None,
    pos: int,
    current: str,
    suggestion: str | None,
    reason: str,
) -> ReviewItem:
    tokens = _cell_text(block, cell).split()
    return ReviewItem(
        item_id=stable_id(block.id, cell or "", pos, current, prefix="rv"),
        priority=priority,
        page=block.page_start,
        printed_page=block.printed_start,
        block_id=block.id,
        kind=block.kind,
        cell=cell,
        position=pos,
        context=_context(tokens, pos) if pos != WHOLE else _cell_text(block, cell),
        current=current,
        suggestion=suggestion,
        reason=reason,
    )


def _rejected_fix_item(block: Block, fix: Fix) -> ReviewItem | None:
    if fix.rule == "G-ratio":
        return _item(
            block,
            "2-BỊ TỪ CHỐI",
            fix.cell,
            WHOLE,
            _cell_text(block, fix.cell),
            fix.after,
            "G-ratio: LLM đổi quá nhiều - cả block giữ nguyên",
        )
    tokens = _cell_text(block, fix.cell).split()
    first = fix.before.split()[0] if fix.before.split() else fix.before
    pos = _locate(tokens, first, fix.position)
    if pos is None:
        return None  # token đã không còn (đã được duyệt / sửa khác) - không cần hỏi
    if len(fix.before.split()) > 1:  # vùng nhiều token (thêm/bớt/tách) → hỏi theo token đầu
        return _item(
            block,
            "2-BỊ TỪ CHỐI",
            fix.cell,
            pos,
            first,
            None,
            f"{fix.rule}: LLM đề xuất `{fix.before}` → `{fix.after}`",
        )
    if fix.suggestion is not None:
        return _item(
            block,
            "1-SỐ LIỆU",
            fix.cell,
            pos,
            fix.before,
            fix.suggestion,
            "số liệu nghi nhận nhầm (OCR) - KHÔNG tự sửa",
        )
    return _item(
        block,
        "2-BỊ TỪ CHỐI",
        fix.cell,
        pos,
        fix.before,
        fix.after,
        f"{fix.rule}: guard chặn đề xuất của LLM",
    )


def build_queue(blocks: list[Block]) -> list[ReviewItem]:
    """Mọi mục cần người quyết định trong `blocks` (đã trừ mục đã được duyệt)."""
    items: dict[str, ReviewItem] = {}
    for block in blocks:
        reviewed = {r.item_id for r in block.reviews}
        # đã duyệt cả block/ô → không hỏi lại mục cả-block (văn bản đã đổi nên item_id cũng đổi)
        whole_done = {r.cell for r in block.reviews if r.position == WHOLE}
        candidates: list[ReviewItem] = []
        for fix in block.fixes:
            if not fix.accepted and fix.rule != "review":
                if fix.rule == "G-ratio" and fix.cell in whole_done:
                    continue
                item = _rejected_fix_item(block, fix)
                if item:
                    candidates.append(item)
        if "fix_failed" in block.flags and None not in whole_done:
            candidates.append(
                _item(
                    block,
                    "2-BỊ TỪ CHỐI",
                    None,
                    WHOLE,
                    block.text,
                    None,
                    "fix_failed: LLM không trả về block này - cần đọc lại",
                )
            )
        if "ocr_suspect" in block.flags:
            texts = (
                [(None, block.text)]
                if block.kind != "table"
                else [
                    (f"r{r}c{c}", cell)
                    for r, row in enumerate(block.rows or [])
                    for c, cell in enumerate(row)
                ]
            )
            for cell, text in texts:
                tokens = text.split()
                for kind, token, detail in text_ocr_signals(text):
                    if kind == "digit_lookalike":
                        continue
                    pos = next((i for i, t in enumerate(tokens) if token in t), None)
                    if pos is not None:
                        candidates.append(
                            _item(
                                block,
                                "3-NGHI LỖI",
                                cell,
                                pos,
                                tokens[pos],
                                None,
                                f"{kind}: {detail}",
                            )
                        )
        for item in candidates:
            if item.item_id not in reviewed:
                items.setdefault(item.item_id, item)
    order = {"1-SỐ LIỆU": 0, "2-BỊ TỪ CHỐI": 1, "3-NGHI LỖI": 2, "4-KIỂM TRA MẪU": 3}
    return sorted(items.values(), key=lambda i: (order[i.priority], i.page, i.block_id, i.position))


AUDITABLE_RULES = ("ok", "digit_letter")  # thay đổi 1 token LLM đã được chấp nhận


def audit_sample(blocks: list[Block], rate: float) -> list[ReviewItem]:
    """Mẫu NGẪU NHIÊN-TẤT ĐỊNH các thay đổi LLM ĐÃ ĐƯỢC CHẤP NHẬN để người duyệt kiểm tra
    chất lượng (N10: duyệt 2-5%). Lý do: sửa sai thành một từ sai khác (gặp thật ở P1.4:
    "kinh dien" → "kinh diễn") không có tín hiệu nào - chỉ kiểm tra mẫu mới thấy.
    Chọn theo thứ tự hash của item_id → cùng block/rate luôn ra cùng mẫu; rate=1 → tất cả.
    Quyết định hợp lệ: keep (LLM đúng) hoặc edit (sửa lại)."""
    if rate <= 0:
        return []
    candidates: list[ReviewItem] = []
    for block in blocks:
        reviewed = {r.item_id for r in block.reviews}
        for fix in block.fixes:
            if not (fix.accepted and fix.rule in AUDITABLE_RULES and len(fix.after.split()) == 1):
                continue
            tokens = _cell_text(block, fix.cell).split()
            pos = _locate(tokens, fix.after, fix.position)
            if pos is None:
                continue
            item = _item(
                block,
                "4-KIỂM TRA MẪU",
                fix.cell,
                pos,
                fix.after,
                None,
                f"kiểm tra mẫu: LLM đã sửa `{fix.before}` → `{fix.after}` ({fix.rule})",
            )
            if item.item_id not in reviewed:
                candidates.append(item)
    if not candidates:
        return []
    count = max(1, round(rate * len(candidates))) if rate < 1 else len(candidates)
    chosen = sorted(candidates, key=lambda i: stable_id(i.item_id))[:count]
    return sorted(chosen, key=lambda i: (i.page, i.block_id, i.position))


def known_items(blocks: list[Block]) -> list[ReviewItem]:
    """Mọi mục có thể xuất hiện trong CSV (hàng đợi + toàn bộ mẫu kiểm tra) - dùng khi nhập."""
    return [*build_queue(blocks), *audit_sample(blocks, 1.0)]


# --------------------------------------------------------------------------- CSV


def export_csv(items: list[ReviewItem], path: Path) -> None:
    """CSV UTF-8 có BOM (Excel mở đúng tiếng Việt). Cột decision/edited_value/... để trống."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        for item in items:
            row = {k: "" if v is None else v for k, v in item.model_dump().items()}
            writer.writerow(
                {**row, "decision": "", "edited_value": "", "reviewer": "", "comment": ""}
            )


def import_csv(path: Path, items: list[ReviewItem]) -> list[Decision]:
    """Đọc quyết định đã điền. Dòng trống `decision` = chưa duyệt (bỏ qua). Mọi dòng sai được
    gom lại và báo một lần (ReviewError) kèm số dòng CSV; không nhập dòng nào nếu có lỗi."""
    known = {i.item_id: i for i in items}
    decisions: list[Decision] = []
    errors: list[str] = []
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        for lineno, row in enumerate(csv.DictReader(fh), start=2):
            decision = (row.get("decision") or "").strip().lower()
            if not decision:
                continue
            item = known.get((row.get("item_id") or "").strip())
            if item is None:
                errors.append(
                    f"dòng {lineno}: item_id '{row.get('item_id')}' không có trong hàng đợi"
                )
                continue
            if decision not in ("accept", "keep", "edit"):
                errors.append(
                    f"dòng {lineno}: decision '{decision}' không hợp lệ (accept / keep / edit)"
                )
                continue
            if decision == "accept":
                if item.suggestion is None:
                    errors.append(
                        f"dòng {lineno}: 'accept' nhưng mục không có gợi ý (dùng keep/edit)"
                    )
                    continue
                value = item.suggestion
            elif decision == "edit":
                value = nfc((row.get("edited_value") or "").strip())
                if not value:
                    errors.append(f"dòng {lineno}: 'edit' nhưng edited_value trống")
                    continue
            else:
                value = item.current
            if (
                item.priority == "1-SỐ LIỆU"
                and decision != "keep"
                and not RE_NUMBER_VALUE.fullmatch(value)
            ):
                errors.append(
                    f"dòng {lineno}: mục SỐ LIỆU phải là số (vd. 500, 7,5-15) - nhận '{value}'"
                )
                continue
            decisions.append(
                Decision(
                    id=item.item_id,
                    decision=cast(DecisionKind, decision),
                    value=value,
                    current=item.current,
                    block_id=item.block_id,
                    cell=item.cell,
                    position=item.position,
                    priority=item.priority,
                    reviewer=(row.get("reviewer") or "").strip(),
                    comment=(row.get("comment") or "").strip(),
                    at=now,
                )
            )
    if errors:
        raise ReviewError(
            f"{path.name}: {len(errors)} dòng không hợp lệ:\n  - " + "\n  - ".join(errors)
        )
    return decisions


def save_decisions(path: Path, new: list[Decision]) -> list[Decision]:
    """Gộp quyết định mới vào decisions.jsonl (cùng item_id → quyết định mới thắng)."""
    merged = {d.id: d for d in (read_jsonl(path, Decision) if path.is_file() else [])}
    merged.update({d.id: d for d in new})
    write_jsonl(path, merged.values())
    return list(merged.values())


# --------------------------------------------------------------------------- áp quyết định


class ApplyReport(BaseModel):
    applied: int = 0
    stale: list[str] = []


def _set_cell(block: Block, cell: str | None, text: str) -> None:
    if cell is None:
        block.text = text
        return
    r, c = (int(x) for x in cell[1:].split("c"))
    rows = block.rows or []
    rows[r][c] = text
    block.text = "\n".join(" | ".join(row) for row in rows)


def apply_decisions(
    blocks: list[Block], decisions: list[Decision]
) -> tuple[list[Block], ApplyReport]:
    """Áp quyết định lên bản sao của `blocks`; cập nhật cờ theo các mục còn chờ."""
    out = [b.model_copy(deep=True) for b in blocks]
    by_id = {b.id: b for b in out}
    report = ApplyReport()
    for d in decisions:
        block = by_id.get(d.block_id)
        if block is None:
            report.stale.append(d.id)
            continue
        text = _cell_text(block, d.cell)
        if d.position == WHOLE:
            if text != d.current:
                report.stale.append(d.id)
                continue
            new_text = d.value
        else:
            tokens = text.split()
            pos = _locate(tokens, d.current, d.position)
            if pos is None:
                report.stale.append(d.id)
                continue
            tokens[pos] = d.value
            new_text = " ".join(tokens)
        _set_cell(block, d.cell, new_text)
        if d.value != d.current:
            block.fixes.append(
                Fix(
                    position=max(d.position, 0),
                    before=d.current,
                    after=d.value,
                    accepted=True,
                    rule="review",
                    cell=d.cell,
                )
            )
        block.reviews.append(
            Review(
                item_id=d.id,
                decision=d.decision,
                before=d.current,
                after=d.value,
                reviewer=d.reviewer,
                at=d.at,
                cell=d.cell,
                position=d.position,
            )
        )
        report.applied += 1
    pending = build_queue(out)
    for block in out:
        mine = [i for i in pending if i.block_id == block.id]
        flags = set(block.flags)
        if not any(i.priority == "1-SỐ LIỆU" for i in mine):
            flags.discard("dose_suspect")
        if not any(i.priority == "2-BỊ TỪ CHỐI" for i in mine):
            flags -= {
                "fix_partially_rejected",
                "number_change_rejected",
                "fix_rejected",
                "fix_failed",
            }
        if not any(i.priority == "3-NGHI LỖI" for i in mine):
            flags.discard("ocr_suspect")
        if block.reviews:
            flags.add("reviewed")
        block.flags = sorted(flags)
    return out, report
