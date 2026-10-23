"""Danh sách sách đã có bộ luật: `project.book_id` (cấu hình) → bộ luật."""

from collections.abc import Callable

from dataminer.books.base import BookRules
from dataminer.core.config import ConfigError, Settings


def _book01() -> BookRules:
    from dataminer.books.book01.rules import RULES

    return RULES


REGISTRY: dict[str, Callable[[], BookRules]] = {
    "book01": _book01,
}


def rules_for(settings: Settings) -> BookRules:
    """Bộ luật của sách đang cấu hình; sách chưa có luật → lỗi kèm danh sách sách hợp lệ."""
    book_id = settings.project.book_id
    factory = REGISTRY.get(book_id)
    if factory is None:
        known = ", ".join(sorted(REGISTRY))
        raise ConfigError(
            f"Sách '{book_id}' chưa có bộ luật (src/dataminer/books/). Sách đã có: {known}"
        )
    return factory()
