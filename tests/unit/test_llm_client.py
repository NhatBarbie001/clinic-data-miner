"""P0.3 - LLM client với HTTP giả lập. Số (#) khớp mục 6 của docs/phases/P0/P0.3_plan.md."""

import asyncio
import json
from pathlib import Path
from typing import Any

import httpx
import pytest
from pydantic import BaseModel, Field

from dataminer.core.config import ConfigError, ReasoningCfg
from dataminer.core.llm_client import LLMClient
from dataminer.core.llm_types import (
    BudgetExceededError,
    CacheMissError,
    LLMError,
    LLMJSONError,
)
from tests.unit.llm_fakes import (
    FAKE_KEY,
    MODEL,
    Script,
    SleepRecorder,
    make_client,
    make_settings,
    ok,
    raise_connect,
    raise_timeout,
    status,
)

MSG = [{"role": "user", "content": "Triệu chứng cúm?"}]


class Disease(BaseModel):
    benh: str = Field(min_length=1)
    trieu_chung: list[str] = Field(min_length=1)


DISEASE_JSON = '{"benh": "cúm", "trieu_chung": ["sốt", "ho"]}'


# ---------------------------------------------------------------- 1-2 payload & parse


def test_01_payload_and_headers(tmp_path: Path) -> None:
    script = Script(ok())
    client, _ = make_client(tmp_path, script)
    client.chat_sync("ping", MSG)
    p = script.payload()
    assert p["model"] == MODEL
    assert p["messages"] == MSG
    assert p["temperature"] == 0.0
    assert p["max_tokens"] == 256  # từ models.yaml (ping)
    assert p["usage"] == {"include": True}
    # ping không bật reasoning → phải gửi rõ enabled=false (DeepSeek tự suy luận nếu không tắt)
    assert p["reasoning"] == {"enabled": False}
    req = script.requests[0]
    assert req.headers["Authorization"] == f"Bearer {FAKE_KEY}"
    assert str(req.url) == "https://openrouter.ai/api/v1/chat/completions"


def test_01b_reasoning_enabled_from_spec_and_override(tmp_path: Path) -> None:
    script = Script(ok())
    client, _ = make_client(tmp_path, script)
    client.chat_sync("extract", MSG)  # extract bật reasoning trong models.yaml
    assert script.payload()["reasoning"] == {"enabled": True}
    client.chat_sync("ping", MSG, reasoning=ReasoningCfg(enabled=True, effort="low"))
    assert script.payload()["reasoning"] == {"enabled": True, "effort": "low"}


def test_02_parse_response_fields(tmp_path: Path) -> None:
    details = [{"type": "reasoning.text", "text": "nghĩ..."}]
    script = Script(
        ok(
            "Sốt và ho.",
            reasoning="Suy luận",
            reasoning_details=details,
            cost=0.00042,
            prompt_tokens=100,
            completion_tokens=50,
            reasoning_tokens=30,
        )
    )
    client, _ = make_client(tmp_path, script)
    r = client.chat_sync("ping", MSG)
    assert r.content == "Sốt và ho."
    assert r.reasoning == "Suy luận"
    assert r.reasoning_details == details
    assert r.model == MODEL
    assert r.provider == "DeepSeek"
    assert r.finish_reason == "stop"
    assert (r.usage.prompt_tokens, r.usage.completion_tokens, r.usage.reasoning_tokens) == (
        100,
        50,
        30,
    )
    assert r.usage.cost_usd == pytest.approx(0.00042)
    assert r.usage.cost_estimated is False
    assert r.cached is False
    assert r.attempts == 1
    assert r.as_assistant_message() == {
        "role": "assistant",
        "content": "Sốt và ho.",
        "reasoning_details": details,
    }


# ---------------------------------------------------------------- 3-6 cache & mode


def test_03_cache_hit_skips_http_and_costs_nothing(tmp_path: Path) -> None:
    script = Script(ok())
    client, _ = make_client(tmp_path, script)
    first = client.chat_sync("ping", MSG)
    second = client.chat_sync("ping", MSG)
    assert script.calls == 1
    assert second.cached is True
    assert second.usage.cost_usd == 0.0
    assert second.content == first.content
    assert client.ledger.summary()["calls"] == 1


def test_03b_cache_ignores_task_name(tmp_path: Path) -> None:
    """Cùng payload (model, messages, tham số) → cùng key, dù khác tên tác vụ."""
    script = Script(ok())
    client, _ = make_client(tmp_path, script)
    client.chat_sync("ping", MSG, max_tokens=100)
    r = client.chat_sync("classify", MSG, max_tokens=100)  # classify: cùng model, temp 0
    assert r.cached is True
    assert script.calls == 1


