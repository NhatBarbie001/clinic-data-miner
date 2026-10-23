"""Sách IASP - luật cho TỪNG DÒNG (L2, L5-L7, L10): số trang, dòng nào là tiêu đề.

Tiêu đề trong sách này nhận ra bằng CHỮ ĐẬM (không phải IN HOA / đánh số như sách mẫu):
- chữ đậm, cỡ ≥ thân bài + 2 (cỡ 12.5-15.5): tên phần / nhóm chữ cái / GROUP La Mã / hội chứng;
- chữ đậm, cỡ thường, ngắn, không kết thúc bằng dấu chấm: tên mục ("Definition", "Site"…).
Tiêu đề nhiều dòng nối theo luật riêng (`heading_joins`, L5-L7).
"""

import re

from dataminer.books.iasp.codes import RE_CODE_END, syndrome_code
from dataminer.core.config import BlocksCfg
from dataminer.core.text_vi import nfc
from dataminer.model.line import Line
from dataminer.text.blocks import RE_NUMBERED_ITEM, LineKind, bullet_marker, is_upper_text

RE_PAGE = re.compile(r"^(?:page\s+)?(\d{1,4})$", re.IGNORECASE)  # "Page 121", "1"
RE_GROUP = re.compile(r"^GROUP\s+([IVXLC]+)\s*:")  # "GROUP XI:  PAIN IN THE SHOULDER…"
RE_LETTER = re.compile(r"^([A-H])\.(\s|$)")  # "E." / "A. RELATIVELY GENERALIZED SYNDROMES"
RE_LETTER_ONLY = re.compile(r"^[A-H]\.$")
RE_PAREN_LINE = re.compile(r"^\(.*\)$")  # "(XXVI-9.1)", "(CRPS)", "(Tic Douloureux) (II-1)"
# "Intermittent Claudication (XV-1)" ↵ "and Rest Pain (XV-2)": mục gộp 2 hội chứng
RE_AND_LINE = re.compile(r"^(and|or)\s")
RE_NOTE = re.compile(r"^(Note:|N\.B\.)")  # ghi chú in đậm = nội dung, không phải tên mục
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
        if RE_NOTE.match(text):
            return "body"  # ghi chú in đậm "Note: “b” coding used to allow …" là nội dung
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
    """Số hiệu của tiêu đề: GROUP → "XI"; nhóm chữ cái → "E"; hội chứng → mã đã chuẩn hóa
    ở cuối tên "XI-1" (L8)."""
    text = " ".join(nfc(text).split())
    if m := RE_GROUP.match(text):
        return m.group(1)
    if m := RE_LETTER.match(text):
        return m.group(1)
    return syndrome_code(text)


def heading_joins(prev: str, text: str) -> bool:
    """Dòng tiêu đề `text` nối vào tiêu đề đang mở `prev`? (L5-L7)
    - dòng bắt đầu bằng "and"/"or" thường → nối (mục gộp 2 hội chứng, kể cả sau mã);
    - tên hội chứng đã kết thúc bằng mã "(XI-1)" → dừng;
    - dòng chỉ gồm ngoặc "(XXVI-9.1)", "(CRPS)" → nối (dù IN HOA khác kiểu dòng trên);
    - "E." đứng riêng + dòng IN HOA "LOCAL SYNDROMES …" → nối;
    - còn lại: dòng sau không mở nhóm mới (GROUP / chữ cái) và cùng kiểu IN HOA."""
    prev = " ".join(nfc(prev).split())
    text = " ".join(nfc(text).split())
    if RE_AND_LINE.match(text):
        return True
    if RE_CODE_END.search(prev):
        return False
    if RE_PAREN_LINE.match(text):
        return True
    if RE_LETTER_ONLY.match(prev):
        return is_upper_text(text)
    if RE_GROUP.match(text) or RE_LETTER.match(text):
        return False
    return is_upper_text(text) == is_upper_text(prev)
