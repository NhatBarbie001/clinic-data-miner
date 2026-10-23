"""Nhóm lệnh `dm llm`: kiểm tra model, ping thật, xem chi phí."""

import asyncio
import json
from pathlib import Path
from typing import Any

import typer
from pydantic import BaseModel, Field

from dataminer.cli._common import current_book
from dataminer.core.config import ConfigError, Settings, load_settings
from dataminer.core.llm_client import LLMClient
from dataminer.core.llm_types import LLMError, LLMResponse

llm_app = typer.Typer(help="LLM: kiểm tra model, ping, chi phí.", no_args_is_help=True)

RootOption = typer.Option(None, "--root", help="Gốc dự án.", show_default=False)
SaveOption = typer.Option(None, "--save", help="Ghi request/response ra file JSON.")

PING_CHAT = [
    {"role": "system", "content": "Bạn là trợ lý y khoa. Trả lời ngắn gọn bằng tiếng Việt."},
    {
        "role": "user",
        "content": "Kể tên 3 triệu chứng thường gặp của bệnh cúm, trả lời trong một câu.",
    },
]
PING_JSON = [
    {"role": "system", "content": "Bạn là trợ lý y khoa. Chỉ trả về JSON."},
    {
        "role": "user",
        "content": (
            "Trả về JSON gồm: `benh` = 'cúm', `trieu_chung` = danh sách 3 triệu chứng thường gặp "
            "(tiếng Việt), `muc_do_pho_bien` = một trong 'thấp', 'trung bình', 'cao'."
        ),
    },
]


class PingAnswer(BaseModel):
    """Schema cho lời gọi chat_json trong `dm llm ping`."""

    benh: str = Field(min_length=1)
    trieu_chung: list[str] = Field(min_length=1)
    muc_do_pho_bien: str


def _load(root: Path | None) -> Settings:
    try:
        return load_settings(root, book=current_book())
    except ConfigError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from None


def _per_million(price: Any) -> str:
    try:
        return f"${float(price) * 1_000_000:.3f}"
    except (TypeError, ValueError):
        return "?"


@llm_app.command("models")
def models_cmd(root: Path | None = RootOption) -> None:
    """Tải danh sách model OpenRouter; kiểm tra model của từng tác vụ (tồn tại, giá, tính năng)."""
    settings = _load(root)
    client = LLMClient(settings)
    try:
        data = asyncio.run(client.fetch_models())
    except Exception as exc:  # mạng / HTTP
        typer.echo(f"Không tải được danh sách model: {exc}", err=True)
        raise typer.Exit(1) from None
    catalog = {m["id"]: m for m in data.get("data", [])}
    typer.echo(f"OpenRouter: {len(catalog)} model. Đã lưu bảng giá vào cache_dir/models.json\n")
    typer.echo(f"{'tác vụ':<9} {'model':<36} {'tồn tại':<8} {'vào/1M':>8} {'ra/1M':>8}  ghi chú")
    missing = 0
    for task, spec in settings.models.items():
        info = catalog.get(spec.model)
        if info is None:
            missing += 1
            typer.echo(f"{task:<9} {spec.model:<36} {'KHÔNG':<8}")
            continue
        price = info.get("pricing") or {}
        params = set(info.get("supported_parameters") or [])
        notes = []
        notes.append("json ✓" if {"response_format", "structured_outputs"} & params else "json ✗")
        if spec.reasoning.enabled:
            notes.append("reasoning ✓" if "reasoning" in params else "reasoning ✗ (KHÔNG hỗ trợ)")
        if price.get("overrides"):
            notes.append("giá thay đổi theo giờ")
        typer.echo(
            f"{task:<9} {spec.model:<36} {'có':<8} {_per_million(price.get('prompt')):>8} "
            f"{_per_million(price.get('completion')):>8}  {', '.join(notes)}"
        )
    if missing:
        typer.echo(f"\n✗ {missing} tác vụ trỏ tới model không tồn tại - sửa configs/models.yaml")
        raise typer.Exit(1)
    typer.echo("\n✓ Mọi tác vụ trỏ tới model tồn tại.")


def _describe(label: str, resp: LLMResponse) -> list[str]:
    u = resp.usage
    return [
        f"[{label}] model={resp.model} provider={resp.provider} cached={resp.cached}",
        f"  tokens: vào={u.prompt_tokens} ra={u.completion_tokens} suy-luận={u.reasoning_tokens}",
        f"  chi phí: ${u.cost_usd:.6f}{' (ước tính)' if u.cost_estimated else ''}"
        f"  thời gian: {resp.latency_s:.2f}s  số lần gọi HTTP: {resp.attempts}"
        f"  finish={resp.finish_reason}",
    ]


@llm_app.command("ping")
def ping_cmd(
    root: Path | None = RootOption,
    save: Path | None = SaveOption,
) -> None:
    """Gọi thật 2 lần (chat tiếng Việt + chat_json). Chạy lại lần 2 phải là cache hit, $0."""
    settings = _load(root)
    client = LLMClient(settings)
    try:
        chat = client.chat_sync("ping", PING_CHAT)
        parsed, json_resp = client.chat_json_sync("ping", PING_JSON, PingAnswer)
    except (LLMError, ConfigError) as exc:
        typer.echo(f"✗ {exc}", err=True)
        raise typer.Exit(1) from None

    typer.echo("1) chat")
    typer.echo(f"  hỏi : {PING_CHAT[-1]['content']}")
    typer.echo(f"  đáp : {chat.content.strip()}")
    for line in _describe("chat", chat):
        typer.echo(line)
    typer.echo("\n2) chat_json (schema PingAnswer)")
    typer.echo(f"  object: {parsed.model_dump_json()}")
    for line in _describe("json", json_resp):
        typer.echo(line)
    total = chat.usage.cost_usd + json_resp.usage.cost_usd
    typer.echo(f"\nTổng chi phí lần chạy này: ${total:.6f}")

    if save is not None:
        record = {
            "chat": {"request": PING_CHAT, "response": chat.model_dump(mode="json")},
            "chat_json": {
                "request": PING_JSON,
                "schema": PingAnswer.model_json_schema(),
                "parsed": parsed.model_dump(mode="json"),
                "response": json_resp.model_dump(mode="json"),
            },
        }
        save.parent.mkdir(parents=True, exist_ok=True)
        save.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        typer.echo(f"Đã ghi {save}")


@llm_app.command("cost")
def cost_cmd(root: Path | None = RootOption) -> None:
    """Tổng chi phí theo tác vụ/model, ngân sách còn lại, thống kê cache."""
    settings = _load(root)
    client = LLMClient(settings)
    s = client.ledger.summary()
    typer.echo(f"Số lời gọi API thật: {s['calls']}")
    typer.echo(
        f"Tổng đã chi: ${s['total_usd']:.6f} / ngân sách ${s['budget_total_usd']} "
        f"(còn ${s['budget_total_usd'] - s['total_usd']:.4f})"
    )
    typer.echo("\nTheo tác vụ:")
    for task, spent in sorted(s["by_task"].items()):
        limit = s["per_task_limits"].get(task)
        limit_text = f" / ${limit}" if limit is not None else ""
        typer.echo(f"  - {task:<9} ${spent:.6f}{limit_text}")
    typer.echo("\nTheo model:")
    for model, spent in sorted(s["by_model"].items()):
        typer.echo(f"  - {model:<40} ${spent:.6f}")
    c = client.cache.stats()
    typer.echo(f"\nCache: {c['entries']} response, {c['size_kb']} KB")
