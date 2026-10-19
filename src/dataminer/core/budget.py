"""Nhật ký chi phí và kiểm tra ngân sách LLM.

Mỗi lời gọi API thật (không tính cache hit) ghi một dòng vào `cost_log.jsonl`.
Tổng đã chi được tính lại từ log khi khởi tạo → ngân sách giữ qua nhiều lần chạy.
"""

import json
import threading
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from dataminer.core.config import BudgetCfg
from dataminer.core.llm_types import BudgetExceededError, Usage


class CostLedger:
    def __init__(self, path: Path, budget: BudgetCfg) -> None:
        self.path = path
        self.budget = budget
        self._lock = threading.Lock()
        self._by_task: dict[str, float] = defaultdict(float)
        self._by_model: dict[str, float] = defaultdict(float)
        self._calls = 0
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self._account(json.loads(line))

    def _account(self, entry: dict[str, Any]) -> None:
        cost = float(entry.get("cost_usd", 0.0))
        self._by_task[str(entry["task"])] += cost
        self._by_model[str(entry["model"])] += cost
        self._calls += 1

    @property
    def total(self) -> float:
        return sum(self._by_task.values())

    def spent(self, task: str) -> float:
        return self._by_task.get(task, 0.0)

    def check(self, task: str) -> None:
        """BudgetExceededError nếu tổng hoặc chi của tác vụ đã chạm ngân sách."""
        with self._lock:
            if self.total >= self.budget.total_usd:
                raise BudgetExceededError(
                    f"Đã chi ${self.total:.4f} ≥ ngân sách tổng ${self.budget.total_usd} "
                    "(budget.total_usd)."
                )
            limit = self.budget.per_task_usd.get(task)
            if limit is not None and self.spent(task) >= limit:
                raise BudgetExceededError(
                    f"Tác vụ '{task}' đã chi ${self.spent(task):.4f} ≥ ngân sách ${limit} "
                    f"(budget.per_task_usd.{task})."
                )

    def add(self, *, task: str, model: str, usage: Usage, latency_s: float, cache_key: str) -> None:
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "task": task,
            "model": model,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "reasoning_tokens": usage.reasoning_tokens,
            "cost_usd": usage.cost_usd,
            "cost_estimated": usage.cost_estimated,
            "latency_s": round(latency_s, 3),
            "cache_key": cache_key,
        }
        with self._lock:
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self._account(entry)

    def summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "calls": self._calls,
                "total_usd": self.total,
                "budget_total_usd": self.budget.total_usd,
                "by_task": dict(self._by_task),
                "by_model": dict(self._by_model),
                "per_task_limits": dict(self.budget.per_task_usd),
            }
