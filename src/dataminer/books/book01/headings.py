"""Sách mẫu (book01) - luật CẤP TIÊU ĐỀ và cách hiển thị tên nút.

Lớp 1 của P2.2: đánh số ("CHƯƠNG n", "n.", "n.m."), IN HOA, cỡ chữ so với thân bài.
Chuyển nguyên văn từ structure/heading_levels.py và structure/tree_builder.py."""

import re

from dataminer.books.book01.toc import RE_CHAPTER_NORM
from dataminer.core.config import HeadingsCfg
from dataminer.model.block import Block
from dataminer.model.tree import Confidence, Level
from dataminer.structure.heading_levels import RE_SECTION_NUM, RE_SUB_NUM
from dataminer.structure.toc_match import norm_title
from dataminer.structure.tree_builder import display_title as default_display_title

RE_CHAPTER_PREFIX = re.compile(r"^(chuong|phan)\s+\S+?[.:]?\s+")


SECTION_SIZE_DELTA = 0.75  # "3. Triệu chứng" (không IN HOA) vẫn là mục nếu cỡ ≥ thân bài + 0.75


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


RE_CHAPTER_DISPLAY = re.compile(r"^(Chương|Phần|Chuong|Phan)\s+\S+?[.:]\s+")


def display_title(text: str, level: str) -> str:
    """Tên hiển thị của sách mẫu: như mặc định, thêm viết hoa chữ đầu sau "Chương n."
    ("CHƯƠNG 1. BỆNH…" → "Chương 1. Bệnh…")."""
    title = default_display_title(text, level)
    if m := RE_CHAPTER_DISPLAY.match(title):  # "Chương 1. bệnh…" → "Chương 1. Bệnh…"
        rest = title[m.end() :]
        title = title[: m.end()] + rest[:1].upper() + rest[1:]
    return title
