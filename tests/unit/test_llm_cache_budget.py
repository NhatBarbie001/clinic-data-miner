"""P0.3 - Cache SQLite, sổ chi phí, CLI `dm llm cost`."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dataminer.cli import app
from dataminer.core.budget import CostLedger
from dataminer.core.cache import LLMCache
from dataminer.core.config import BudgetCfg
from dataminer.core.llm_types import BudgetExceededError, Usage
from tests.unit.llm_fakes import make_settings

runner = CliRunner()


def test_cache_put_get_and_persist(tmp_path: Path) -> None:
    path = tmp_path / "c.sqlite"
    cache = LLMCache(path)
    assert cache.get("k") is None
    cache.put("k", "m", {"messages": ["xin chào"]}, {"data": {"text": "chào bạn"}})
    assert cache.get("k") == {"data": {"text": "chào bạn"}}
    cache.close()

    reopened = LLMCache(path)  # #22: đóng rồi mở lại vẫn còn
    assert reopened.get("k") == {"data": {"text": "chào bạn"}}
    stats = reopened.stats()
    assert stats["entries"] == 1
    assert stats["models"] == 1
    reopened.close()


def test_cache_overwrite(tmp_path: Path) -> None:
    cache = LLMCache(tmp_path / "c.sqlite")
    cache.put("k", "m", {}, {"v": 1})
    cache.put("k", "m", {}, {"v": 2})
    assert cache.get("k") == {"v": 2}
    assert cache.stats()["entries"] == 1


def _usage(cost: float) -> Usage:
    return Usage(prompt_tokens=10, completion_tokens=5, cost_usd=cost)


def test_ledger_check_and_reload(tmp_path: Path) -> None:
    path = tmp_path / "log.jsonl"
    budget = BudgetCfg(total_usd=1.0, per_task_usd={"ping": 0.1})
    ledger = CostLedger(path, budget)
    ledger.check("ping")
    ledger.add(task="ping", model="m", usage=_usage(0.1), latency_s=0.5, cache_key="k")
    with pytest.raises(BudgetExceededError):
        ledger.check("ping")
    ledger.check("qa")  # tác vụ khác, không có giới hạn riêng

    reloaded = CostLedger(path, budget)
    assert reloaded.spent("ping") == pytest.approx(0.1)
    assert reloaded.summary()["calls"] == 1


def test_cli_cost_summary(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    ledger = CostLedger(settings.paths.cache_dir / "cost_log.jsonl", settings.budget)
    ledger.add(task="ping", model="deepseek/x", usage=_usage(0.0012), latency_s=1, cache_key="a")
    ledger.add(task="extract", model="deepseek/x", usage=_usage(0.003), latency_s=1, cache_key="b")
    result = runner.invoke(app, ["llm", "cost", "--root", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "Số lời gọi API thật: 2" in result.output
    assert "$0.004200" in result.output
    assert "ping" in result.output
    assert "/ $1.0" in result.output  # giới hạn ping


def test_ledger_lines_are_valid_json(tmp_path: Path) -> None:
    path = tmp_path / "log.jsonl"
    ledger = CostLedger(path, BudgetCfg(total_usd=5))
    ledger.add(task="qa", model="m", usage=_usage(0.01), latency_s=1.23456, cache_key="k")
    entry = json.loads(path.read_text(encoding="utf-8").strip())
    assert entry["latency_s"] == 1.235
    assert set(entry) >= {"ts", "task", "model", "cost_usd", "cost_estimated", "cache_key"}
