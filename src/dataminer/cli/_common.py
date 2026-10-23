"""Tiện ích chung cho các nhóm lệnh `dm`."""

_book: str | None = None


def set_current_book(book: str | None) -> None:
    """Gọi bởi lệnh gốc `dm` ở MỖI lần gọi (None khi không có --book) → không rò sang lần sau."""
    global _book
    _book = book


def current_book() -> str | None:
    """Sách chọn bằng `dm --book <id>` trong lần gọi hiện tại; None = theo cấu hình. Chỉ CLI
    dùng giá trị này (truyền vào `load_settings(book=…)`); phần còn lại không có trạng thái ẩn."""
    return _book
