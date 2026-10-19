"""P0.2 - Cấu hình: nạp nhiều lớp, ghi đè, kiểm tra lỗi, che bí mật, fingerprint.

Mọi test (trừ #1) dùng thư mục tạm + `env` giả → không phụ thuộc .env/local.yaml trên máy.
Số thứ tự (#) khớp mục 6 của docs/phases/P0/P0.2_plan.md.
"""

import shutil
from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from dataminer.cli import app
from dataminer.core.config import (
    REQUIRED_TASKS,
    ConfigError,
    Settings,
    find_project_root,
    load_settings,
)

ROOT = Path(__file__).resolve().parents[2]
FAKE_KEY = "sk-or-test-SECRET-123456"
runner = CliRunner()


@pytest.fixture
def proj(tmp_path: Path) -> Path:
    """Dự án tạm với bản sao configs thật."""
    (tmp_path / "configs").mkdir()
    for name in ("default.yaml", "models.yaml"):
        shutil.copy(ROOT / "configs" / name, tmp_path / "configs" / name)
    return tmp_path


def write_yaml(path: Path, data: Any) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")


def edit_yaml(path: Path, change: dict[str, Any]) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for dotted, value in change.items():
        node = data
        *parents, last = dotted.split(".")
        for p in parents:
            node = node[p]
        if value is _DELETE:
            del node[last]
        else:
            node[last] = value
    write_yaml(path, data)


_DELETE = object()


def load_error(proj: Path, env: dict[str, str] | None = None) -> str:
    with pytest.raises(ConfigError) as info:
        load_settings(proj, env=env or {})
    return str(info.value)


# ---------------------------------------------------------------- 1-2: nạp cơ bản


def test_01_real_config_is_valid() -> None:
    s = load_settings(ROOT, env={})
    assert isinstance(s, Settings)
    assert set(REQUIRED_TASKS) <= set(s.models)
    assert s.model_for("ping").model.startswith("deepseek/")


def test_02_paths_resolved_absolute_relative_to_root(proj: Path) -> None:
    s = load_settings(proj, env={})
    assert s.paths.raw_dir == (proj / "data" / "raw").resolve()
    for value in s.paths.model_dump().values():
        assert Path(value).is_absolute()


# ---------------------------------------------------------------- 3-5: các lớp


def test_03_local_yaml_deep_merge(proj: Path) -> None:
    write_yaml(proj / "configs/local.yaml", {"llm": {"concurrency": 2}})
    s = load_settings(proj, env={})
    assert s.llm.concurrency == 2
    assert s.llm.base_url == "https://openrouter.ai/api/v1"  # khóa khác giữ nguyên
    assert s.llm.max_retries == 4
    assert "configs/local.yaml" in s.sources


def test_03b_local_yaml_overrides_nested_model(proj: Path) -> None:
    write_yaml(proj / "configs/local.yaml", {"models": {"extract": {"max_tokens": 100}}})
    s = load_settings(proj, env={})
    assert s.model_for("extract").max_tokens == 100
    assert s.model_for("extract").reasoning.enabled is True  # giữ từ models.yaml


def test_04_env_override_with_type_coercion(proj: Path) -> None:
    s = load_settings(proj, env={"DM__LLM__CONCURRENCY": "8", "DM__LLM__MODE": "replay"})
    assert s.llm.concurrency == 8
    assert isinstance(s.llm.concurrency, int)
    assert s.llm.mode == "replay"
    assert any(src.startswith("env:") for src in s.sources)


def test_05_priority_env_over_local_over_default(proj: Path) -> None:
    write_yaml(proj / "configs/local.yaml", {"llm": {"concurrency": 2, "max_retries": 7}})
    s = load_settings(proj, env={"DM__LLM__CONCURRENCY": "9"})
    assert s.llm.concurrency == 9  # env thắng local
    assert s.llm.max_retries == 7  # local thắng default
    assert s.llm.timeout_s == 120  # default


def test_05b_unrelated_env_vars_ignored(proj: Path) -> None:
    s = load_settings(proj, env={"PATH": "/usr/bin", "LLM_MODE": "replay"})
    assert s.llm.mode == "live"


