"""Sách IASP - luật cho TỪNG DÒNG (L2, L5-L7, L10): số trang, dòng nào là tiêu đề.

Tiêu đề trong sách này nhận ra bằng CHỮ ĐẬM (không phải IN HOA / đánh số như sách mẫu):
- chữ đậm, cỡ ≥ thân bài + 2 (cỡ 12.5-15.5): tên phần / nhóm chữ cái / GROUP La Mã / hội chứng;
- chữ đậm, cỡ thường, ngắn, không kết thúc bằng dấu chấm: tên mục ("Definition", "Site"…).
"""

import re

from dataminer.core.config import BlocksCfg
from dataminer.core.text_vi import nfc
from dataminer.model.line import Line
from dataminer.text.blocks import RE_NUMBERED_ITEM, LineKind, bullet_marker

RE_PAGE = re.compile(r"^(?:page\s+)?(\d{1,4})$", re.IGNORECASE)  # "Page 121", "1"
RE_GROUP = re.compile(r"^GROUP\s+([IVXLC]+)\s*:")  # "GROUP XI:  PAIN IN THE SHOULDER…"
RE_LETTER = re.compile(r"^([A-G])\.(\s|$)")  # "E." / "A. RELATIVELY GENERALIZED SYNDROMES"
RE_CAPTION = re.compile(r"^(Table|TABLE|Fig\.?|Figure|FIGURE)\s+\d")
BIG_DELTA = 2.0  # tiêu đề lớn: cỡ ≥ thân bài + 2 (thân bài 10, tiêu đề 12.5-15.5)
FIELD_MAX_CHARS = 60  # tên mục dài nhất thấy được: "Summary of Essential Features and Diagnostic"
TABLE_PAGES = range(106, 109)  # L14: bảng "HEADACHE CROSSWALK" (PDF 106-108, đo trên PDF thật)


def page_number(text: str) -> int | None:
    """L2: dòng đầu trang "Page 121" (hoặc chỉ "121") → số trang in."""
    match = RE_PAGE.match(" ".join(nfc(text).split()))
    return int(match.group(1)) if match else None


def classify_line(ln: Line, body_size: float, cfg: BlocksCfg) -> LineKind:
    text = " ".join(nfc(ln.text).split())
    if RE_CAPTION.match(text):
        return "caption"
    if bullet_marker(text, cfg.bullet_markers):
        return "bullet_start"
    if ln.bold:
        if ln.size >= body_size + BIG_DELTA:
            return "heading"  # L5-L7: nhóm, GROUP, hội chứng
        if ln.page in TABLE_PAGES:
            return (
                "body"  # L14: ô in đậm của bảng đối chiếu (mã + tên hội chứng), không phải tên mục
            )
        if len(text) <= FIELD_MAX_CHARS and not text.endswith("."):
            return "heading"  # L10: tên mục
    if RE_NUMBERED_ITEM.match(text):
        return "numbered_item"
    return "body"


def numbering(text: str) -> str | None:
    """Số hiệu ở ĐẦU tiêu đề: "GROUP XI", "E". Mã hội chứng "(XI-1)" ở CUỐI tên KHÔNG tính ở đây:
    dòng "(XI-1)" đứng riêng phải được nối vào tên hội chứng phía trên (L7) - mã tách ở P2."""
    text = " ".join(nfc(text).split())
    if m := RE_GROUP.match(text):
        return f"GROUP {m.group(1)}"
    if m := RE_LETTER.match(text):
        return m.group(1)
    return None
