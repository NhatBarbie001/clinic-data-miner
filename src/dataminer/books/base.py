"""Giao diện "bộ luật sách": phần dùng chung (pipeline/) chỉ hỏi luật của sách qua lớp này.

Mỗi sách trả lời 6 câu hỏi (docs/phases/P2R/architecture.md mục 4):
    1. đọc trang nào                 → cấu hình (pilot / phạm vi)
    2. thứ tự đọc các dòng           → order_lines          (mặc định: theo hàng - sách 1 cột)
    3. dòng nào là số trang          → page_number          (mặc định: "12", "- 12 -", "Trang 12")
    4. dòng nào là tiêu đề / nội dung → classify_line, numbering   (riêng từng sách)
    5. mục lục đọc thế nào           → read_toc             (riêng từng sách)
    6. tiêu đề thuộc cấp nào         → rule_level, chapter_prefix, display_title
Phương thức trừu tượng = BẮT BUỘC mỗi sách tự viết; còn lại có mặc định dùng chung.
"""

import re
from abc import ABC, abstractmethod
from typing import Any

from dataminer.core.config import BlocksCfg, HeadingsCfg, Settings
from dataminer.model.block import Block
from dataminer.model.line import Line
from dataminer.model.toc import TocResult
from dataminer.model.tree import Confidence, Level
from dataminer.pdf.furniture import page_number_of
from dataminer.pdf.layout import reading_order
from dataminer.structure.tree_builder import display_title
from dataminer.text.blocks import LineKind


class BookRules(ABC):
    """Luật của một cuốn sách. Sách nào khác mặc định ở đâu thì ghi đè đúng chỗ đó."""

    book_id: str = "book"
    # tiền tố chương bỏ đi khi so tiêu đề ↔ mục lục (so trên chữ đã bỏ dấu); None = không bỏ
    chapter_prefix: re.Pattern[str] | None = None

    # ---------------------------------------------------------------- P1: đọc trang
    def order_lines(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Thứ tự đọc các dòng của MỘT trang. Mặc định: theo hàng (sách 1 cột)."""
        return reading_order(items)

    def page_number(self, text: str) -> int | None:
        """Số trang in nếu dòng ở lề chỉ là số trang, ngược lại None."""
        return page_number_of(text)

    @abstractmethod
    def classify_line(self, line: Line, body_size: float, cfg: BlocksCfg) -> LineKind:
        """Dòng này là tiêu đề / gạch đầu dòng / danh sách số / chú thích / mục lục / thân bài?"""

    @abstractmethod
    def numbering(self, text: str) -> str | None:
        """Số thứ tự của một tiêu đề (vd. "3.1"), None nếu không có."""

    # ---------------------------------------------------------------- P2: dựng cây
    @abstractmethod
    def read_toc(self, settings: Settings) -> TocResult:
        """Tìm và đọc mục lục của sách (TocResult rỗng nếu sách không có)."""

    @abstractmethod
    def rule_level(
        self, block: Block, body_size: float, cfg: HeadingsCfg
    ) -> tuple[Level, Confidence, list[str]]:
        """Cấp của một tiêu đề theo quy tắc của sách (lớp 1 của P2.2) + độ tin cậy + lý do."""

    def display_title(self, text: str, level: str) -> str:
        """Tên hiển thị của nút (dùng làm `path` → ID ổn định)."""
        return display_title(text, level)
