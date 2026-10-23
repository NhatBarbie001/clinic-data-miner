"""Hợp đồng dữ liệu: mục lục đã phân tích (P2.1)."""

from typing import Literal

from pydantic import BaseModel, Field

TocLevel = Literal["chapter", "disease"]


class TocEntry(BaseModel):
    title: str  # nguyên văn OCR (NFC, gộp khoảng trắng), đã bỏ chấm dẫn và số trang
    title_norm: str  # norm_title(title)
    level: TocLevel
    printed_page: int
    pdf_page: int | None  # trang PDF tương ứng (theo ánh xạ số trang in của P1.2)
    toc_pdf_page: int  # trang mục lục chứa dòng này
    line_id: str  # dòng đầu tiên (truy vết)
    x0: float  # lề trái của dòng đầu (để xét thụt lề)
    flags: list[str] = Field(default_factory=list)  # level_conflict, page_decreasing, …


class TocResult(BaseModel):
    toc_pages: list[int]
    source: Literal["auto", "config", "none"]
    page_offset: int | None  # số trang PDF - số trang in (None nếu không ánh xạ được)
    entries: list[TocEntry]
    warnings: list[str] = Field(default_factory=list)
