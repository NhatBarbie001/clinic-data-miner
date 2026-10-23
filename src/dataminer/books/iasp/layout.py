"""Sách IASP - thứ tự đọc (luật L3, L4).

Trang thân sách in 2 cột: cột trái bắt đầu ở x ≈ 65, cột phải ở x ≈ 318, khe giữa ở x ≈ 306 (trang
rộng 612pt; đo trên PDF thật, Part II). Dòng vắt ngang qua khe (tiêu đề nhóm, tiêu đề phần) là
dòng TOÀN TRANG. Thứ tự đọc: theo chiều dọc, mỗi dòng toàn trang cắt trang thành đoạn; trong mỗi
đoạn đọc HẾT cột trái rồi mới sang cột phải. Trang 1 cột (mọi dòng dài) → đúng thứ tự dọc.
"""

import re
from typing import Any, Literal

from dataminer.core.text_vi import nfc
from dataminer.pdf.layout import reading_order

SPLIT_X = 306.0  # khe giữa 2 cột (giữa trang 612pt)
GAP = 5.0  # dòng phải vượt khe ít nhất chừng này mới tính là vắt ngang
RE_JUNK = re.compile(r"^Page\s+\d+\s+is\s+BLANK$", re.IGNORECASE)  # L3: trang trắng có chú thích
# L14: bảng "HEADACHE CROSSWALK" (PDF 106-108) - trang 1 cột có bảng, ô mã IHS "12.7.2"
RE_IHS_CODE = re.compile(r"\d{1,2}(\.\d{1,2})+\.?")
TABLE_PAGE_MIN_CODES = 5

Column = Literal["full", "left", "right"]


def column_of(item: dict[str, Any]) -> Column:
    """Dòng thuộc cột trái, cột phải, hay vắt ngang cả trang."""
    x0, _, x1, _ = item["bbox"]
    if x0 >= SPLIT_X - GAP:
        return "right"
    if x1 <= SPLIT_X + GAP:
        return "left"
    return "full"


def is_junk(item: dict[str, Any]) -> bool:
    return RE_JUNK.match(" ".join(nfc(item["text_raw"]).split())) is not None


def is_table_page(items: list[dict[str, Any]]) -> bool:
    """L14: trang bảng đối chiếu (≥ 5 ô mã IHS) - cột bảng trùng khe giữa, KHÔNG đọc theo cột."""
    codes = sum(
        RE_IHS_CODE.fullmatch(" ".join(nfc(it["text_raw"]).split())) is not None for it in items
    )
    return codes >= TABLE_PAGE_MIN_CODES


def column_order(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Thứ tự đọc của MỘT trang (xem docstring module). Bỏ dòng rác (L3); trang bảng (L14) đọc
    theo hàng."""
    if is_table_page(items):
        return reading_order([it for it in items if not is_junk(it)])

    def top(it: dict[str, Any]) -> tuple[float, float]:
        return it["bbox"][1], it["bbox"][0]

    out: list[dict[str, Any]] = []
    segment: list[dict[str, Any]] = []

    def flush() -> None:
        out.extend(sorted((it for it in segment if column_of(it) == "left"), key=top))
        out.extend(sorted((it for it in segment if column_of(it) == "right"), key=top))
        segment.clear()

    for it in sorted((it for it in items if not is_junk(it)), key=top):
        if column_of(it) == "full":
            flush()
            out.append(it)
        else:
            segment.append(it)
    flush()
    return out
