"""Nhóm lệnh `dm p2`: dựng cây cấu trúc sách (mục lục → cấp tiêu đề → cây → loại mục).

Module nặng (PyMuPDF...) được import BÊN TRONG lệnh để `dm` khởi động nhanh.
"""

import json
from pathlib import Path

import typer

from dataminer.core.config import ConfigError, Settings, load_settings

p2_app = typer.Typer(help="P2 - dựng cây cấu trúc sách.", no_args_is_help=True)

RootOption = typer.Option(None, "--root", help="Gốc dự án.", show_default=False)
TruthOption = typer.Option(None, "--truth", help="Đáp án (mặc định <pdf>.truth.json).")
EvalOption = typer.Option(False, "--eval", help="So với đáp án sách mẫu (G1), exit 1 nếu sai.")


def _load(root: Path | None) -> Settings:
    try:
        return load_settings(root)
    except ConfigError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from None


def p2_dir(settings: Settings) -> Path:
    return settings.paths.data_dir / "p2_tree"


@p2_app.command("toc")
def toc_cmd(
    root: Path | None = RootOption, evaluate: bool = EvalOption, truth: Path | None = TruthOption
) -> None:
    """Tìm và đọc mục lục → data/p2_tree/toc.json (chương, bệnh, số trang in → trang PDF)."""
    from dataminer.core.io import write_json
    from dataminer.evaluation.p1_eval import format_eval
    from dataminer.evaluation.p2_eval import all_pass, eval_toc
    from dataminer.structure.toc import extract_toc

    settings = _load(root)
    pdf = settings.paths.raw_dir / settings.project.book_file
    if not pdf.is_file():
        typer.echo(f"Không có file sách {pdf} (đặt PDF vào {settings.paths.raw_dir}).", err=True)
        raise typer.Exit(1)
    result = extract_toc(
        pdf, book_id=settings.project.book_id, cfg=settings.p2.toc, furniture=settings.p1.furniture
    )
    out = p2_dir(settings) / "toc.json"
    write_json(out, result.model_dump(mode="json"))

    pages = ", ".join(map(str, result.toc_pages)) or "-"
    offset = "?" if result.page_offset is None else f"{result.page_offset:+d}"
    typer.echo(
        f"Mục lục: trang PDF {pages} ({result.source}) · {len(result.entries)} mục · "
        f"trang PDF = trang in {offset}"
    )
    for e in result.entries:
        indent = "  " if e.level == "disease" else ""
        flags = f"  ⚑ {', '.join(e.flags)}" if e.flags else ""
        typer.echo(
            f"  {indent}[{e.level:<7}] {e.title}  · tr.in {e.printed_page} → PDF {e.pdf_page}"
            + flags
        )
    for w in result.warnings:
        typer.echo(f"  ⚠ {w}")
    typer.echo(f"  đầu ra: {out}")

    if evaluate:
        truth_path = truth or pdf.with_suffix(".truth.json")
        if not truth_path.is_file():
            typer.echo(f"Không có đáp án {truth_path} - chỉ đánh giá được với sách mẫu.", err=True)
            raise typer.Exit(1)
        report = eval_toc(result, json.loads(truth_path.read_text(encoding="utf-8")))
        typer.echo("\n" + format_eval(report))
        if not all_pass(report):
            raise typer.Exit(1)
