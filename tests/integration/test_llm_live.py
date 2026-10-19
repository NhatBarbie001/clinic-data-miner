"""P0.3 L1 - gọi OpenRouter THẬT (tốn tiền, cần OPENROUTER_API_KEY).

Mặc định bị bỏ qua. Chạy: `uv run pytest -m live`
Dùng cache riêng trong thư mục tạm → lần 1 luôn gọi thật, lần 2 phải là cache hit.
"""

import shutil
from pathlib import Path

import pytest
from pydantic import BaseModel

from dataminer.core.config import load_settings
from dataminer.core.llm_client import LLMClient

ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.live


class Answer(BaseModel):
    benh: str
    trieu_chung: list[str]


def test_live_ping_chat_and_json(tmp_path: Path) -> None:
    (tmp_path / "configs").mkdir()
    for name in ("default.yaml", "models.yaml"):
        shutil.copy(ROOT / "configs" / name, tmp_path / "configs" / name)
    real = load_settings(ROOT)  # lấy key từ .env thật
    settings = load_settings(tmp_path, env={"OPENROUTER_API_KEY": real.require_api_key()})
    client = LLMClient(settings)

    msg = [{"role": "user", "content": "Bệnh cúm có triệu chứng gì? Trả lời một câu."}]
    first = client.chat_sync("ping", msg)
    assert first.content.strip()
    assert first.cached is False
    assert first.usage.prompt_tokens > 0
    assert first.usage.cost_usd < 0.01

    second = client.chat_sync("ping", msg)
    assert second.cached is True
    assert second.usage.cost_usd == 0.0

    obj, resp = client.chat_json_sync(
        "ping",
        [{"role": "user", "content": "JSON: benh='cúm', trieu_chung = 3 triệu chứng."}],
        Answer,
    )
    assert obj.benh
    assert len(obj.trieu_chung) >= 1
    assert resp.usage.cost_usd < 0.01
