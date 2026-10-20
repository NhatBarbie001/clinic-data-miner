"""Lệnh `dm survey` (P0.5) và nhóm `dm dev` (sách mẫu, đối chiếu đáp án).

Các module dùng PyMuPDF được import BÊN TRONG lệnh: nạp pymupdf mất ~2 giây, không để mọi
lệnh `dm` (kể cả `dm version`) phải chịu.
"""

import json
from pathlib import Path

import typer

from dataminer.core.config import ConfigError, Settings, load_settings
from dataminer.core.run import RunRecorder

PHASE = "p0_survey"
dev_app = typer.Typer(
    help="Công cụ phát triển: sách mẫu tổng hợp, đối chiếu đáp án.", no_args_is_help=True
)

RootOption = typer.Option(None, "--root", help="Gốc dự án.", show_default=False)
PdfOption = typer.Option(
    None, "--pdf", help="File PDF (mặc định: paths.raw_dir/project.book_file)."
)
OutOption = typer.Option(None, "--out", help="Thư mục kết quả.")
SeedOption = typer.Option(7, "--seed", help="Seed sinh sách mẫu (cùng seed → cùng sách).")
TruthOption = typer.Option(None, "--truth", help="File đáp án (mặc định: <pdf>.truth.json).")


def _load(root: Path | None) -> Settings:
    try:
        return load_settings(root)
    except ConfigError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from None


def survey_cmd(
    root: Path | None = RootOption, pdf: Path | None = PdfOption, out: Path | None = OutOption
) -> None:
    """Khảo sát PDF sách: thống kê, header/footer, ứng viên tiêu đề, dấu hiệu lỗi OCR."""
    from dataminer.ingest.survey import survey_pdf

    settings = _load(root)
    pdf_path = pdf or settings.paths.raw_dir / settings.project.book_file
    if not pdf_path.is_file():
        typer.echo(
            f"Không thấy {pdf_path}. Chép sách vào đó, hoặc tạo sách mẫu: "
            "`dm dev make-sample-book`.",
            err=True,
        )
        raise typer.Exit(1)
    out_dir = out or settings.paths.data_dir / PHASE
    with RunRecorder(settings, PHASE, out_dir=out_dir) as run:
        run.add_input(pdf_path, records=False)
        result = survey_pdf(pdf_path, out_dir, book_id=settings.project.book_id)
        for name in (
            "stats.json",
            "lines.jsonl",
            "header_footer.json",
            "heading_candidates.json",
            "ocr_signals.json",
            "survey_report.md",
        ):
            run.add_output(out_dir / name, records=name.endswith(".jsonl"))
        run.count("pages", result.stats["pages"])
        run.count("lines", result.stats["lines"])
        run.count("heading_candidates", len(result.headings["candidates"]))
        run.count("ocr_signals", len(result.signals))
    s = result.stats
    typer.echo(
        f"✓ {s['pages']} trang ({s['pages_with_text']} có text), {s['lines']} dòng, "
        f"cỡ chữ thân bài {s['body_font_size']} pt"
    )
    typer.echo(
        f"  header/footer: {len(result.header_footer['patterns'])} mẫu · ứng viên tiêu đề: "
        f"{len(result.headings['candidates'])} · dấu hiệu lỗi OCR: {len(result.signals)}"
    )
    typer.echo(f"  báo cáo: {out_dir / 'survey_report.md'}")


@dev_app.command("make-sample-book")
def make_book_cmd(
    root: Path | None = RootOption, out: Path | None = OutOption, seed: int = SeedOption
) -> None:
    """Sinh sách mẫu tổng hợp 'scan + OCR' + đáp án (mặc định vào data/raw/)."""
    from dataminer.devtools.sample_book import make_sample_book

    settings = _load(root)
    out_dir = out or settings.paths.raw_dir
    name = Path(settings.project.book_file).stem
    book = make_sample_book(out_dir, name=name, seed=seed)
    kinds: dict[str, int] = {}
    for err in book.truth["ocr_errors"]:
        kinds[err["kind"]] = kinds.get(err["kind"], 0) + 1
    typer.echo(
        f"✓ {book.pdf_path} ({len(book.truth['pages'])} trang, "
        f"{book.pdf_path.stat().st_size // 1024} KB, seed {seed})"
    )
    typer.echo(f"  đáp án: {book.truth_path}")
    typer.echo(f"  lỗi OCR đã cài: {kinds}")


@dev_app.command("check-survey")
def check_cmd(
    root: Path | None = RootOption,
    pdf: Path | None = PdfOption,
    truth: Path | None = TruthOption,
    out: Path | None = OutOption,
) -> None:
    """Chạy khảo sát rồi đối chiếu với đáp án của sách mẫu (exit 1 nếu chưa đạt chỉ tiêu)."""
    from dataminer.devtools.survey_check import check_survey, format_check
    from dataminer.ingest.survey import survey_pdf

    settings = _load(root)
    pdf_path = pdf or settings.paths.raw_dir / settings.project.book_file
    truth_path = truth or pdf_path.with_suffix(".truth.json")
    if not truth_path.is_file():
        typer.echo(f"Không có đáp án {truth_path} - lệnh này chỉ dùng cho sách mẫu.", err=True)
        raise typer.Exit(1)
    out_dir = out or settings.paths.data_dir / PHASE
    result = survey_pdf(pdf_path, out_dir, book_id=settings.project.book_id)
    checks = check_survey(result, json.loads(truth_path.read_text(encoding="utf-8")))
    report = format_check(checks)
    (out_dir / "survey_vs_truth.txt").write_text(report + "\n", encoding="utf-8")
    typer.echo(report)
    if not checks["all_pass"]:
        raise typer.Exit(1)


pilot_app = typer.Typer(help="Chương mẫu (pilot): kiểm tra cấu hình pilot.", no_args_is_help=True)
SurveyDirOption = typer.Option(None, "--survey", help="Thư mục kết quả `dm survey`.")


@pilot_app.command("check")
def pilot_check_cmd(root: Path | None = RootOption, survey: Path | None = SurveyDirOption) -> None:
    """Kiểm tra pilot: trang tồn tại, có text, mỗi bệnh có tiêu đề trong phạm vi trang."""
    from dataminer.ingest.pilot import check_pilot, format_pilot_report

    settings = _load(root)
    report = check_pilot(settings.pilot, survey or settings.paths.data_dir / PHASE)
    typer.echo(format_pilot_report(report))
    if not report.ok:
        raise typer.Exit(1)
