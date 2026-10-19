"""LLM client: cửa duy nhất để gọi OpenRouter.

    client = LLMClient(get_settings())
    resp = client.chat_sync("qa", [{"role": "user", "content": "..."}])
    obj, resp = client.chat_json_sync("extract", messages, DiseaseSchema)

Tính năng: cache SQLite (live/replay/refresh), retry + backoff, model dự phòng,
giới hạn đồng thời, ngân sách, chat_json có validate + tự yêu cầu sửa.
Xem docs/phases/P0/P0.3_plan.md.
"""

import asyncio
import hashlib
import json
import logging
import random
import re
import time
from collections.abc import Awaitable, Callable, Sequence
from pathlib import Path
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from dataminer.core.budget import CostLedger
from dataminer.core.cache import LLMCache
from dataminer.core.config import ReasoningCfg, Settings
from dataminer.core.llm_types import (
    CacheMissError,
    LLMError,
    LLMJSONError,
    LLMResponse,
    Usage,
)

log = logging.getLogger("dataminer.llm")

T = TypeVar("T", bound=BaseModel)
Message = dict[str, Any]
SleepFn = Callable[[float], Awaitable[None]]

CACHE_FILE = "llm_cache.sqlite"
LEDGER_FILE = "cost_log.jsonl"
MODELS_FILE = "models.json"

# Lỗi vĩnh viễn: không retry. 404 (model không tồn tại) → thử model dự phòng.
_FATAL_MESSAGES = {
    400: "Request không hợp lệ",
    401: "API key không hợp lệ hoặc đã bị thu hồi - kiểm tra OPENROUTER_API_KEY trong .env",
    402: "Hết credit OpenRouter - nạp thêm tại https://openrouter.ai/settings/credits",
    403: "Bị từ chối (kiểm duyệt nội dung hoặc không có quyền dùng model)",
    404: "Model không tồn tại hoặc không có nhà cung cấp khả dụng",
}
_FENCE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)


class _ModelUnavailableError(Exception):
    """Model hiện tại không dùng được (hết retry hoặc 404) → chuyển model dự phòng."""

    def __init__(self, message: str, attempts: int) -> None:
        super().__init__(message)
        self.attempts = attempts


def _error_text(resp: httpx.Response) -> str:
    try:
        body = resp.json()
        err = body.get("error", body)
        if isinstance(err, dict):
            return str(err.get("message", err))
        return str(err)
    except ValueError:
        return resp.text[:300]


def _strip_fences(text: str) -> str:
    match = _FENCE.match(text)
    return match.group(1) if match else text.strip()


def _load_pricing(path: Path) -> dict[str, tuple[float, float]]:
    """{model_id: (giá/token vào, giá/token ra)} từ models.json đã lưu bởi `dm llm models`."""
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    pricing: dict[str, tuple[float, float]] = {}
    for model in data.get("data", []):
        price = model.get("pricing") or {}
        try:
            pricing[model["id"]] = (float(price["prompt"]), float(price["completion"]))
        except (KeyError, TypeError, ValueError):
            continue
    return pricing


