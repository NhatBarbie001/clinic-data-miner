"""Công cụ giả lập OpenRouter cho test LLM client (không gọi mạng)."""

import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx

from dataminer.core.config import Settings, load_settings
from dataminer.core.llm_client import LLMClient

ROOT = Path(__file__).resolve().parents[2]
FAKE_KEY = "sk-or-test-key"
MODEL = "deepseek/deepseek-v4.1-flash-1017"

Handler = Callable[[httpx.Request], Any]


def copy_configs(root: Path) -> None:
    """Chép cấu hình thật vào dự án tạm: default.yaml, models.yaml và mọi hồ sơ sách
    (configs/books/<sách>/: book.yaml, từ điển tên mục, thuật ngữ…). Không chép local.yaml."""
    (root / "configs").mkdir(parents=True, exist_ok=True)
    for name in ("default.yaml", "models.yaml"):
        shutil.copy(ROOT / "configs" / name, root / "configs" / name)
    shutil.copytree(ROOT / "configs" / "books", root / "configs" / "books", dirs_exist_ok=True)


def make_settings(root: Path, **env: str) -> Settings:
    """Dự án tạm với configs thật; cache/ledger nằm trong `root/data/cache`."""
    if not (root / "configs").exists():
        copy_configs(root)
    base = {"OPENROUTER_API_KEY": FAKE_KEY}
    base.update({k: v for k, v in env.items()})
    return load_settings(root, env=base)


def body(
    content: str = "Sốt, ho, đau mỏi người.",
    *,
    model: str = MODEL,
    cost: float | None = 0.0001,
    finish: str = "stop",
    reasoning: str | None = None,
    reasoning_details: list[Any] | None = None,
    prompt_tokens: int = 20,
    completion_tokens: int = 10,
    reasoning_tokens: int = 0,
) -> dict[str, Any]:
    usage: dict[str, Any] = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "completion_tokens_details": {"reasoning_tokens": reasoning_tokens},
    }
    if cost is not None:
        usage["cost"] = cost
    message: dict[str, Any] = {"role": "assistant", "content": content}
    if reasoning is not None:
        message["reasoning"] = reasoning
    if reasoning_details is not None:
        message["reasoning_details"] = reasoning_details
    return {
        "id": "gen-1",
        "model": model,
        "provider": "DeepSeek",
        "choices": [{"index": 0, "message": message, "finish_reason": finish}],
        "usage": usage,
    }


def ok(content: str = "Sốt, ho, đau mỏi người.", **kwargs: Any) -> httpx.Response:
    return httpx.Response(200, json=body(content, **kwargs))


def status(
    code: int, message: str = "lỗi", headers: dict[str, str] | None = None
) -> httpx.Response:
    return httpx.Response(code, json={"error": {"message": message}}, headers=headers)


def raise_timeout(request: httpx.Request) -> httpx.Response:
    raise httpx.ReadTimeout("hết thời gian chờ", request=request)


def raise_connect(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("mất kết nối", request=request)


class Script:
    """Trả lần lượt các phản hồi đã định; hết danh sách thì lặp lại phản hồi cuối.

    Mỗi phần tử: httpx.Response, hoặc hàm(request) → Response (có thể raise).
    """

    def __init__(self, *items: httpx.Response | Handler) -> None:
        self.items = list(items)
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        item = self.items.pop(0) if len(self.items) > 1 else self.items[0]
        if isinstance(item, httpx.Response):
            return item
        result: httpx.Response = item(request)
        return result

    @property
    def calls(self) -> int:
        return len(self.requests)

    def payload(self, index: int = -1) -> dict[str, Any]:
        data: dict[str, Any] = json.loads(self.requests[index].content)
        return data


class SleepRecorder:
    """Thay asyncio.sleep: ghi lại thời gian chờ, không ngủ thật."""

    def __init__(self) -> None:
        self.delays: list[float] = []

    async def __call__(self, delay: float) -> None:
        self.delays.append(delay)


def make_client(
    root: Path, script: Script | Handler, **env: str
) -> tuple[LLMClient, SleepRecorder]:
    sleep = SleepRecorder()
    client = LLMClient(
        make_settings(root, **env), transport=httpx.MockTransport(script), sleep=sleep
    )
    return client, sleep
