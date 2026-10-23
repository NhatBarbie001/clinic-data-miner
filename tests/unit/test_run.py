"""P0.4 - RunRecorder (manifest + log theo lần chạy), logging, CLI `dm runs`. #11-#18."""

import logging
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dataminer.cli import app
from dataminer.core.budget import CostLedger
from dataminer.core.io import read_json, write_jsonl
from dataminer.core.llm_types import Usage
from dataminer.core.logging import LOGGER_NAME, setup_logging
from dataminer.core.run import RunRecorder
from dataminer.core.schemas import BaseRecord, RunManifest
from tests.unit.llm_fakes import make_settings

runner = CliRunner()
log = logging.getLogger("dataminer.test")


class Rec(BaseRecord):
    text: str


@pytest.fixture(autouse=True)
def _restore_logger() -> Iterator[None]:
    """Mỗi test bắt đầu với logger `dataminer` sạch (setup_logging sửa trạng thái toàn cục)."""
    logger = logging.getLogger(LOGGER_NAME)
    saved = (list(logger.handlers), logger.level, logger.propagate)
    yield
    logger.handlers[:] = saved[0]
    logger.setLevel(saved[1])
    logger.propagate = saved[2]


def _git_init(root: Path) -> None:
    def git(*args: str) -> None:
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=root,
            check=True,
            capture_output=True,
        )

    git("init", "-q")
    git("add", "-A")
    git("commit", "-q", "-m", "init")


def _run_ok(root: Path) -> RunRecorder:
    settings = make_settings(root)
    src = root / "data" / "books" / "book01" / "raw" / "input.jsonl"
    write_jsonl(src, [Rec(id="a", text="vào")])
    out = settings.paths.data_dir / "p9_demo" / "out.jsonl"
    with RunRecorder(settings, phase="p9_demo") as run:
        run.use_prompt("p9_prompt", "v3")
        run.add_input(src)
        n = write_jsonl(out, [Rec(id=f"r{i}", text="ra") for i in range(3)])
        run.add_output(out)
        run.count("records", n)
        run.note("chạy thử")
        log.info("đang xử lý bản ghi")
    return run


# ---------------------------------------------------------------- 11-12


def test_11_success_manifest_complete(tmp_path: Path) -> None:
    make_settings(tmp_path)  # tạo configs trước khi init git
    _git_init(tmp_path)
    run = _run_ok(tmp_path)
    m = RunManifest.model_validate(read_json(run.manifest_path))
    assert m.status == "success"
    assert m.phase == "p9_demo"
    assert m.run_id.startswith("p9_demo_")
    assert m.finished_at is not None
    assert m.duration_s is not None
    assert m.duration_s >= 0
    assert m.git_commit is not None
    assert len(m.git_commit) == 40
    assert m.config_fingerprint == make_settings(tmp_path).fingerprint()
    assert m.models["extract"].startswith("deepseek/")
    assert m.prompts == {"p9_prompt": "v3"}
    assert m.inputs[0].path == "data/books/book01/raw/input.jsonl"
    assert m.inputs[0].records == 1
    assert m.outputs[0].path == "data/books/book01/p9_demo/out.jsonl"
    assert m.outputs[0].records == 3
    assert len(m.outputs[0].sha256) == 64
    assert m.counts == {"records": 3}
    assert m.notes == ["chạy thử"]
    assert m.error is None


def test_11b_duration_matches_timestamps(tmp_path: Path) -> None:
    """duration_s phải khớp finished_at - started_at (không lệch do thời gian chạy git)."""
    from datetime import datetime

    make_settings(tmp_path)
    _git_init(tmp_path)  # có git → khởi tạo mất thời gian gọi git
    m = _run_ok(tmp_path).manifest
    assert m.finished_at is not None
    assert m.duration_s is not None
    span = (
        datetime.fromisoformat(m.finished_at) - datetime.fromisoformat(m.started_at)
    ).total_seconds()
    assert abs(span - m.duration_s) < 0.02