def test_04_variant_or_params_change_key(tmp_path: Path) -> None:
    script = Script(ok())
    client, _ = make_client(tmp_path, script)
    client.chat_sync("ping", MSG)
    client.chat_sync("ping", MSG, variant=1)
    client.chat_sync("ping", MSG, temperature=0.5)
    client.chat_sync("ping", [{"role": "user", "content": "Câu khác"}])
    assert script.calls == 4


def test_05_replay_uses_cache_and_fails_on_miss(tmp_path: Path) -> None:
    script = Script(ok())
    live, _ = make_client(tmp_path, script)
    live.chat_sync("ping", MSG)
    replay, _ = make_client(tmp_path, script, DM__LLM__MODE="replay")
    assert replay.chat_sync("ping", MSG).cached is True
    with pytest.raises(CacheMissError):
        replay.chat_sync("ping", [{"role": "user", "content": "chưa hỏi bao giờ"}])
    assert script.calls == 1


def test_06_refresh_always_calls_and_overwrites(tmp_path: Path) -> None:
    script = Script(ok("cũ"), ok("mới"))
    live, _ = make_client(tmp_path, script)
    live.chat_sync("ping", MSG)
    refresh, _ = make_client(tmp_path, script, DM__LLM__MODE="refresh")
    assert refresh.chat_sync("ping", MSG).content == "mới"
    live2, _ = make_client(tmp_path, script)
    assert live2.chat_sync("ping", MSG).content == "mới"  # cache đã bị ghi đè
    assert script.calls == 2


# ---------------------------------------------------------------- 7-12 retry & fallback


def test_07_retry_429_then_503_then_ok(tmp_path: Path) -> None:
    script = Script(status(429, "rate limit"), status(503, "quá tải"), ok())
    client, sleep = make_client(tmp_path, script)
    r = client.chat_sync("ping", MSG)
    assert r.attempts == 3
    assert script.calls == 3
    assert len(sleep.delays) == 2
    # backoff: base 1s * 2^n * jitter[0.5, 1]
    assert 0.5 <= sleep.delays[0] <= 1.0
    assert 1.0 <= sleep.delays[1] <= 2.0


def test_07b_retry_after_header_respected(tmp_path: Path) -> None:
    script = Script(status(429, headers={"Retry-After": "7"}), ok())
    client, sleep = make_client(tmp_path, script)
    client.chat_sync("ping", MSG)
    assert sleep.delays == [7.0]


def test_07c_backoff_capped(tmp_path: Path) -> None:
    script = Script(status(500), status(500), status(500), ok())
    client, sleep = make_client(tmp_path, script, DM__LLM__BACKOFF_MAX_S="1.5")
    client.chat_sync("ping", MSG)
    assert max(sleep.delays) <= 1.5


@pytest.mark.parametrize("failure", [raise_timeout, raise_connect])
def test_08_timeout_and_connection_errors_retried(tmp_path: Path, failure: Any) -> None:
    script = Script(failure, ok())
    client, _ = make_client(tmp_path, script)
    assert client.chat_sync("ping", MSG).attempts == 2


@pytest.mark.parametrize(
    "bad",
    [
        httpx.Response(200, json={"error": {"message": "provider lỗi"}}),
        httpx.Response(200, json={"choices": []}),
        httpx.Response(200, content=b"<html>gateway</html>"),
    ],
)
def test_09_200_with_error_body_retried(tmp_path: Path, bad: httpx.Response) -> None:
    script = Script(bad, ok())
    client, _ = make_client(tmp_path, script)
    assert client.chat_sync("ping", MSG).attempts == 2


@pytest.mark.parametrize(
    ("code", "hint"),
    [
        (400, "không hợp lệ"),
        (401, "OPENROUTER_API_KEY"),
        (402, "Hết credit"),
        (403, "từ chối"),
        (422, "HTTP 422"),
    ],
)
def test_10_fatal_errors_not_retried(tmp_path: Path, code: int, hint: str) -> None:
    script = Script(status(code, "chi tiết"))
    client, sleep = make_client(tmp_path, script)
    with pytest.raises(LLMError) as info:
        client.chat_sync("ping", MSG)
    assert hint in str(info.value)
    assert script.calls == 1
    assert sleep.delays == []


def _set_fallback(tmp_path: Path) -> None:
    models = tmp_path / "configs" / "models.yaml"
    text = models.read_text(encoding="utf-8").replace(
        "ping:\n  model: deepseek/deepseek-v4.1-flash-1017\n",
        "ping:\n  model: deepseek/deepseek-v4.1-flash-1017\n  fallbacks: [backup/model-b]\n",
    )
    models.write_text(text, encoding="utf-8")


