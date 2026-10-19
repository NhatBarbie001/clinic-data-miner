"""CLI `dm`: điểm vào chung cho mọi phase.

Mỗi phase sẽ đăng ký nhóm lệnh con của mình (vd. `dm p1 run`, `dm eval p3`).
"""

import importlib
import io
import platform
import sys
from pathlib import Path

import typer
import yaml

from dataminer import SUBMODULES, __version__
from dataminer.cli_llm import llm_app
from dataminer.core.config import ConfigError, find_project_root, load_settings

app = typer.Typer(
    name="dm",
    help="Data-miner: khai thác dữ liệu y khoa từ sách PDF.",
    no_args_is_help=True,
    add_completion=False,
)
config_app = typer.Typer(help="Xem và kiểm tra cấu hình.", no_args_is_help=True)
app.add_typer(config_app, name="config")
app.add_typer(llm_app, name="llm")

RootOption = typer.Option(
    None, "--root", help="Gốc dự án (mặc định: tìm từ thư mục hiện tại).", show_default=False
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


@config_app.command("show")
def config_show(root: Path | None = RootOption) -> None:
    """In cấu hình cuối cùng sau khi gộp các lớp (API key đã bị che)."""
    try:
        settings = load_settings(root)
    except ConfigError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from None
    typer.echo(f"# fingerprint: {settings.fingerprint()}")
    typer.echo("# các lớp đã áp dụng (lớp sau ghi đè lớp trước):")
    for source in settings.sources:
        typer.echo(f"#   - {source}")
    typer.echo(
        yaml.safe_dump(settings.to_display_dict(), allow_unicode=True, sort_keys=False).rstrip()
    )


@config_app.command("validate")
def config_validate(root: Path | None = RootOption) -> None:
    """Kiểm tra cấu hình: exit 0 nếu hợp lệ, exit 1 kèm danh sách lỗi."""
    try:
        settings = load_settings(root)
    except ConfigError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from None
    key_status = "đã đặt" if settings.llm.api_key else "chưa đặt (cần trước khi gọi LLM)"
    typer.echo(f"Cấu hình hợp lệ ✓  fingerprint={settings.fingerprint()}")
    typer.echo(f"  - {len(settings.models)} tác vụ model, chế độ LLM: {settings.llm.mode}")
    typer.echo(f"  - API key: {key_status}")


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
