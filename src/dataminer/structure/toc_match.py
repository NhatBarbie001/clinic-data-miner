"""So khớp tiêu đề ↔ mục lục (dùng chung mọi sách): khóa không dấu, chịu lỗi dính từ; ánh xạ
trang in → trang PDF từ số trang của các trang nội dung."""

from collections.abc import Sequence

from dataminer.core.config import FurnitureCfg
from dataminer.core.text_vi import nfc, strip_diacritics
from dataminer.model.line import Line
from dataminer.pdf.furniture import strip_furniture
from dataminer.pdf.reader import body_font_size


def norm_title(text: str) -> str:
    """Bỏ dấu, chữ thường, gộp khoảng trắng: "Bệnh tiêu hỏa" → "benh tieu hoa"."""
    return " ".join(strip_diacritics(nfc(text)).casefold().split())


def match_key(text: str) -> str:
    """Khóa so khớp chịu lỗi dính từ: chỉ giữ chữ và số của `norm_title`.

    "Thoái hóa khớpgối" và "THOÁI HÓA KHỚP GỐI" → cùng "thoaihoakhopgoi".
    """
    return "".join(ch for ch in norm_title(text) if ch.isalnum())


def content_page_offset(
    lines: Sequence[Line], furniture: FurnitureCfg | None
) -> tuple[int | None, dict[int, int], list[str]]:
    """Độ lệch (PDF - in) và ánh xạ trang in → PDF, từ footer/số trang của MỌI trang (P1.2)."""
    result = strip_furniture(list(lines), body_font_size(list(lines)), furniture)
    printed_to_pdf = {p.printed_page: p.page for p in result.pages if p.printed_page is not None}
    offsets = {pdf - printed for printed, pdf in printed_to_pdf.items()}
    offset = next(iter(offsets)) if len(offsets) == 1 else None
    return offset, printed_to_pdf, result.warnings
