"""Bộ luật của sách mẫu tiếng Việt (book01) + hàm tiện dụng cho test/script của sách mẫu.

`Book01Rules` nối các luật trong lines.py / toc.py / headings.py vào giao diện chung. Các hàm
build_blocks / classify_headings / build_tree ở cuối file = hàm DÙNG CHUNG cùng tên + luật book01,
giữ đúng chữ ký cũ (để test và script mẫu của P1/P2 không phải đổi gì ngoài dòng import).
"""

from collections.abc import Sequence

from dataminer.books.base import BookRules
from dataminer.books.book01 import headings, lines, toc
from dataminer.core.config import BlocksCfg, HeadingsCfg, Settings
from dataminer.core.llm_client import LLMClient
from dataminer.core.prompts import Prompt
from dataminer.model.block import Block
from dataminer.model.line import Line
from dataminer.model.toc import TocEntry, TocResult
from dataminer.model.tree import Confidence, HeadingDecision, Level
from dataminer.structure import heading_levels, tree_builder
from dataminer.text import blocks as text_blocks
from dataminer.text.blocks import LineKind


class Book01Rules(BookRules):
    book_id = "book01"
    chapter_prefix = headings.RE_CHAPTER_PREFIX

    def classify_line(self, line: Line, body_size: float, cfg: BlocksCfg) -> LineKind:
        return lines.classify_line(line, body_size, cfg)

    def numbering(self, text: str) -> str | None:
        return lines.numbering_of(text)

    def read_toc(self, settings: Settings) -> TocResult:
        pdf = settings.paths.raw_dir / settings.project.book_file
        return toc.extract_toc(
            pdf,
            book_id=settings.project.book_id,
            cfg=settings.p2.toc,
            furniture=settings.p1.furniture,
        )

    def rule_level(
        self, block: Block, body_size: float, cfg: HeadingsCfg
    ) -> tuple[Level, Confidence, list[str]]:
        return headings.rule_level(block, body_size, cfg)

    def display_title(self, text: str, level: str) -> str:
        return headings.display_title(text, level)


RULES = Book01Rules()


# ---------------------------------------------------------------- tiện dụng (chữ ký cũ)


def build_blocks(
    lines_: list[Line],
    body_size: float,
    cfg: BlocksCfg | None = None,
    printed: dict[int, int | None] | None = None,
    book_id: str = "book",
) -> list[Block]:
    """`text.blocks.build_blocks` với luật dòng của sách mẫu."""
    return text_blocks.build_blocks(
        lines_,
        body_size,
        cfg,
        printed,
        book_id,
        classify=RULES.classify_line,
        numbering=RULES.numbering,
    )


def classify_headings(
    blocks: Sequence[Block],
    toc_entries: Sequence[TocEntry],
    cfg: HeadingsCfg | None = None,
    *,
    client: LLMClient | None = None,
    prompt: Prompt | None = None,
) -> heading_levels.HeadingResult:
    """`structure.heading_levels.classify_headings` với luật cấp tiêu đề của sách mẫu."""
    return heading_levels.classify_headings(
        blocks,
        toc_entries,
        cfg,
        rule_level=RULES.rule_level,
        chapter_prefix=RULES.chapter_prefix,
        client=client,
        prompt=prompt,
    )


def build_tree(
    blocks: Sequence[Block],
    decisions: Sequence[HeadingDecision],
    *,
    book_id: str,
    book_title: str | None = None,
    toc: Sequence[TocEntry] = (),
) -> tree_builder.TreeResult:
    """`structure.tree_builder.build_tree` với cách hiển thị tên nút của sách mẫu."""
    return tree_builder.build_tree(
        blocks,
        decisions,
        book_id=book_id,
        book_title=book_title,
        toc=toc,
        display_title=RULES.display_title,
    )
