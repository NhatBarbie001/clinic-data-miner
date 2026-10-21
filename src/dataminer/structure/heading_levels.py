"""P2.2 - Phân cấp tiêu đề: mỗi block `heading` của P1 → chương / bệnh / mục / mục con / khác.

Ba lớp, lớp sau chỉ chạy khi lớp trước chưa chắc:
    1. Quy tắc   đánh số ("CHƯƠNG n", "n.", "n.m."), IN HOA, cỡ chữ so với thân bài.
    2. Mục lục   tiêu đề không đánh số khớp một mục của mục lục (P2.1) → cấp theo mục lục.
    3. LLM       chỉ cho tiêu đề còn tin cậy `low` (tác vụ `classify`, nhãn đóng).
Mỗi quyết định kèm lý do + độ tin cậy để người duyệt hiểu vì sao.
Xem docs/phases/P2/P2.2_plan.md.
"""

import asyncio
import difflib
import json
import re
from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, Field

from dataminer.core.config import HeadingsCfg
from dataminer.core.llm_client import LLMClient
from dataminer.core.prompts import Prompt
from dataminer.ingest.blocks import Block
from dataminer.structure.toc import RE_CHAPTER_NORM, TocEntry, match_key, norm_title

Level = Literal["chapter", "disease", "section", "subsection", "other"]
Confidence = Literal["high", "medium", "low"]
RE_SUB_NUM = re.compile(r"^\d{1,2}\.\d{1,2}$")
RE_SECTION_NUM = re.compile(r"^\d{1,2}$")
RE_CHAPTER_PREFIX = re.compile(r"^(chuong|phan)\s+\S+?[.:]?\s+")
SECTION_SIZE_DELTA = 0.75  # "3. Triệu chứng" (không IN HOA) vẫn là mục nếu cỡ ≥ thân bài + 0.75


class HeadingDecision(BaseModel):
    block_id: str
    text: str
    page: int  # trang PDF
    level: Level
    confidence: Confidence
    reasons: list[str]
    toc_match: str | None = None  # title_norm của mục lục khớp
    source: Literal["rules", "toc", "llm"] = "rules"
    numbering: str | None = None
    flags: list[str] = Field(default_factory=list)


class HeadingResult(BaseModel):
    decisions: list[HeadingDecision]
    body_size: float
    toc_missing: list[str]  # mục lục có, thân sách (trong phạm vi) không thấy
    warnings: list[str] = Field(default_factory=list)
    llm_calls: int = 0
    llm_cost_usd: float = 0.0
    prompt: str | None = None  # id@version nếu có gọi LLM


class LLMHeadingLabel(BaseModel):
    """Schema trả về của LLM (nhãn đóng)."""

    level: Level
    reason: str = Field(max_length=300)


# --------------------------------------------------------------------------- lớp 1


def body_size_of(blocks: Sequence[Block]) -> float:
    """Cỡ chữ thân bài = trung vị (theo số ký tự) cỡ chữ của đoạn văn và gạch đầu dòng."""
    weighted = sorted(
        (b.font_size, len(b.text)) for b in blocks if b.kind in ("paragraph", "list_item")
    )
    total = sum(w for _, w in weighted)
    acc = 0
    for size, weight in weighted:
        acc += weight
        if acc * 2 >= total:
            return round(size, 1)
    return 0.0


def rule_level(
    block: Block, body_size: float, cfg: HeadingsCfg
) -> tuple[Level, Confidence, list[str]]:
    """Lớp 1: cấp theo đánh số, IN HOA, cỡ chữ."""
    num = block.numbering
    size = f"cỡ {block.font_size:.1f}"
    if num and RE_CHAPTER_NORM.match(norm_title(num)):
        return "chapter", "high", [f"mẫu '{num}'"]
    # P1 chỉ nhận "CHƯƠNG n" có dấu; OCR mất dấu ("CHUONG 1.") → so trên chữ đã bỏ dấu.
    if chapter := RE_CHAPTER_NORM.match(norm_title(block.text)):
        return "chapter", "high", [f"mẫu '{chapter.group(0)}' (so không dấu)"]
    if num and RE_SUB_NUM.match(num):
        return "subsection", "high", [f"đánh số mục con '{num}'"]
    if num and RE_SECTION_NUM.match(num):
        if block.is_upper:
            return "section", "high", [f"đánh số mục '{num}' + IN HOA"]
        if block.font_size >= body_size + SECTION_SIZE_DELTA:
            return "section", "medium", [f"đánh số mục '{num}', {size} ≥ thân bài + 0.75"]
        return "other", "low", [f"đánh số '{num}' nhưng chữ thường, {size} ~ thân bài"]
    threshold = body_size + cfg.disease_size_delta
    if block.is_upper and block.font_size >= threshold:
        rule = f"thân bài {body_size:.1f} + {cfg.disease_size_delta}"
        return "disease", "medium", [f"IN HOA, không đánh số, {size} ≥ {rule}"]
    if block.is_upper:
        return "other", "low", [f"IN HOA, không đánh số, {size} < ngưỡng bệnh {threshold:.1f}"]
    return "other", "low", [f"không IN HOA, không đánh số, {size}"]


