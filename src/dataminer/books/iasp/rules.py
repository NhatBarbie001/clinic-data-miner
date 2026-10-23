"""Bộ luật của sách IASP: nối luật trong layout.py / lines.py vào giao diện chung."""

from typing import Any

from dataminer.books.base import BookRules
from dataminer.books.iasp import headings, layout, lines
from dataminer.core.config import BlocksCfg, HeadingsCfg, Settings
from dataminer.model.block import Block
from dataminer.model.line import Line
from dataminer.model.toc import TocResult
from dataminer.model.tree import Confidence, Level, Node
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

    def heading_joins(self, prev: str, text: str) -> bool:
        return lines.heading_joins(prev, text)

    # ---------------------------------------------------------------- P2
    def read_toc(self, settings: Settings) -> TocResult:
        # TODO(I4): đọc mục lục PDF 5-6 (L12) - tạm thời không đối chiếu
        return TocResult(
            toc_pages=[],
            source="none",
            page_offset=None,
            entries=[],
            warnings=["IASP: chưa đọc mục lục (việc I4) - cấp tiêu đề chỉ dựa trên quy tắc."],
        )

    def rule_level(
        self, block: Block, body_size: float, cfg: HeadingsCfg
    ) -> tuple[Level, Confidence, list[str]]:
        return headings.rule_level(block, body_size, cfg)

    def display_title(self, text: str, level: str) -> str:
        return headings.display_title(text, level)

    def annotate_tree(self, nodes: list[Node]) -> list[str]:
        return headings.annotate_tree(nodes)


RULES = IaspRules()