class LLMClient:
    def __init__(
        self,
        settings: Settings,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        cache: LLMCache | None = None,
        ledger: CostLedger | None = None,
        sleep: SleepFn | None = None,
    ) -> None:
        self.settings = settings
        self.cfg = settings.llm
        cache_dir = settings.paths.cache_dir
        self.cache = cache or LLMCache(cache_dir / CACHE_FILE)
        self.ledger = ledger or CostLedger(cache_dir / LEDGER_FILE, settings.budget)
        self._pricing = _load_pricing(cache_dir / MODELS_FILE)
        self._transport = transport
        self._sleep: SleepFn = sleep or asyncio.sleep
        # Semaphore gắn với event loop → mỗi loop một cái (hàm *_sync dùng asyncio.run).
        self._semaphores: dict[int, asyncio.Semaphore] = {}

    # ------------------------------------------------------------------ public

    async def chat(
        self,
        task: str,
        messages: Sequence[Message],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        reasoning: ReasoningCfg | None = None,
        response_format: dict[str, Any] | None = None,
        variant: int = 0,
    ) -> LLMResponse:
        """Gọi model của `task`. `variant` khác nhau → mục cache khác nhau (lấy nhiều mẫu)."""
        spec = self.settings.model_for(task)
        payload = self._payload(
            model=spec.model,
            messages=messages,
            temperature=spec.temperature if temperature is None else temperature,
            max_tokens=max_tokens or spec.max_tokens,
            reasoning=reasoning or spec.reasoning,
            response_format=response_format,
        )
        key = self._cache_key(payload, variant)
        mode = self.cfg.mode

        if mode in ("live", "replay"):
            hit = self.cache.get(key)
            if hit is not None:
                resp = self._parse(hit["data"], cached=True, latency=0.0, attempts=0, key=key)
                log.info("llm %-8s cache-hit model=%s", task, resp.model)
                return resp
            if mode == "replay":
                raise CacheMissError(
                    f"[replay] Chưa có trong cache: tác vụ '{task}', key {key[:12]}… "
                    "- chạy lại ở chế độ live để ghi cache."
                )

        self.ledger.check(task)
        api_key = self.settings.require_api_key()
        async with self._semaphore():
            start = time.perf_counter()
            data, model_used, attempts = await self._call_with_fallback(
                payload, [spec.model, *spec.fallbacks], api_key
            )
            latency = time.perf_counter() - start

        resp = self._parse(data, cached=False, latency=latency, attempts=attempts, key=key)
        self.ledger.add(
            task=task, model=resp.model, usage=resp.usage, latency_s=latency, cache_key=key
        )
        self.cache.put(key, model_used, payload, {"data": data})
        log.info(
            "llm %-8s model=%s in=%d out=%d reason=%d cost=$%.6f %.1fs attempts=%d",
            task,
            resp.model,
            resp.usage.prompt_tokens,
            resp.usage.completion_tokens,
            resp.usage.reasoning_tokens,
            resp.usage.cost_usd,
            latency,
            attempts,
        )
        if resp.finish_reason == "length":
            log.warning(
                "llm %s: output bị cắt (finish_reason=length) - cân nhắc tăng max_tokens", task
            )
        return resp

    async def chat_json(
        self,
        task: str,
        messages: Sequence[Message],
        schema: type[T],
        **kwargs: Any,
    ) -> tuple[T, LLMResponse]:
        """Như `chat` nhưng trả object đã validate theo `schema`; tự yêu cầu sửa khi sai."""
        response_format = {
            "type": "json_schema",
            "json_schema": {"name": schema.__name__, "schema": schema.model_json_schema()},
        }
        convo: list[Message] = list(messages)
        errors: list[str] = []
        resp: LLMResponse | None = None
        for _ in range(self.cfg.json_retries + 1):
            resp = await self.chat(task, convo, response_format=response_format, **kwargs)
            if resp.finish_reason == "length":
                limit = kwargs.get("max_tokens") or self.settings.model_for(task).max_tokens
                raise LLMJSONError(
                    f"[{task}] Output JSON bị cắt (finish_reason=length) - tăng max_tokens "
                    f"(hiện {limit}).",
                    resp.content,
                    [*errors, "finish_reason=length"],
                )
            try:
                return schema.model_validate(json.loads(_strip_fences(resp.content))), resp
            except json.JSONDecodeError as exc:
                error = f"không phải JSON hợp lệ ({exc.msg} ở vị trí {exc.pos})"
            except ValidationError as exc:
                parts = [
                    f"{'.'.join(str(p) for p in e['loc']) or '(gốc)'}: {e['msg']}"
                    for e in exc.errors()
                ]
                error = "sai schema - " + "; ".join(parts)
            errors.append(error)
            log.warning("llm %s: JSON lỗi (%s) - yêu cầu model sửa", task, error)
            convo = [
                *convo,
                resp.as_assistant_message(),
                {
                    "role": "user",
                    "content": (
                        f"JSON vừa trả về không hợp lệ: {error}.\n"
                        "Hãy trả lại DUY NHẤT một đối tượng JSON đúng schema, không kèm giải thích."
                    ),
                },
            ]
        assert resp is not None
        raise LLMJSONError(
            f"[{task}] Không nhận được JSON hợp lệ sau {len(errors)} lần: {errors[-1]}",
            resp.content,
            errors,
        )

    def chat_sync(self, task: str, messages: Sequence[Message], **kwargs: Any) -> LLMResponse:
        return asyncio.run(self.chat(task, messages, **kwargs))

    def chat_json_sync(
        self, task: str, messages: Sequence[Message], schema: type[T], **kwargs: Any
    ) -> tuple[T, LLMResponse]:
        return asyncio.run(self.chat_json(task, messages, schema, **kwargs))

    async def fetch_models(self) -> dict[str, Any]:
        """Tải danh sách model + giá từ OpenRouter (không cần key) và lưu vào cache_dir."""
        async with httpx.AsyncClient(
            transport=self._transport, timeout=self.cfg.timeout_s
        ) as client:
            resp = await client.get(f"{self.cfg.base_url}/models")
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        path = self.settings.paths.cache_dir / MODELS_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        self._pricing = _load_pricing(path)
        return data

    # ------------------------------------------------------------------ nội bộ

    def _semaphore(self) -> asyncio.Semaphore:
        loop_id = id(asyncio.get_running_loop())
        if loop_id not in self._semaphores:
            self._semaphores[loop_id] = asyncio.Semaphore(self.cfg.concurrency)
        return self._semaphores[loop_id]

    @staticmethod
    def _payload(
        *,
        model: str,
        messages: Sequence[Message],
        temperature: float,
        max_tokens: int,
        reasoning: ReasoningCfg,
        response_format: dict[str, Any] | None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": list(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "usage": {"include": True},  # yêu cầu OpenRouter trả usage.cost
        }
        # Luôn gửi rõ: một số model (vd. DeepSeek V4.1) TỰ suy luận nếu không được bảo tắt,
        # làm tăng ~2-3 lần token ra (đo thực tế ở P0.3).
        payload["reasoning"] = {"enabled": reasoning.enabled}
        if reasoning.enabled and reasoning.effort:
            payload["reasoning"]["effort"] = reasoning.effort
        if response_format is not None:
            payload["response_format"] = response_format
        return payload

    @staticmethod
    def _cache_key(payload: dict[str, Any], variant: int) -> str:
        semantic = {k: v for k, v in payload.items() if k != "usage"}
        canonical = json.dumps(
            {"payload": semantic, "variant": variant}, sort_keys=True, ensure_ascii=False
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _backoff(self, attempt: int, retry_after: str | None) -> float:
        if retry_after:
            try:
                return min(float(retry_after), self.cfg.backoff_max_s)
            except ValueError:
                pass
        delay = min(self.cfg.backoff_base_s * 2.0**attempt, self.cfg.backoff_max_s)
        return delay * random.uniform(0.5, 1.0)

    async def _call_with_fallback(
        self, payload: dict[str, Any], models: list[str], api_key: str
    ) -> tuple[dict[str, Any], str, int]:
        failures: list[str] = []
        total_attempts = 0
        for model in models:
            try:
                data, attempts = await self._call_model({**payload, "model": model}, api_key)
                return data, model, total_attempts + attempts
            except _ModelUnavailableError as exc:
                total_attempts += exc.attempts
                failures.append(f"{model}: {exc}")
                log.warning("llm: model %s không dùng được (%s)", model, exc)
        raise LLMError("Mọi model đều thất bại:\n  - " + "\n  - ".join(failures))

    async def _call_model(
        self, payload: dict[str, Any], api_key: str
    ) -> tuple[dict[str, Any], int]:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Title": "dataminer",
        }
        errors: list[str] = []
        async with httpx.AsyncClient(
            transport=self._transport, timeout=self.cfg.timeout_s
        ) as client:
            for attempt in range(self.cfg.max_retries + 1):
                retry_after: str | None = None
                try:
                    resp = await client.post(
                        f"{self.cfg.base_url}/chat/completions", json=payload, headers=headers
                    )
                except (httpx.TimeoutException, httpx.TransportError) as exc:
                    error = f"{type(exc).__name__}: {exc}"
                else:
                    status = resp.status_code
                    if status == 200:
                        try:
                            data: dict[str, Any] = resp.json()
                        except ValueError:
                            data = {"error": {"message": "response không phải JSON"}}
                        if data.get("choices") and "error" not in data:
                            return data, attempt + 1
                        error = f"200 nhưng lỗi: {data.get('error') or 'choices rỗng'}"
                    elif status == 404:
                        raise _ModelUnavailableError(
                            f"404 {_FATAL_MESSAGES[404]}: {_error_text(resp)}", attempt + 1
                        )
                    elif status in _FATAL_MESSAGES:
                        raise LLMError(
                            f"HTTP {status} - {_FATAL_MESSAGES[status]}: {_error_text(resp)}"
                        )
                    elif 400 <= status < 500 and status not in (408, 429):
                        raise LLMError(f"HTTP {status}: {_error_text(resp)}")
                    else:
                        error = f"HTTP {status}: {_error_text(resp)}"
                        retry_after = resp.headers.get("Retry-After")
                errors.append(error)
                if attempt < self.cfg.max_retries:
                    delay = self._backoff(attempt, retry_after)
                    log.warning(
                        "llm: lỗi tạm thời (%s) - thử lại sau %.1fs (%d/%d)",
                        error,
                        delay,
                        attempt + 1,
                        self.cfg.max_retries,
                    )
                    await self._sleep(delay)
        raise _ModelUnavailableError(
            f"hết {self.cfg.max_retries + 1} lần thử: {errors[-1]}", self.cfg.max_retries + 1
        )

    def _parse(
        self, data: dict[str, Any], *, cached: bool, latency: float, attempts: int, key: str
    ) -> LLMResponse:
        choice = data["choices"][0]
        message = choice.get("message") or {}
        raw_usage = data.get("usage") or {}
        details = raw_usage.get("completion_tokens_details") or {}
        prompt_tokens = int(raw_usage.get("prompt_tokens") or 0)
        completion_tokens = int(raw_usage.get("completion_tokens") or 0)
        model = str(data.get("model") or "")

        cost = raw_usage.get("cost")
        estimated = cost is None
        if cost is None:
            price_in, price_out = self._pricing.get(model, (0.0, 0.0))
            cost = prompt_tokens * price_in + completion_tokens * price_out

        usage = Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            reasoning_tokens=int(details.get("reasoning_tokens") or 0),
            cost_usd=0.0 if cached else float(cost),  # cache hit: không tốn tiền
            cost_estimated=estimated and not cached,
        )
        return LLMResponse(
            content=message.get("content") or "",
            reasoning=message.get("reasoning"),
            reasoning_details=message.get("reasoning_details"),
            model=model,
            provider=data.get("provider"),
            finish_reason=choice.get("finish_reason"),
            usage=usage,
            cached=cached,
            latency_s=latency,
            attempts=attempts,
            cache_key=key,
        )
