"""Bộ luật của sách IASP: nối luật trong layout.py / lines.py vào giao diện chung."""

from typing import Any

from dataminer.books.base import BookRules
from dataminer.books.iasp import headings, layout, lines, toc
from dataminer.core.config import BlocksCfg, HeadingsCfg, Settings
from dataminer.model.block import Block
from dataminer.model.line import Line
from dataminer.model.toc import TocResult
from dataminer.model.tree import Confidence, Level, Node
from dataminer.text.blocks import LineKind


class IaspRules(BookRules):
    book_id = "iasp"
    chapter_prefix = toc.RE_CHAPTER_PREFIX  # "GROUP XI: …" ↔ mục lục "XI. …"

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
        content = settings.project.content_pages or (1, 10_000)
        return toc.extract_toc(
            settings.paths.raw_dir / settings.project.book_file,
            book_id=settings.project.book_id,
            cfg=settings.p2.toc,
            content_pages=content,
            furniture=settings.p1.furniture,
        )

    def rule_level(
        self, block: Block, body_size: float, cfg: HeadingsCfg
    ) -> tuple[Level, Confidence, list[str]]:
        return headings.rule_level(block, body_size, cfg)

    def display_title(self, text: str, level: str) -> str:
        return headings.display_title(text, level)

    def section_key(self, title: str) -> str:
        return headings.section_key(title)

    def review_units(self, nodes: list[Node]) -> list[Node]:
        return [n for n in nodes if headings.is_syndrome(n)]  # gồm GROUP-hội chứng (XVI-1)

    def annotate_tree(self, nodes: list[Node]) -> list[str]:
        return headings.annotate_tree(nodes)


RULES = IaspRules()
