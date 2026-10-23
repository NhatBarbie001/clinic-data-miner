"""Hợp đồng dữ liệu: block (đoạn / tiêu đề / gạch đầu dòng / bảng) và các sửa đổi trên nó
(P1.3-P1.5). Schema ở docs/phases/P1/plan.md mục 2."""

from typing import Literal

from pydantic import BaseModel, Field

from dataminer.core.schemas import BaseRecord

Rule = Literal[
    "ok",
    "digit_letter",
    "split_merge",
    "G-num",
    "G-protect",
    "G-punct",
    "G-sim",
    "G-insdel",
    "G-ratio",
    "review",
]


class Fix(BaseModel):
    """Một thay đổi (đề xuất) ở mức token."""

    position: int  # vị trí token đầu tiên trong văn bản gốc (text_rules)
    before: str
    after: str
    accepted: bool
    rule: Rule
    suggestion: str | None = None  # gợi ý cho người duyệt (số liệu nghi sai)
    cell: str | None = None  # với bảng: ô "r<hàng>c<cột>"


BlockKind = Literal["heading", "paragraph", "list_item", "table", "caption", "toc_entry", "other"]


class Review(BaseModel):
    """Một quyết định đã áp vào block."""

    item_id: str
    decision: Literal["accept", "keep", "edit"]
    before: str
    after: str
    reviewer: str
    at: str
    cell: str | None = None
    position: int = 0  # -1 = quyết định cho cả block / cả ô


class Block(BaseRecord):
    """Đơn vị văn bản sau P1 - đầu vào của P2. Schema ở docs/phases/P1/plan.md mục 2."""

    kind: BlockKind
    text: str  # văn bản cuối cùng (P1.4/P1.5 sẽ cập nhật)
    text_rules: str  # sau quy tắc, trước LLM
    page_start: int
    page_end: int
    printed_start: int | None = None
    printed_end: int | None = None
    line_ids: list[str]
    bbox: tuple[float, float, float, float]  # của dòng đầu
    x0: float
    font_size: float
    is_upper: bool = False
    numbering: str | None = None
    marker: str | None = None  # ký hiệu gạch đầu dòng ("-", "1."...) - không nằm trong text
    rows: list[list[str]] | None = None
    flags: list[str] = Field(default_factory=list)
    fixes: list[Fix] = Field(default_factory=list)  # P1.4: từng sửa đổi token (chấp nhận/từ chối)
    reviews: list[Review] = Field(default_factory=list)  # P1.5: quyết định duyệt tay
