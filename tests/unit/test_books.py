"""S3 - Bộ luật sách: giao diện chung (books/base.py), danh sách sách (registry), luật sách mẫu.

Kiểm 3 điều kiến trúc (docs/phases/P2R/architecture.md):
1. sách phải tự viết đủ các luật riêng (lớp trừu tượng không khởi tạo được nếu thiếu);
2. phần dùng chung KHÔNG mang luật của sách mẫu (mặc định không có "Chương n.", không có mẫu
   "CHƯƠNG"/"Bảng" - các thứ đó chỉ có khi truyền luật book01 vào);
3. pipeline chọn luật theo `project.book_id`; sách chưa có luật → lỗi rõ.
"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from dataminer.books.base import BookRules
from dataminer.books.book01 import rules as book01
from dataminer.books.registry import REGISTRY, rules_for
from dataminer.cli import app
from dataminer.core.config import BlocksCfg, ConfigError, load_settings
from dataminer.model.line import Line
from dataminer.structure import tree_builder
from dataminer.text import blocks as text_blocks
from tests.unit.llm_fakes import make_settings

runner = CliRunner()


def line(text: str, size: float = 10.5) -> Line:
    return Line(
        id="l1",
        page=1,
        index=0,
        text=text,
        bbox=(48, 100, 300, 113),
        size=size,
        font="f",
        bold=False,
        zone="body",
    )


def test_rules_must_implement_book_specific_parts() -> None:
    class Incomplete(BookRules):  # chỉ viết 1 trong 4 luật bắt buộc
        def numbering(self, text: str) -> str | None:
            return None

    with pytest.raises(TypeError, match="classify_line"):
        Incomplete()  # type: ignore[abstract]


def test_defaults_are_generic_not_book01() -> None:
    rules = book01.RULES
    # thứ tự đọc + số trang: book01 dùng mặc định chung
    assert type(rules).order_lines is BookRules.order_lines
    assert type(rules).page_number is BookRules.page_number
    # tên hiển thị: mặc định KHÔNG biết "Chương n."; luật book01 thì có
    assert tree_builder.display_title("CHƯƠNG 1. BỆNH HÔ HẤP", "chapter") == "Chương 1. bệnh hô hấp"
    assert rules.display_title("CHƯƠNG 1. BỆNH HÔ HẤP", "chapter") == "Chương 1. Bệnh hô hấp"
    assert tree_builder.display_title("3. TRIỆU CHỨNG", "section") == "Triệu chứng"


def test_book01_line_rules() -> None:
    rules = book01.RULES
    cfg = BlocksCfg()
    assert rules.classify_line(line("CHƯƠNG 2. TIM MẠCH", 14), 10.5, cfg) == "heading"
    assert rules.classify_line(line("Bảng 2.1. Phác đồ"), 10.5, cfg) == "caption"
    assert rules.classify_line(line("- Sốt cao."), 10.5, cfg) == "bullet_start"
    assert rules.classify_line(line("Viêm gan ........ 12"), 10.5, cfg) == "toc_entry"
    assert rules.numbering("3.1. Lâm sàng") == "3.1"
    assert rules.numbering("CHƯƠNG 2. TIM") == "CHƯƠNG 2"


def test_generic_block_builder_requires_book_rules() -> None:
    """Hàm dùng chung không có luật mặc định cho dòng: phải truyền luật của một sách."""
    with pytest.raises(TypeError, match="classify"):
        text_blocks.build_blocks([line("x")], 10.5)  # type: ignore[call-arg]
    # luật khác → kết quả khác: một sách coi MỌI dòng là thân bài
    built = text_blocks.build_blocks(
        [line("CHƯƠNG 2. TIM MẠCH", 14)],
        10.5,
        classify=lambda ln, body, cfg: "body",
        numbering=lambda text: None,
    )
    assert [b.kind for b in built] == ["paragraph"]
    assert [b.kind for b in book01.build_blocks([line("CHƯƠNG 2. TIM MẠCH", 14)], 10.5)] == [
        "heading"
    ]


def test_registry_selects_rules_by_book_id(tmp_path: Path) -> None:
    root = tmp_path
    assert rules_for(make_settings(root)) is book01.RULES  # cấu hình mặc định: book01
    assert set(REGISTRY) == {"book01", "iasp"}
    other = make_settings(root / "x", DM__PROJECT__BOOK_ID="chua_co")
    with pytest.raises(ConfigError, match=r"Sách 'chua_co' chưa có bộ luật.*book01, iasp"):
        rules_for(other)


# ---------------------------------------------------------------- S4: hồ sơ sách, --book


def _demo_book(root: Path) -> None:
    """Thêm một sách 'demo' (chỉ có hồ sơ, chưa có bộ luật) vào dự án tạm."""
    (root / "configs" / "books" / "demo").mkdir(parents=True)
    (root / "configs" / "books" / "demo" / "book.yaml").write_text(
        "project:\n  book_file: demo.pdf\npilot:\n  page_start: 10\n  page_end: 12\n",
        encoding="utf-8",
    )


def test_profile_layer_and_book_placeholders(tmp_path: Path) -> None:
    s = make_settings(tmp_path)
    assert s.project.book_id == "book01" and s.project.book_file == "book01.pdf"
    assert (s.pilot.page_start, s.pilot.page_end) == (4, 9)  # từ hồ sơ sách
    assert "configs/books/book01/book.yaml" in s.sources
    assert s.paths.raw_dir == (tmp_path / "data" / "books" / "book01" / "raw").resolve()
    assert s.paths.data_dir == (tmp_path / "data" / "books" / "book01").resolve()
    assert s.paths.eval_dir == (tmp_path / "eval" / "book01").resolve()
    assert s.paths.cache_dir == (tmp_path / "data" / "cache").resolve()  # dùng chung
    assert s.from_root(s.p2.sections.map).is_file()  # configs/books/book01/section_map.yaml
    assert s.from_root(s.p1.fix.glossary).is_file()
    assert s.root == tmp_path.resolve()


def test_book_selection_priority(tmp_path: Path) -> None:
    make_settings(tmp_path)
    _demo_book(tmp_path)
    env = {"OPENROUTER_API_KEY": "sk-or-x"}
    demo = load_settings(tmp_path, env=env, book="demo")
    assert (demo.project.book_id, demo.project.book_file) == ("demo", "demo.pdf")
    assert (demo.pilot.page_start, demo.pilot.page_end) == (10, 12)
    assert demo.paths.raw_dir == (tmp_path / "data" / "books" / "demo" / "raw").resolve()
    assert demo.fingerprint() != load_settings(tmp_path, env=env).fingerprint()
    # env chọn sách; tham số book (≈ dm --book) thắng env
    assert (
        load_settings(tmp_path, env={**env, "DM__PROJECT__BOOK_ID": "demo"}).project.book_id
        == "demo"
    )
    both = load_settings(tmp_path, env={**env, "DM__PROJECT__BOOK_ID": "demo"}, book="book01")
    assert both.project.book_id == "book01"
    assert load_settings(tmp_path, env=env).project.book_id == "book01"  # mặc định


def test_cli_book_option(tmp_path: Path) -> None:
    make_settings(tmp_path)
    _demo_book(tmp_path)
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    root = ["--root", str(tmp_path)]
    shown = runner.invoke(app, ["--book", "demo", "config", "show", *root])
    assert shown.exit_code == 0, shown.output
    assert "book_id: demo" in shown.output and "book_file: demo.pdf" in shown.output
    # lần gọi sau không có --book → về sách mặc định (không rò lựa chọn cũ)
    assert "book_id: book01" in runner.invoke(app, ["config", "show", *root]).output
    # lệnh chạy cho sách demo: tìm PDF trong data/books/demo/raw (dữ liệu riêng từng sách)
    toc = runner.invoke(app, ["--book", "demo", "p2", "toc", *root])
    assert toc.exit_code == 1
    assert str(Path("data") / "books" / "demo" / "raw" / "demo.pdf") in toc.output
    # không trạng thái ẩn: code ngoài CLI không thấy lựa chọn --book của lần gọi trước
    after = load_settings(tmp_path, env={"OPENROUTER_API_KEY": "sk-or-x"})
    assert after.project.book_id == "book01"
