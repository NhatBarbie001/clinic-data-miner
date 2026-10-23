"""Ghi manifest + log cho một lần chạy phase (N8).

    with RunRecorder(settings, phase="p1_clean") as run:
        run.use_prompt("p1_fix_ocr", "v1")
        run.add_input(pdf_path)
        n = write_jsonl(out_path, records)
        run.add_output(out_path)
        run.count("blocks", n)

Kết quả trong `data/<phase>/`:
    runs/<run_id>.json   manifest của lần chạy (giữ toàn bộ lịch sử)
    runs/<run_id>.log    log chi tiết của lần chạy
    manifest.json        bản sao manifest của lần chạy GẦN NHẤT
"""

import logging
import secrets
import subprocess
import time
from datetime import datetime
from pathlib import Path
from types import TracebackType

from dataminer.core.budget import CostLedger
from dataminer.core.config import Settings
from dataminer.core.io import file_info, write_json
from dataminer.core.llm_client import LEDGER_FILE
from dataminer.core.logging import add_file_handler, remove_handler
from dataminer.core.schemas import LLMUsage, RunManifest

log = logging.getLogger("dataminer.run")


def _git(root: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def project_root(settings: Settings) -> Path:
    """Gốc dự án (ghi nhớ lúc nạp cấu hình) - KHÔNG suy từ data_dir: mỗi sách có thư mục dữ
    liệu riêng (data/books/<sách>/)."""
    return settings.root


class RunRecorder:
    def __init__(self, settings: Settings, phase: str, *, out_dir: Path | None = None) -> None:
        self.settings = settings
        self.phase = phase
        self.root = project_root(settings)
        self.out_dir = out_dir or settings.paths.data_dir / phase
        now = datetime.now()
        stamp = now.strftime("%Y%m%d-%H%M%S-") + f"{now.microsecond // 1000:03d}"
        self.run_id = f"{phase}_{stamp}_{secrets.token_hex(2)}"
        self.runs_dir = self.out_dir / "runs"
        self.manifest_path = self.runs_dir / f"{self.run_id}.json"
        self.log_path = self.runs_dir / f"{self.run_id}.log"
        self._ledger_path = settings.paths.cache_dir / LEDGER_FILE
        self._start = 0.0
        self._ledger_start = (0, 0.0)
        self._handler: logging.Handler | None = None

        dirty = _git(self.root, "status", "--porcelain")
        self.manifest = RunManifest(
            run_id=self.run_id,
            phase=phase,
            started_at=now.astimezone().isoformat(timespec="milliseconds"),
            git_commit=_git(self.root, "rev-parse", "HEAD"),
            git_dirty=None if dirty is None else bool(dirty),
            config_fingerprint=settings.fingerprint(),
            models={task: spec.model for task, spec in settings.models.items()},
        )

    # ------------------------------------------------------------- ghi nhận

    def use_prompt(self, prompt_id: str, version: str) -> None:
        self.manifest.prompts[prompt_id] = version

    def add_input(self, path: Path, *, records: bool = True) -> None:
        self.manifest.inputs.append(file_info(path, self.root, records=records))

    def add_output(self, path: Path, *, records: bool = True) -> None:
        self.manifest.outputs.append(file_info(path, self.root, records=records))

    def count(self, name: str, value: int) -> None:
        self.manifest.counts[name] = value

    def note(self, text: str) -> None:
        self.manifest.notes.append(text)
        log.info("ghi chú: %s", text)

    # ------------------------------------------------------------- vòng đời

    def _ledger_totals(self) -> tuple[int, float]:
        """(số lời gọi, tổng chi phí) hiện có trong sổ chi phí LLM (P0.3)."""
        summary = CostLedger(self._ledger_path, self.settings.budget).summary()
        return int(summary["calls"]), float(summary["total_usd"])

    def _save(self) -> None:
        write_json(self.manifest_path, self.manifest)
        write_json(self.out_dir / "manifest.json", self.manifest)

    def __enter__(self) -> "RunRecorder":
        # started_at và duration_s cùng tính từ đây (không tính thời gian chạy git lúc khởi tạo).
        self.manifest.started_at = datetime.now().astimezone().isoformat(timespec="milliseconds")
        self._start = time.perf_counter()
        self._ledger_start = self._ledger_totals()
        self._handler = add_file_handler(self.log_path)
        log.info("bắt đầu %s (config %s)", self.run_id, self.manifest.config_fingerprint)
        self._save()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        calls, cost = self._ledger_totals()
        self.manifest.llm = LLMUsage(
            calls=calls - self._ledger_start[0],
            cost_usd=round(cost - self._ledger_start[1], 8),
        )
        self.manifest.finished_at = datetime.now().astimezone().isoformat(timespec="milliseconds")
        self.manifest.duration_s = round(time.perf_counter() - self._start, 3)
        if exc is None:
            self.manifest.status = "success"
            log.info("xong %s sau %.2fs", self.run_id, self.manifest.duration_s)
        else:
            self.manifest.status = "failed"
            self.manifest.error = f"{type(exc).__name__}: {exc}"
            log.error("THẤT BẠI %s: %s", self.run_id, self.manifest.error)
        self._save()
        if self._handler is not None:
            remove_handler(self._handler)
            self._handler = None
        # Không nuốt exception: trả None → exception (nếu có) được ném tiếp.
