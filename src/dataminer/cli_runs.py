"""Nhóm lệnh `dm runs`: xem lịch sử các lần chạy phase (manifest)."""

import json
from pathlib import Path

import typer

from dataminer.core.config import ConfigError, Settings, load_settings
from dataminer.core.io import DataFileError, read_json
from dataminer.core.schemas import RunManifest

runs_app = typer.Typer(help="Lịch sử các lần chạy (manifest).", no_args_is_help=True)

RootOption = typer.Option(None, "--root", help="Gốc dự án.", show_default=False)


def _load(root: Path | None) -> Settings:
    try:
        return load_settings(root)
    except ConfigError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from None


def _manifests(data_dir: Path) -> list[RunManifest]:
    found = []
    for path in data_dir.glob("*/runs/*.json"):
        try:
            found.append(RunManifest.model_validate(read_json(path)))
        except (DataFileError, ValueError):
            continue
    return sorted(found, key=lambda m: m.started_at)


@runs_app.command("list")
def list_cmd(root: Path | None = RootOption) -> None:
    """Bảng các lần chạy: phase, trạng thái, thời lượng, file ra, chi phí LLM."""
    settings = _load(root)
    manifests = _manifests(settings.paths.data_dir)
    if not manifests:
        typer.echo("Chưa có lần chạy nào (data/<phase>/runs/ trống).")
        return
    typer.echo(
        f"{'run_id':<38} {'trạng thái':<10} {'thời lượng':>10} {'file ra':>7} "
        f"{'gọi LLM':>7} {'chi phí':>10}"
    )
    for m in manifests:
        duration = f"{m.duration_s:.2f}s" if m.duration_s is not None else "-"
        typer.echo(
            f"{m.run_id:<38} {m.status:<10} {duration:>10} {len(m.outputs):>7} "
            f"{m.llm.calls:>7} {'$' + format(m.llm.cost_usd, '.6f'):>10}"
        )


@runs_app.command("show")
def show_cmd(target: str, root: Path | None = RootOption) -> None:
    """In manifest: TARGET là tên phase (lần chạy gần nhất) hoặc run_id."""
    settings = _load(root)
    data_dir = settings.paths.data_dir
    latest = data_dir / target / "manifest.json"
    if latest.is_file():
        path = latest
    else:
        matches = list(data_dir.glob(f"*/runs/{target}.json"))
        if not matches:
            typer.echo(f"Không tìm thấy phase hoặc run_id '{target}'.", err=True)
            raise typer.Exit(1)
        path = matches[0]
    typer.echo(json.dumps(read_json(path), ensure_ascii=False, indent=2))
