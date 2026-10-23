"""P0.1 - Kiểm tra khung dự án: package, module, CLI, thư mục, gitignore."""

import importlib
import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
from typer.testing import CliRunner

import dataminer
from dataminer.cli import REQUIRED_DIRS, app, find_project_root

ROOT = Path(__file__).resolve().parents[2]
runner = CliRunner()


def test_version_matches_pyproject() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert dataminer.__version__ == pyproject["project"]["version"]


@pytest.mark.parametrize("name", dataminer.SUBMODULES)
def test_submodule_importable_and_documented(name: str) -> None:
    module = importlib.import_module(f"dataminer.{name}")
    assert module.__doc__, f"dataminer.{name} cần docstring mô tả vai trò"


def test_submodules_match_source_tree() -> None:
    on_disk = {
        p.name for p in (ROOT / "src" / "dataminer").iterdir() if (p / "__init__.py").is_file()
    }
    assert on_disk == set(dataminer.SUBMODULES)


@pytest.mark.parametrize("rel", REQUIRED_DIRS)
def test_required_dir_exists(rel: str) -> None:
    assert (ROOT / rel).is_dir(), f"Thiếu thư mục {rel}"


def test_find_project_root_from_subdir() -> None:
    assert find_project_root(ROOT / "src" / "dataminer") == ROOT


def test_find_project_root_fails_outside_project(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        find_project_root(tmp_path)


def test_cli_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output.strip() == f"dataminer {dataminer.__version__}"


def test_cli_info(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(ROOT)
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0, result.output
    for name in dataminer.SUBMODULES:
        assert f"- {name}" in result.output
    assert "THIẾU" not in result.output
    assert "LỖI" not in result.output
    assert "Sách      : book01 · book01.pdf" in result.output


@pytest.mark.parametrize("command", ["version", "info"])
def test_cli_subprocess_redirected_output_is_utf8(command: str) -> None:
    """Chạy `dm` như tiến trình thật với stdout bị chuyển hướng (giống `dm info > file`).

    Bắt lỗi UnicodeEncodeError trên Windows mà CliRunner không phát hiện được.
    """
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}
    proc = subprocess.run(
        [sys.executable, "-c", "from dataminer.cli import main; main()", command],
        cwd=ROOT,
        env=env,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr.decode("utf-8", errors="replace")
    out = proc.stdout.decode("utf-8")  # phải decode được UTF-8
    if command == "info":
        assert "Thư mục:" in out
        assert "Trạng thái:" in out


def test_cli_no_args_shows_help() -> None:
    result = runner.invoke(app, [])
    assert "info" in result.output
    assert "version" in result.output


def _git_ignored(path: str) -> bool:
    """True nếu git bỏ qua `path` (dùng chính .gitignore của repo)."""
    proc = subprocess.run(
        ["git", "check-ignore", "-q", "--no-index", path],
        cwd=ROOT,
        check=False,
    )
    return proc.returncode == 0


@pytest.mark.parametrize(
    ("path", "ignored"),
    [
        (".env", True),
        ("configs/local.yaml", True),
        ("data/books/book01/raw/book.pdf", True),
        ("data/books/iasp/p1_clean/blocks.jsonl", True),
        ("data/.gitkeep", False),
        ("data/cache/llm_cache.sqlite", True),
        ("samples/P0.1/cli_info.txt", False),
        (".env.example", False),
        ("src/dataminer/cli/__init__.py", False),
        ("configs/books/iasp/book.yaml", False),
    ],
)
def test_gitignore_rules(path: str, ignored: bool) -> None:
    assert _git_ignored(path) is ignored
