"""Hợp đồng dữ liệu: một dòng chữ của PDF (đầu ra của bước đọc PDF, P1.1)."""

from typing import Literal

from pydantic import Field, model_validator

from dataminer.core.schemas import BaseRecord

Zone = Literal["top", "body", "bottom"]


class Line(BaseRecord):
    """Một dòng text của lớp OCR kèm đặc trưng trình bày."""

    page: int  # số trang PDF
    index: int  # thứ tự dòng trong trang, theo thứ tự đọc
    text: str  # đã chuẩn hóa NFC và gộp khoảng trắng (khi đọc bằng read_lines)
    text_raw: str = ""  # nguyên văn từ PDF (có thể NFD); trống → bằng text
    bbox: tuple[float, float, float, float]
    size: float  # cỡ chữ trung bình theo số ký tự của các span
    font: str
    bold: bool
    zone: Zone
    page_width: float = 0.0
    page_height: float = 0.0
    flags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _default_raw(self) -> "Line":
        if not self.text_raw:
            self.text_raw = self.text
        return self