# --------------------------------------------------------------------------- lớp 2


def _keys(text: str) -> list[str]:
    """Các biến thể khóa so khớp: nguyên tiêu đề, và (với chương) bỏ phần "Chương n."."""
    keys = [match_key(text)]
    stripped = RE_CHAPTER_PREFIX.sub("", norm_title(text))
    if stripped != norm_title(text):
        keys.append(match_key(stripped))
    return [k for k in keys if k]


def toc_similarity(heading: str, entry: str) -> float:
    """Độ giống lớn nhất giữa các biến thể khóa (1.0 = trùng sau khi bỏ dấu/khoảng trắng)."""
    return max(
        (difflib.SequenceMatcher(None, a, b).ratio() for a in _keys(heading) for b in _keys(entry)),
        default=0.0,
    )


def match_toc(
    decisions: list[HeadingDecision],
    blocks: dict[str, Block],
    toc: Sequence[TocEntry],
    cfg: HeadingsCfg,
) -> tuple[list[str], list[str]]:
    """Lớp 2 (tại chỗ): tiêu đề không đánh số mục ↔ mục lục. Trả (mục lục thiếu, cảnh báo).

    Mỗi mục lục chỉ ghép một lần; ưu tiên trùng khóa, rồi khớp gần ≥ `toc_match_min`
    (tiêu đề mục lục có thể còn lỗi nhầm ký tự: "Viêrn loét…", "Cbương 2" - xem P2.1).
    """
    warnings: list[str] = []
    used: set[int] = set()
    candidates = [d for d in decisions if d.level in ("chapter", "disease", "other")]
    for d in candidates:
        scored = [(toc_similarity(d.text, e.title), i) for i, e in enumerate(toc) if i not in used]
        score, idx = max(scored, default=(0.0, -1))
        if score < cfg.toc_match_min:
            if d.level == "disease" and toc:
                d.confidence = "low"
                d.flags.append("missing_from_toc")
                d.reasons.append("không khớp mục nào trong mục lục")
            continue
        entry = toc[idx]
        used.add(idx)
        how = "trùng khóa" if score == 1.0 else f"khớp gần {score:.2f}"
        reason = f"khớp mục lục: '{entry.title}' (tr.in {entry.printed_page}, {how})"
        if entry.level != d.level:
            reason += f" → đổi {d.level} thành {entry.level}"
        d.level, d.confidence, d.source = entry.level, "high", "toc"
        d.toc_match = entry.title_norm
        d.reasons.append(reason)
        page = blocks[d.block_id].page_start
        if entry.pdf_page is not None and entry.pdf_page != page:
            d.flags.append("toc_page_mismatch")
            warnings.append(
                f"'{d.text}' ở trang PDF {page} nhưng mục lục ghi trang PDF {entry.pdf_page}."
            )

    pages = [blocks[d.block_id].page_start for d in decisions]
    lo, hi = (min(pages), max(pages)) if pages else (0, -1)
    missing = [
        e.title
        for i, e in enumerate(toc)
        if i not in used and e.pdf_page is not None and lo <= e.pdf_page <= hi
    ]
    warnings.extend(
        f"Mục lục có '{t}' nhưng không tìm thấy tiêu đề nào khớp trong thân sách." for t in missing
    )
    return missing, warnings


# --------------------------------------------------------------------------- kiểm tra số


def check_numbering(decisions: Sequence[HeadingDecision]) -> list[str]:
    """Trong một bệnh: mục 1, 2, 3… liên tiếp; mục con n.1, n.2… thuộc mục n. Lệch → cờ.

    Chỉ cảnh báo, không đổi cấp: lệch số là dấu hiệu sót tiêu đề hoặc OCR đọc nhầm số.
    """
    warnings: list[str] = []
    section = 0
    sub = 0
    for d in decisions:
        if d.level in ("chapter", "disease"):
            section, sub = 0, 0
            continue
        if d.numbering is None:
            continue
        expected: str | None = None
        if d.level == "section" and RE_SECTION_NUM.match(d.numbering):
            n = int(d.numbering)
            if n != section + 1:
                expected = str(section + 1)
            section, sub = n, 0
        elif d.level == "subsection" and RE_SUB_NUM.match(d.numbering):
            n, m = (int(x) for x in d.numbering.split("."))
            if n != section or m != sub + 1:
                expected = f"{section}.{sub + 1}"
            sub = m if n == section else sub
        if expected is not None:
            d.flags.append("numbering_gap")
            warnings.append(
                f"'{d.text}' (trang PDF {d.page}): số '{d.numbering}', mong đợi '{expected}' "
                "- có thể sót tiêu đề hoặc OCR đọc nhầm số."
            )
    return warnings