# ---------------------------------------------------------------- 6-9: lỗi


def test_06_typo_key_suggests_correct_name(proj: Path) -> None:
    write_yaml(proj / "configs/local.yaml", {"llm": {"concurency": 2}})
    msg = load_error(proj)
    assert "llm.concurency" in msg
    assert "khóa không tồn tại" in msg
    assert "'concurrency'" in msg
    assert "configs/local.yaml" in msg


def test_06b_typo_in_env_reports_env_source(proj: Path) -> None:
    msg = load_error(proj, env={"DM__LLM__TIMEOUT": "5"})
    assert "llm.timeout" in msg
    assert "'timeout_s'" in msg
    assert "[nguồn: env]" in msg


@pytest.mark.parametrize(
    ("change", "expect"),
    [
        ({"llm.concurrency": 100}, "llm.concurrency: phải ≤ 64"),
        ({"llm.concurrency": 0}, "llm.concurrency: phải ≥ 1"),
        ({"budget.total_usd": -1}, "budget.total_usd: phải ≥ 0"),
        ({"llm.mode": "fast"}, "llm.mode: phải là một trong"),
        ({"project.book_id": "Sách 1"}, "project.book_id: không khớp mẫu"),
        ({"pilot.page_start": 50, "pilot.page_end": 10}, "page_start (50) phải ≤ page_end (10)"),
        ({"pilot.page_start": 5}, "cùng có hoặc cùng để trống"),
        ({"llm.base_url": _DELETE}, "llm.base_url: thiếu giá trị bắt buộc"),
    ],
)
def test_07_out_of_range_values(proj: Path, change: dict[str, Any], expect: str) -> None:
    edit_yaml(proj / "configs/default.yaml", change)
    assert expect in load_error(proj)


def test_07b_multiple_errors_reported_together(proj: Path) -> None:
    edit_yaml(proj / "configs/default.yaml", {"llm.concurrency": 100, "budget.total_usd": -5})
    msg = load_error(proj)
    assert "(2 lỗi)" in msg
    assert "llm.concurrency" in msg
    assert "budget.total_usd" in msg


def test_07c_group_error_blames_latest_layer(proj: Path) -> None:
    """Lỗi cấp nhóm (pilot) phải chỉ vào lớp vừa làm sai, không phải default.yaml."""
    write_yaml(proj / "configs/local.yaml", {"pilot": {"page_start": 50, "page_end": 10}})
    msg = load_error(proj)
    assert "pilot: page_start (50) phải ≤ page_end (10)" in msg
    assert "[nguồn: configs/local.yaml]" in msg


def test_07d_messages_in_vietnamese(proj: Path) -> None:
    write_yaml(
        proj / "configs/local.yaml",
        {"llm": {"mode": "fast"}, "models": {"extract": {"model": ""}}},
    )
    msg = load_error(proj)
    assert "models.extract.model: không được để trống" in msg
    assert "'live', 'replay', 'refresh'" in msg
    assert " or " not in msg


def test_08_missing_required_task(proj: Path) -> None:
    edit_yaml(proj / "configs/models.yaml", {"judge": _DELETE})
    msg = load_error(proj)
    assert "thiếu tác vụ bắt buộc: judge" in msg


def test_08b_budget_for_unknown_task(proj: Path) -> None:
    edit_yaml(proj / "configs/default.yaml", {"budget.per_task_usd": {"khong_co": 1.0}})
    assert "khong_co" in load_error(proj)


def test_09_model_for_unknown_task_lists_valid(proj: Path) -> None:
    s = load_settings(proj, env={})
    with pytest.raises(ConfigError) as info:
        s.model_for("khong_co")
    assert "extract" in str(info.value)


# ---------------------------------------------------------------- 10-11: API key


def test_10_missing_api_key_loads_but_require_fails(proj: Path) -> None:
    s = load_settings(proj, env={})
    assert s.llm.api_key is None
    with pytest.raises(ConfigError) as info:
        s.require_api_key()
    assert ".env" in str(info.value)


