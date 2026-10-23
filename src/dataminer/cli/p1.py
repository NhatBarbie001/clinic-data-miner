"""Nhóm lệnh `dm p1`: chạy phase P1, đánh giá, báo cáo, duyệt tay.

Module nặng (PyMuPDF...) được import BÊN TRONG lệnh để `dm` khởi động nhanh.
"""

import json
from pathlib import Path
from typing import Literal, cast

import typer

from dataminer.cli._common import current_book
from dataminer.core.config import ConfigError, Settings, load_settings

Scope = Literal["pilot", "all"]
p1_app = typer.Typer(help="P1 - trích xuất và làm sạch text.", no_args_is_help=True)
review_app = typer.Typer(help="Hàng đợi duyệt tay (CSV).", no_args_is_help=True)
p1_app.add_typer(review_app, name="review")

RootOption = typer.Option(None, "--root", help="Gốc dự án.", show_default=False)
ScopeOption = typer.Option("pilot", "--scope", help="pilot (chương mẫu) hoặc all (toàn sách).")
PagesOption = typer.Option(None, "--pages", help="Phạm vi trang PDF, vd. 6-7 (ghi đè --scope).")
NoLLMOption = typer.Option(False, "--no-llm", help="Bỏ qua sửa OCR bằng LLM.")
ForceOption = typer.Option(False, "--force", help="Bỏ tiến độ sửa OCR cũ (cache LLM vẫn dùng).")
TruthOption = typer.Option(None, "--truth", help="Đáp án (mặc định <pdf>.truth.json).")
AuditOption = typer.Option(
    0.0, "--audit", help="Thêm mẫu kiểm tra thay đổi đã chấp nhận (vd. 0.05)."
)
OutCsvOption = typer.Option(
    None, "--out", help="File CSV (mặc định data/p1_clean/review/review_queue.csv)."
)


def _load(root: Path | None) -> Settings:
    try:
        return load_settings(root, book=current_book())
    except ConfigError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from None


def _parse_pages(pages: str | None) -> tuple[int, int] | None:
    if not pages:
        return None
    try:
        a, b = (int(x) for x in pages.split("-"))
    except ValueError:
        typer.echo(f"--pages phải có dạng a-b (vd. 6-7), nhận '{pages}'", err=True)
        raise typer.Exit(1) from None
    return a, b


@p1_app.command("run")
def run_cmd(
    root: Path | None = RootOption,
    scope: str = ScopeOption,
    pages: str | None = PagesOption,
    no_llm: bool = NoLLMOption,
    force: bool = ForceOption,
) -> None:
    """Chạy P1: đọc PDF → bỏ header/footer → dựng block → sửa OCR → áp duyệt → blocks.jsonl."""
    from dataminer.core.llm_types import LLMError
    from dataminer.pipeline.p1 import run_p1

    settings = _load(root)
    if scope not in ("pilot", "all"):
        typer.echo("--scope phải là pilot hoặc all", err=True)
        raise typer.Exit(1)
    try:
        result = run_p1(
            settings,
            scope=cast(Scope, scope),
            pages=_parse_pages(pages),
            use_llm=not no_llm,
            force=force,
        )
    except (FileNotFoundError, LLMError, ConfigError) as exc:
        typer.echo(f"✗ {exc}", err=True)
        raise typer.Exit(1) from None
    c = result.counts
    typer.echo(
        f"✓ P1 xong: trang PDF {result.pages[0]}-{result.pages[1]} · {c['lines']} dòng · "
        f"bỏ {c['furniture_removed']} header/footer · {c['blocks']} block"
    )
    typer.echo(
        f"  sửa OCR: {c['fixes_accepted']} chấp nhận, {c['fixes_rejected']} từ chối · "
        f"đã duyệt {c['reviews_applied']} · chờ duyệt {result.pending_review}"
    )
    typer.echo(f"  chi phí LLM: ${result.llm_cost_usd:.6f} · manifest: {result.run_id}")
    if result.stale_decisions:
        typer.echo(f"  ⚠ {len(result.stale_decisions)} quyết định duyệt không còn khớp (stale)")
    typer.echo(f"  đầu ra: {result.out_dir}/blocks.jsonl")