def test_11_fallback_after_retries_exhausted(tmp_path: Path) -> None:
    make_settings(tmp_path)  # tạo configs
    _set_fallback(tmp_path)

    def handler(request: httpx.Request) -> httpx.Response:
        model = json.loads(request.content)["model"]
        return status(503) if model == MODEL else ok(model="backup/model-b")

    script = Script(handler)
    client, _ = make_client(tmp_path, script, DM__LLM__MAX_RETRIES="1")
    r = client.chat_sync("ping", MSG)
    assert r.model == "backup/model-b"
    assert r.attempts == 3  # 2 lần model chính + 1 lần dự phòng
    assert [json.loads(q.content)["model"] for q in script.requests] == [
        MODEL,
        MODEL,
        "backup/model-b",
    ]


def test_11b_404_goes_to_fallback_immediately(tmp_path: Path) -> None:
    make_settings(tmp_path)
    _set_fallback(tmp_path)
    script = Script(status(404, "no endpoints"), ok(model="backup/model-b"))
    client, sleep = make_client(tmp_path, script)
    r = client.chat_sync("ping", MSG)
    assert r.model == "backup/model-b"
    assert r.attempts == 2
    assert sleep.delays == []


def test_12_all_models_fail(tmp_path: Path) -> None:
    make_settings(tmp_path)
    _set_fallback(tmp_path)
    script = Script(status(503, "quá tải"))
    client, _ = make_client(tmp_path, script, DM__LLM__MAX_RETRIES="0")
    with pytest.raises(LLMError) as info:
        client.chat_sync("ping", MSG)
    msg = str(info.value)
    assert MODEL in msg
    assert "backup/model-b" in msg
    assert "503" in msg


# ---------------------------------------------------------------- 13-16 chat_json


def test_13_chat_json_valid(tmp_path: Path) -> None:
    script = Script(ok(DISEASE_JSON))
    client, _ = make_client(tmp_path, script)
    obj, resp = client.chat_json_sync("extract", MSG, Disease)
    assert obj == Disease(benh="cúm", trieu_chung=["sốt", "ho"])
    assert resp.content == DISEASE_JSON
    assert resp.attempts == 1
    rf = script.payload()["response_format"]
    assert rf["type"] == "json_schema"
    assert rf["json_schema"]["name"] == "Disease"
    assert "trieu_chung" in rf["json_schema"]["schema"]["properties"]


def test_13b_chat_json_strips_code_fence(tmp_path: Path) -> None:
    script = Script(ok(f"```json\n{DISEASE_JSON}\n```"))
    client, _ = make_client(tmp_path, script)
    obj, _ = client.chat_json_sync("extract", MSG, Disease)
    assert obj.benh == "cúm"


def test_14_chat_json_repairs_after_schema_error(tmp_path: Path) -> None:
    script = Script(ok('{"benh": "cúm", "trieu_chung": []}'), ok(DISEASE_JSON))
    client, _ = make_client(tmp_path, script)
    obj, _ = client.chat_json_sync("extract", MSG, Disease)
    assert obj.trieu_chung == ["sốt", "ho"]
    repair = script.payload(1)["messages"]
    assert repair[-2]["role"] == "assistant"
    assert "sai schema" in repair[-1]["content"]
    assert "trieu_chung" in repair[-1]["content"]


def test_15_chat_json_gives_up(tmp_path: Path) -> None:
    script = Script(ok("không phải json"))
    client, _ = make_client(tmp_path, script, DM__LLM__JSON_RETRIES="2")
    with pytest.raises(LLMJSONError) as info:
        client.chat_json_sync("extract", MSG, Disease)
    assert len(info.value.errors) == 3
    assert info.value.last_output == "không phải json"
    assert script.calls == 3


def test_16_chat_json_truncated_output(tmp_path: Path) -> None:
    script = Script(ok('{"benh": "cú', finish="length"))
    client, _ = make_client(tmp_path, script)
    with pytest.raises(LLMJSONError) as info:
        client.chat_json_sync("extract", MSG, Disease)
    assert "max_tokens" in str(info.value)
    assert script.calls == 1


# ---------------------------------------------------------------- 17-19 ngân sách & chi phí


def test_17_ledger_records_real_calls_only(tmp_path: Path) -> None:
    script = Script(ok(cost=0.002))
    client, _ = make_client(tmp_path, script)
    client.chat_sync("ping", MSG)
    client.chat_sync("ping", MSG)  # cache hit
    s = client.ledger.summary()
    assert s["calls"] == 1
    assert s["by_task"]["ping"] == pytest.approx(0.002)
    lines = (tmp_path / "data/cache/cost_log.jsonl").read_text(encoding="utf-8").splitlines()
    entry = json.loads(lines[0])
    assert entry["task"] == "ping"
    assert entry["model"] == MODEL
    assert entry["prompt_tokens"] == 20