def test_12_failure_recorded_and_reraised(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    with pytest.raises(ValueError, match="dữ liệu hỏng"), RunRecorder(settings, "p9_demo") as run:
        run.count("done", 2)
        raise ValueError("dữ liệu hỏng ở bản ghi 3")
    m = RunManifest.model_validate(read_json(run.manifest_path))
    assert m.status == "failed"
    assert m.error == "ValueError: dữ liệu hỏng ở bản ghi 3"
    assert m.counts == {"done": 2}  # giữ lại tiến độ đã có


def test_12b_manifest_written_as_running_on_enter(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    with RunRecorder(settings, "p9_demo") as run:
        during = read_json(run.manifest_path)
    assert during["status"] == "running"


# ---------------------------------------------------------------- 13: chi phí LLM


def test_13_llm_cost_is_delta_of_ledger(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    ledger_path = settings.paths.cache_dir / "cost_log.jsonl"
    old = CostLedger(ledger_path, settings.budget)
    old.add(task="ping", model="m", usage=Usage(cost_usd=0.5), latency_s=1, cache_key="old")
    with RunRecorder(settings, "p9_demo") as run:
        ledger = CostLedger(ledger_path, settings.budget)
        for i in range(2):
            ledger.add(
                task="qa", model="m", usage=Usage(cost_usd=0.01), latency_s=1, cache_key=str(i)
            )
    assert run.manifest.llm.calls == 2
    assert run.manifest.llm.cost_usd == pytest.approx(0.02)


# ---------------------------------------------------------------- 14-16: log, lịch sử


def test_14_run_log_file_and_handler_removed(tmp_path: Path) -> None:
    run = _run_ok(tmp_path)
    text = run.log_path.read_text(encoding="utf-8")
    assert "bắt đầu " + run.run_id in text
    assert "đang xử lý bản ghi" in text
    assert "ghi chú: chạy thử" in text
    assert "xong " + run.run_id in text

    log.info("sau khi lần chạy đã kết thúc")
    assert "sau khi lần chạy" not in run.log_path.read_text(encoding="utf-8")
    handlers = logging.getLogger(LOGGER_NAME).handlers
    assert not any(getattr(h, "baseFilename", "") == str(run.log_path) for h in handlers)


def _consoles() -> list[logging.Handler]:
    handlers = logging.getLogger(LOGGER_NAME).handlers
    return [h for h in handlers if getattr(h, "_dataminer_console", False)]


def test_15_setup_logging_idempotent() -> None:
    setup_logging("INFO")
    setup_logging("DEBUG")
    setup_logging("WARNING")
    consoles = _consoles()
    assert len(consoles) == 1  # không nhân đôi dù gọi nhiều lần
    assert consoles[0].level == logging.WARNING  # lần gọi cuối cập nhật mức


def test_15b_file_log_does_not_make_console_noisy(tmp_path: Path) -> None:
    setup_logging("WARNING")
    run = _run_ok(tmp_path)  # file handler ở mức DEBUG trong lúc chạy
    assert _consoles()[0].level == logging.WARNING
    assert "đang xử lý" in run.log_path.read_text(encoding="utf-8")


def test_16_latest_manifest_and_history(tmp_path: Path) -> None:
    first = _run_ok(tmp_path)
    second = _run_ok(tmp_path)
    assert first.run_id != second.run_id
    phase_dir = tmp_path / "data" / "books" / "book01" / "p9_demo"
    assert read_json(phase_dir / "manifest.json")["run_id"] == second.run_id
    assert len(list((phase_dir / "runs").glob("*.json"))) == 2
    assert len(list((phase_dir / "runs").glob("*.log"))) == 2


# ---------------------------------------------------------------- 17-18


def test_17_no_git_repository(tmp_path: Path) -> None:
    run = _run_ok(tmp_path)  # tmp_path không phải git repo
    assert run.manifest.git_commit is None
    assert run.manifest.git_dirty is None
    assert run.manifest.status == "success"


def test_18_cli_runs_list_and_show(tmp_path: Path) -> None:
    make_settings(tmp_path)
    empty = runner.invoke(app, ["runs", "list", "--root", str(tmp_path)])
    assert "Chưa có lần chạy nào" in empty.output

    run = _run_ok(tmp_path)
    listed = runner.invoke(app, ["runs", "list", "--root", str(tmp_path)])
    assert listed.exit_code == 0, listed.output
    assert run.run_id in listed.output
    assert "success" in listed.output

    by_phase = runner.invoke(app, ["runs", "show", "p9_demo", "--root", str(tmp_path)])
    assert by_phase.exit_code == 0
    assert run.run_id in by_phase.output
    by_id = runner.invoke(app, ["runs", "show", run.run_id, "--root", str(tmp_path)])
    assert by_id.exit_code == 0
    assert '"status": "success"' in by_id.output
    missing = runner.invoke(app, ["runs", "show", "khong_co", "--root", str(tmp_path)])
    assert missing.exit_code == 1