def test_10b_api_key_from_env(proj: Path) -> None:
    s = load_settings(proj, env={"OPENROUTER_API_KEY": FAKE_KEY})
    assert s.require_api_key() == FAKE_KEY


def test_10c_api_key_from_dotenv_file(proj: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    (proj / ".env").write_text(f"OPENROUTER_API_KEY={FAKE_KEY}\n", encoding="utf-8")
    s = load_settings(proj)  # env=None → đọc .env + os.environ
    assert s.require_api_key() == FAKE_KEY


def test_11_api_key_never_displayed(proj: Path) -> None:
    s = load_settings(proj, env={"OPENROUTER_API_KEY": FAKE_KEY})
    assert FAKE_KEY not in str(s.to_display_dict())
    assert FAKE_KEY not in repr(s)
    assert FAKE_KEY not in str(s)
    assert s.to_display_dict()["llm"]["api_key"] == "***(đã đặt)"


def test_11b_api_key_not_in_cli_show(proj: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", FAKE_KEY)
    result = runner.invoke(app, ["config", "show", "--root", str(proj)])
    assert result.exit_code == 0, result.output
    assert FAKE_KEY not in result.output
    assert "***(đã đặt)" in result.output


# ---------------------------------------------------------------- 12: fingerprint


def test_12_fingerprint_stable(proj: Path) -> None:
    a = load_settings(proj, env={}).fingerprint()
    b = load_settings(proj, env={}).fingerprint()
    assert a == b
    assert len(a) == 12


def test_12b_fingerprint_changes_with_params(proj: Path) -> None:
    a = load_settings(proj, env={}).fingerprint()
    b = load_settings(proj, env={"DM__LLM__CONCURRENCY": "8"}).fingerprint()
    assert a != b


def test_12c_fingerprint_ignores_api_key(proj: Path) -> None:
    a = load_settings(proj, env={}).fingerprint()
    b = load_settings(proj, env={"OPENROUTER_API_KEY": FAKE_KEY}).fingerprint()
    assert a == b


def test_12d_fingerprint_independent_of_location(proj: Path, tmp_path_factory: Any) -> None:
    other = tmp_path_factory.mktemp("other")
    shutil.copytree(proj / "configs", other / "configs")
    assert load_settings(proj, env={}).fingerprint() == load_settings(other, env={}).fingerprint()


# ---------------------------------------------------------------- 13: YAML hỏng


def test_13_broken_yaml_reports_file_and_line(proj: Path) -> None:
    (proj / "configs/local.yaml").write_text("llm:\n  concurrency: [1, 2\n", encoding="utf-8")
    msg = load_error(proj)
    assert "local.yaml" in msg
    assert "dòng" in msg


def test_13b_missing_required_file(proj: Path) -> None:
    (proj / "configs/models.yaml").unlink()
    assert "models.yaml" in load_error(proj)


def test_13c_non_mapping_root(proj: Path) -> None:
    (proj / "configs/local.yaml").write_text("- a\n- b\n", encoding="utf-8")
    assert "mapping" in load_error(proj)


# ---------------------------------------------------------------- 14: CLI


def test_14_cli_validate_ok(proj: Path) -> None:
    result = runner.invoke(app, ["config", "validate", "--root", str(proj)])
    assert result.exit_code == 0, result.output
    assert "hợp lệ" in result.output


def test_14b_cli_validate_fails_with_errors(proj: Path) -> None:
    write_yaml(proj / "configs/local.yaml", {"llm": {"concurrency": 100}})
    result = runner.invoke(app, ["config", "validate", "--root", str(proj)])
    assert result.exit_code == 1
    assert "llm.concurrency" in result.output


def test_14c_cli_show_lists_sources_and_fingerprint(proj: Path) -> None:
    result = runner.invoke(app, ["config", "show", "--root", str(proj)])
    assert result.exit_code == 0, result.output
    assert "# fingerprint:" in result.output
    assert "configs/default.yaml" in result.output
    data = yaml.safe_load(result.output)
    assert data["llm"]["concurrency"] == 4


# ---------------------------------------------------------------- tiện ích


def test_find_project_root_moved_to_core() -> None:
    assert find_project_root(ROOT / "src") == ROOT