def test_17b_task_budget_blocks_before_http(tmp_path: Path) -> None:
    script = Script(ok(cost=0.6))
    client, _ = make_client(tmp_path, script)  # ping: tối đa $1
    client.chat_sync("ping", MSG, variant=1)
    client.chat_sync("ping", MSG, variant=2)  # đã chi 0.6 < 1 → vẫn gọi
    with pytest.raises(BudgetExceededError) as info:
        client.chat_sync("ping", MSG, variant=3)  # đã chi 1.2 ≥ 1
    assert "ping" in str(info.value)
    assert script.calls == 2


def test_17c_total_budget(tmp_path: Path) -> None:
    script = Script(ok(cost=0.5))
    client, _ = make_client(tmp_path, script, DM__BUDGET__TOTAL_USD="0.4")
    client.chat_sync("classify", MSG)
    with pytest.raises(BudgetExceededError) as info:
        client.chat_sync("qa", MSG)
    assert "total_usd" in str(info.value)


def test_17d_cache_hit_allowed_when_over_budget(tmp_path: Path) -> None:
    script = Script(ok(cost=5.0))
    client, _ = make_client(tmp_path, script, DM__BUDGET__TOTAL_USD="1")
    client.chat_sync("classify", MSG)  # vượt ngân sách sau lời gọi này
    assert client.chat_sync("classify", MSG).cached is True  # vẫn đọc cache được


def test_18_budget_persists_across_runs(tmp_path: Path) -> None:
    script = Script(ok(cost=0.7))
    first, _ = make_client(tmp_path, script)
    first.chat_sync("ping", MSG, variant=1)
    first.chat_sync("ping", MSG, variant=2)
    second, _ = make_client(tmp_path, script)  # tiến trình mới
    assert second.ledger.spent("ping") == pytest.approx(1.4)
    with pytest.raises(BudgetExceededError):
        second.chat_sync("ping", MSG, variant=3)


def test_19_cost_estimated_from_pricing_when_missing(tmp_path: Path) -> None:
    make_settings(tmp_path)
    cache_dir = tmp_path / "data/cache"
    cache_dir.mkdir(parents=True)
    (cache_dir / "models.json").write_text(
        json.dumps(
            {
                "data": [
                    {"id": MODEL, "pricing": {"prompt": "0.00000015", "completion": "0.0000006"}}
                ]
            }
        ),
        encoding="utf-8",
    )
    script = Script(ok(cost=None, prompt_tokens=1000, completion_tokens=500))
    client, _ = make_client(tmp_path, script)
    r = client.chat_sync("ping", MSG)
    assert r.usage.cost_estimated is True
    assert r.usage.cost_usd == pytest.approx(1000 * 0.00000015 + 500 * 0.0000006)


# ---------------------------------------------------------------- 20-22


def test_20_concurrency_limit(tmp_path: Path) -> None:
    state = {"active": 0, "peak": 0}

    async def handler(request: httpx.Request) -> httpx.Response:
        state["active"] += 1
        state["peak"] = max(state["peak"], state["active"])
        await asyncio.sleep(0.01)
        state["active"] -= 1
        return ok()

    client = LLMClient(
        make_settings(tmp_path, DM__LLM__CONCURRENCY="2"),
        transport=httpx.MockTransport(handler),
        sleep=SleepRecorder(),
    )

    async def run() -> None:
        await asyncio.gather(*(client.chat("ping", MSG, variant=i) for i in range(10)))

    asyncio.run(run())
    assert state["peak"] == 2


def test_21_missing_key_live_vs_replay(tmp_path: Path) -> None:
    script = Script(ok())
    with_key, _ = make_client(tmp_path, script)
    with_key.chat_sync("ping", MSG)

    no_key = make_settings(tmp_path, OPENROUTER_API_KEY="")
    live = LLMClient(no_key, transport=httpx.MockTransport(script))
    with pytest.raises(ConfigError) as info:
        live.chat_sync("ping", [{"role": "user", "content": "câu mới"}])
    assert ".env" in str(info.value)

    replay = LLMClient(
        make_settings(tmp_path, OPENROUTER_API_KEY="", DM__LLM__MODE="replay"),
        transport=httpx.MockTransport(script),
    )
    assert replay.chat_sync("ping", MSG).cached is True  # không cần key
    assert script.calls == 1


def test_22_sync_wrappers_can_be_called_repeatedly(tmp_path: Path) -> None:
    """Mỗi lần *_sync tạo event loop mới - semaphore không được dính loop cũ."""
    script = Script(ok())
    client, _ = make_client(tmp_path, script)
    for i in range(3):
        client.chat_sync("ping", MSG, variant=i)
    assert script.calls == 3
