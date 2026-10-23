"""P1.4 - sửa lỗi OCR THẬT bằng DeepSeek trên pilot sách mẫu (tốn ~$0.003).

Mặc định bị bỏ qua. Chạy: `uv run pytest -m live tests/integration/test_p1_fix_live.py`
Dùng cache riêng trong thư mục tạm → luôn gọi API thật.
"""

import asyncio
import shutil
from pathlib import Path

import pytest

from dataminer.books.book01.rules import build_blocks
from dataminer.core.config import load_settings
from dataminer.devtools.sample_book import make_sample_book
from dataminer.evaluation.truth.p1_eval import eval_ocr
from dataminer.ocrfix.fixer import OCRFixer
from dataminer.pdf.furniture import strip_furniture
from dataminer.pdf.reader import body_font_size, read_lines

ROOT = Path(__file__).resolve().parents[2]

from tests.unit.llm_fakes import copy_configs  # noqa: E402

pytestmark = pytest.mark.live


def test_live_fix_pilot_meets_g5_to_g9(tmp_path: Path) -> None:
    copy_configs(tmp_path)
    (tmp_path / "prompts").mkdir()
    shutil.copy(ROOT / "prompts" / "p1_fix_ocr.md", tmp_path / "prompts" / "p1_fix_ocr.md")
    key = load_settings(ROOT).require_api_key()
    settings = load_settings(tmp_path, env={"OPENROUTER_API_KEY": key})
    book = make_sample_book(tmp_path / "book", seed=7)

    lines = read_lines(book.pdf_path, pages=(4, 9))
    body = body_font_size(lines)
    fr = strip_furniture(lines, body, pdf_pages=list(range(4, 10)))
    blocks = build_blocks(fr.content, body, printed={p.page: p.printed_page for p in fr.pages})
    fixed = asyncio.run(OCRFixer.from_settings(settings).fix(blocks, tmp_path / "progress.jsonl"))

    report = eval_ocr(fixed, fr.content, book.truth)
    failed = {g: v for g, v in report.items() if not v["pass"]}
    assert not failed, failed
