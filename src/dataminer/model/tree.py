"""Hợp đồng dữ liệu: cấp tiêu đề (P2.2) và nút của cây tài liệu (P2.3-P2.4).
Schema `Node` ở docs/phases/P2/plan.md mục 2."""

from typing import Literal

from pydantic import BaseModel, Field

from dataminer.core.schemas import BaseRecord

# part = nhóm lớn trên chương (sách IASP: nhóm chữ cái "E. LOCAL SYNDROMES …"); sách mẫu không có
Level = Literal["part", "chapter", "disease", "section", "subsection", "other"]


Confidence = Literal["high", "medium", "low"]


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


NodeLevel = Literal["book", "part", "chapter", "disease", "section", "subsection", "front"]


class Node(BaseRecord):
    level: NodeLevel
    parent_id: str | None
    order: int  # thứ tự trong cha
    title: str  # tiêu đề gốc (sau P1), vd. "3. TRIỆU CHỨNG"
    title_norm: str
    display_title: str  # dạng đọc được, vd. "Triệu chứng"
    numbering: str | None = None
    section_type: str | None = None  # P2.4 điền cho section/subsection
    section_source: str | None = None  # P2.4: map | map_fuzzy | inherited | llm | none
    path: list[str]
    heading_block_id: str | None = None
    block_ids: list[str] = Field(default_factory=list)  # nội dung RIÊNG của nút (không gồm con)
    text: str = ""
    page_start: int  # phạm vi trang PDF của CẢ nhánh
    page_end: int
    printed_start: int | None = None
    printed_end: int | None = None
    flags: list[str] = Field(default_factory=list)
    # thuộc tính riêng của sách (BookRules.annotate_tree), vd. IASP: {"iasp_codes": ["102.X4b"]}
    attrs: dict[str, list[str]] = Field(default_factory=dict)
