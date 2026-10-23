"""Sách mẫu (book01) - luật cho TỪNG DÒNG: dòng nào là tiêu đề / gạch đầu dòng / chú thích /
mục lục; số thứ tự của tiêu đề ("CHƯƠNG 1", "3", "3.1"). Chuyển nguyên văn từ text/blocks.py."""

import re

from dataminer.core.config import BlocksCfg
from dataminer.core.text_vi import nfc
from dataminer.model.line import Line
from dataminer.text.blocks import RE_NUMBERED_ITEM, LineKind, bullet_marker, is_upper_text

RE_CHAPTER = re.compile(r"^(CHƯƠNG|Chương|PHẦN|Phần|BÀI|Bài)\s+([\dIVXLC]+)\b")


RE_SUB = re.compile(r"^(\d{1,2}\.\d{1,2})\.?\s+\S")


RE_SECTION = re.compile(r"^(\d{1,2})\.\s+\S")


RE_TOC_ENTRY = re.compile(r"(\.{4,}|…{2,})\s*\d+\s*$")


RE_CAPTION = re.compile(r"^(Bảng|BẢNG|Hình|HÌNH|Biểu đồ|Sơ đồ)\s+\d+(\.\d+)*\.?(\s|$)")


def heading_signals(
    text: str, size: float, body_size: float, bold: bool = False
) -> tuple[list[str], str]:
    """(lý do, cấp đoán) của một dòng có thể là tiêu đề - dùng chung cho khảo sát (P0.5)."""
    text = nfc(text)
    upper = is_upper_text(text)
    reasons: list[str] = []
    if size >= body_size + 0.75:
        reasons.append(f"cỡ chữ {size:.1f} > thân bài {body_size:.1f}")
    if upper:
        reasons.append("viết hoa toàn bộ")
    if bold:
        reasons.append("in đậm")
    level = "unknown"
    if RE_CHAPTER.match(text):
        reasons.append("mẫu 'CHƯƠNG n'")
        level = "chapter"
    elif RE_SUB.match(text):
        reasons.append("đánh số 'n.m.'")
        level = "subsection"
    elif RE_SECTION.match(text):
        reasons.append("đánh số 'n.'")
        level = "section"
    elif upper and size >= body_size + 1.5:
        level = "disease_or_title"
    return reasons, level


def numbering_of(text: str) -> str | None:
    text = nfc(text)
    if m := RE_CHAPTER.match(text):
        return f"{m.group(1).upper()} {m.group(2)}"
    if m := RE_SUB.match(text):
        return m.group(1)
    if m := RE_NUMBERED_ITEM.match(text):
        return m.group(1)
    return None


def classify_line(ln: Line, body_size: float, cfg: BlocksCfg) -> LineKind:
    """Loại một dòng (không xét bảng - bảng được nhận diện theo hàng trước đó)."""
    text = nfc(ln.text)
    if RE_TOC_ENTRY.search(text):
        return "toc_entry"
    if RE_CAPTION.match(text):
        return "caption"
    if bullet_marker(text, cfg.bullet_markers):
        return "bullet_start"
    upper = is_upper_text(text)
    if RE_CHAPTER.match(text) or RE_SUB.match(text):
        return "heading"
    if RE_SECTION.match(text):
        # "3. TRIỆU CHỨNG" là tiêu đề; "1. Uống thuốc sau ăn." là danh sách đánh số
        if upper or ln.size >= body_size + 0.75:
            return "heading"
        return "numbered_item"
    if RE_NUMBERED_ITEM.match(text):
        return "numbered_item"
    if upper or ln.size >= body_size + cfg.heading_size_delta:
        return "heading"
    return "body"
