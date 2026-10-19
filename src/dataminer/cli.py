"""CLI `dm`: điểm vào chung cho mọi phase.

Mỗi phase sẽ đăng ký nhóm lệnh con của mình (vd. `dm p1 run`, `dm eval p3`).
"""

import importlib
import io
import platform
import sys
from pathlib import Path

import typer

from dataminer import SUBMODULES, __version__

app = typer.Typer(
    name="dm",
    help="Data-miner: khai thác dữ liệu y khoa từ sách PDF.",
    no_args_is_help=True,
    add_completion=False,
)

# Thư mục bắt buộc của dự án, tương đối với gốc repo.
REQUIRED_DIRS: tuple[str, ...] = (
    "configs",
    "prompts",
    "scripts",
    "app",
    "eval",
    "data/raw",
    "samples",
    "docs/phases",
    "tests/unit",
    "tests/integration",
    "tests/fixtures",
)


def find_project_root(start: Path | None = None) -> Path:
    """Tìm gốc repo: thư mục gần nhất (đi ngược lên) có `pyproject.toml`."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    raise FileNotFoundError("Không tìm thấy pyproject.toml - hãy chạy trong thư mục dự án.")


@app.command("version")
def version_cmd() -> None:
    """In phiên bản dataminer."""
    typer.echo(f"dataminer {__version__}")


@app.command("info")
def info_cmd() -> None:
    """In thông tin môi trường và trạng thái dự án."""
    root = find_project_root()
    typer.echo(f"dataminer   : {__version__}")
    typer.echo(f"python      : {platform.python_version()}")
    typer.echo(f"project root: {root}")

    typer.echo("\nModules:")
    for name in SUBMODULES:
        try:
            importlib.import_module(f"dataminer.{name}")
            status = "ok"
        except ImportError as exc:  # pragma: no cover - chỉ xảy ra khi cài đặt hỏng
            status = f"LỖI ({exc})"
        typer.echo(f"  - {name:<11} {status}")

    typer.echo("\nThư mục:")
    for rel in REQUIRED_DIRS:
        mark = "ok" if (root / rel).is_dir() else "THIẾU"
        typer.echo(f"  - {rel:<18} {mark}")

    typer.echo("\nTrạng thái:")
    env_status = "có" if (root / ".env").is_file() else "chưa có (copy từ .env.example)"
    typer.echo(f"  - .env      : {env_status}")
    pdfs = sorted(p.name for p in (root / "data" / "raw").glob("*.pdf"))
    typer.echo(f"  - PDF sách  : {', '.join(pdfs) if pdfs else 'chưa có (chép vào data/raw/)'}")


def _force_utf8_stdio() -> None:
    """Ép stdout/stderr sang UTF-8.

    Trên Windows, khi output bị chuyển hướng (pipe, file) Python dùng code page hệ thống
    (vd. cp1258) và không mã hóa được tiếng Việt đầy đủ → UnicodeEncodeError.
    """
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper) and stream.encoding.lower() != "utf-8":
            stream.reconfigure(encoding="utf-8")


def main() -> None:
    """Entry point của lệnh `dm`."""
    _force_utf8_stdio()
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