# --------------------------------------------------------------------------- lớp 3


def _context(blocks: Sequence[Block], index: int, body_size: float) -> str:
    """Ngữ cảnh gửi LLM: tiêu đề + đặc trưng, tiêu đề trước/sau, block nội dung kế tiếp."""
    b = blocks[index]
    prev = next((x.text for x in reversed(blocks[:index]) if x.kind == "heading"), None)
    nxt = next((x.text for x in blocks[index + 1 :] if x.kind == "heading"), None)
    content = next((x.text for x in blocks[index + 1 :] if x.kind != "heading"), None)
    return json.dumps(
        {
            "heading": b.text,
            "numbering": b.numbering,
            "is_upper": b.is_upper,
            "font_size": b.font_size,
            "body_font_size": body_size,
            "previous_heading": prev,
            "next_heading": nxt,
            "first_content_after": (content or "")[:300],
        },
        ensure_ascii=False,
    )


async def _ask_llm(
    client: LLMClient, prompt: Prompt, context: str
) -> tuple[LLMHeadingLabel, float, bool]:
    messages = [
        {"role": "system", "content": prompt.text},
        {"role": "user", "content": context},
    ]
    label, resp = await client.chat_json("classify", messages, LLMHeadingLabel)
    return label, resp.usage.cost_usd, resp.cached


# --------------------------------------------------------------------------- toàn bộ


def classify_headings(
    blocks: Sequence[Block],
    toc: Sequence[TocEntry],
    cfg: HeadingsCfg | None = None,
    *,
    client: LLMClient | None = None,
    prompt: Prompt | None = None,
) -> HeadingResult:
    """Cấp của mọi block `heading` (theo thứ tự đọc). LLM chỉ chạy khi có `client` + `prompt`
    và `cfg.llm_fallback`."""
    cfg = cfg or HeadingsCfg()
    body = body_size_of(blocks)
    by_id = {b.id: b for b in blocks}
    index_of = {b.id: i for i, b in enumerate(blocks)}
    decisions: list[HeadingDecision] = []
    for b in blocks:
        if b.kind != "heading":
            continue
        level, conf, reasons = rule_level(b, body, cfg)
        decisions.append(
            HeadingDecision(
                block_id=b.id,
                text=b.text,
                page=b.page_start,
                level=level,
                confidence=conf,
                reasons=reasons,
                numbering=b.numbering,
            )
        )

    warnings: list[str] = []
    missing: list[str] = []
    if cfg.use_toc and toc:
        missing, toc_warnings = match_toc(decisions, by_id, toc, cfg)
        warnings.extend(toc_warnings)
    elif cfg.use_toc:
        warnings.append("Không có mục lục - cấp tiêu đề chỉ dựa trên quy tắc.")

    result = HeadingResult(decisions=decisions, body_size=body, toc_missing=missing)
    low = [d for d in decisions if d.confidence == "low"]
    if low and cfg.llm_fallback and client is not None and prompt is not None:
        contexts = [_context(blocks, index_of[d.block_id], body) for d in low]

        async def run_all() -> list[tuple[LLMHeadingLabel, float, bool]]:
            return await asyncio.gather(*(_ask_llm(client, prompt, c) for c in contexts))

        for d, (label, cost, cached) in zip(low, asyncio.run(run_all()), strict=True):
            if label.level != d.level:
                d.reasons.append(f"LLM đổi {d.level} → {label.level}: {label.reason}")
            else:
                d.reasons.append(f"LLM xác nhận {label.level}: {label.reason}")
            d.level, d.confidence, d.source = label.level, "medium", "llm"
            d.flags.append("level_from_llm")
            result.llm_calls += 0 if cached else 1
            result.llm_cost_usd += cost
        result.prompt = prompt.ref
    elif low:
        warnings.append(
            f"{len(low)} tiêu đề tin cậy thấp chưa được LLM xem (llm_fallback tắt hoặc --no-llm)."
        )

    warnings.extend(check_numbering(decisions))
    result.warnings = warnings
    return result
