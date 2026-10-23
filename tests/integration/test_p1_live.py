"""P1.6 - chạy TRỌN P1 THẬT (DeepSeek) trên pilot sách mẫu, đánh giá G1-G9 (tốn ~$0.003).

Mặc định bị bỏ qua. Chạy: `uv run pytest -m live tests/integration/test_p1_live.py`
Dự án tạm + cache mới → luôn gọi API thật; chưa có quyết định duyệt → G8 phải đạt ở dạng
"giữ nguyên + gắn cờ" (chưa qua duyệt).
"""

import shutil
from pathlib import Path

import pytest

from dataminer.core.config import load_settings
from dataminer.devtools.sample_book import make_sample_book
from dataminer.evaluation.p1_eval import evaluate_p1
from dataminer.pipeline.p1 import p1_dir, run_p1

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.live


def test_live_full_p1_pilot(tmp_path: Path) -> None:
    for folder, names in (
        ("configs", ("default.yaml", "models.yaml", "glossary.yaml")),
        ("prompts", ("p1_fix_ocr.md",)),
    ):
        (tmp_path / folder).mkdir()
        for name in names:
            shutil.copy(ROOT / folder / name, tmp_path / folder / name)
    book = make_sample_book(tmp_path / "data" / "raw", seed=7)
    key = load_settings(ROOT).require_api_key()
    settings = load_settings(tmp_path, env={"OPENROUTER_API_KEY": key})

    result = run_p1(settings)
    assert result.counts["fixes_accepted"] > 20
    assert result.pending_review >= 2  # 2 số liệu chờ người duyệt
    assert 0 < result.llm_cost_usd < 0.05

    import json

    report = evaluate_p1(p1_dir(settings), json.loads(book.truth_path.read_text(encoding="utf-8")))
    failed = {g: v for g, v in report.items() if not v["pass"]}
    assert not failed, failed