@p1_app.command("eval")
def eval_cmd(root: Path | None = RootOption, truth: Path | None = TruthOption) -> None:
    """So với đáp án → eval.json + bảng chỉ tiêu G1-G9 (exit 1 nếu chưa đạt)."""
    from dataminer.core.io import write_json
    from dataminer.evaluation.p1_eval import all_pass, evaluate_p1, format_eval
    from dataminer.pipeline.p1 import p1_dir

    settings = _load(root)
    truth_path = truth or (settings.paths.raw_dir / settings.project.book_file).with_suffix(
        ".truth.json"
    )
    if not truth_path.is_file():
        typer.echo(
            f"Không có đáp án {truth_path} - chỉ đánh giá tự động được với sách mẫu.", err=True
        )
        raise typer.Exit(1)
    out = p1_dir(settings)
    if not (out / "blocks.jsonl").is_file():
        typer.echo("Chưa có kết quả P1 - chạy `dm p1 run` trước.", err=True)
        raise typer.Exit(1)
    report = evaluate_p1(out, json.loads(truth_path.read_text(encoding="utf-8")))
    write_json(out / "eval.json", report)
    typer.echo(format_eval(report))
    ok = all_pass(report)
    typer.echo(f"\nKẾT LUẬN: {'ĐẠT mọi chỉ tiêu G1-G9' if ok else 'CHƯA ĐẠT'}")
    if not ok:
        raise typer.Exit(1)


@p1_app.command("report")
def report_cmd(root: Path | None = RootOption) -> None:
    """Sinh data/p1_clean/report.md (tổng quan, chỉ tiêu, trước/sau, chờ duyệt)."""
    from dataminer.pipeline.p1 import p1_dir
    from dataminer.pipeline.p1_report import render_report

    out = p1_dir(_load(root))
    if not (out / "manifest.json").is_file():
        typer.echo("Chưa có kết quả P1 - chạy `dm p1 run` trước.", err=True)
        raise typer.Exit(1)
    (out / "report.md").write_text(render_report(out), encoding="utf-8")
    typer.echo(f"✓ {out / 'report.md'}")


@review_app.command("export")
def review_export_cmd(
    root: Path | None = RootOption, audit: float = AuditOption, out: Path | None = OutCsvOption
) -> None:
    """Xuất hàng đợi duyệt ra CSV (Excel), kèm mẫu kiểm tra nếu --audit > 0."""
    from dataminer.core.io import read_jsonl
    from dataminer.model.block import Block
    from dataminer.ocrfix.review import audit_sample, build_queue, export_csv
    from dataminer.pipeline.p1 import p1_dir

    base = p1_dir(_load(root))
    blocks = list(read_jsonl(base / "blocks.jsonl", Block))
    queue = build_queue(blocks)
    sample = audit_sample(blocks, audit)
    path = out or base / "review" / "review_queue.csv"
    export_csv([*queue, *sample], path)
    typer.echo(f"✓ {path}: {len(queue)} mục cần quyết định + {len(sample)} mục kiểm tra mẫu")


@review_app.command("import")
def review_import_cmd(csv_path: Path, root: Path | None = RootOption) -> None:
    """Nhập quyết định từ CSV đã điền → decisions.jsonl → áp lại → blocks.jsonl."""
    from dataminer.core.io import read_jsonl
    from dataminer.model.block import Block
    from dataminer.ocrfix.review import (
        ReviewError,
        build_queue,
        import_csv,
        known_items,
        save_decisions,
    )
    from dataminer.pipeline.p1 import finalize, p1_dir

    settings = _load(root)
    base = p1_dir(settings)
    current = list(read_jsonl(base / "blocks.jsonl", Block))
    try:
        new = import_csv(csv_path, known_items(current))
    except ReviewError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from None
    save_decisions(base / "review" / "decisions.jsonl", new)
    fixed = list(read_jsonl(base / "blocks_fixed.jsonl", Block))
    final, stale = finalize(settings, fixed)
    typer.echo(
        f"✓ nhập {len(new)} quyết định · còn chờ {len(build_queue(final))} · "
        f"stale {len(stale)} → {base / 'blocks.jsonl'}"
    )
