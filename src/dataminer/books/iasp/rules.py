"""Bộ luật của sách IASP: nối luật trong layout.py / lines.py vào giao diện chung."""

from typing import Any

from dataminer.books.base import BookRules
from dataminer.books.iasp import layout, lines
from dataminer.core.config import BlocksCfg, HeadingsCfg, Settings
from dataminer.model.block import Block
from dataminer.model.line import Line
from dataminer.model.toc import TocResult
from dataminer.model.tree import Confidence, Level
from dataminer.text.blocks import LineKind


class IaspRules(BookRules):
    book_id = "iasp"

    # ---------------------------------------------------------------- P1
    def order_lines(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return layout.column_order(items)

    def page_number(self, text: str) -> int | None:
        return lines.page_number(text)

    def classify_line(self, line: Line, body_size: float, cfg: BlocksCfg) -> LineKind:
        return lines.classify_line(line, body_size, cfg)

    def numbering(self, text: str) -> str | None:
        return lines.numbering(text)

    # ---------------------------------------------------------------- P2 (viết ở I3, I4)
    def read_toc(self, settings: Settings) -> TocResult:
        raise NotImplementedError("IASP: đọc mục lục viết ở việc I4 (docs/phases/P2R/plan.md)")

    def rule_level(
        self, block: Block, body_size: float, cfg: HeadingsCfg
    ) -> tuple[Level, Confidence, list[str]]:
        raise NotImplementedError("IASP: cấp tiêu đề viết ở việc I3 (docs/phases/P2R/plan.md)")


RULES = IaspRules()
