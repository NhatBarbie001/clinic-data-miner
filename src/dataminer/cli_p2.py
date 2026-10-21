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


NoLLMOption = typer.Option(False, "--no-llm", help="Không hỏi LLM cho tiêu đề mơ hồ.")


@p2_app.command("headings")
def headings_cmd(
    root: Path | None = RootOption,
    evaluate: bool = EvalOption,
    truth: Path | None = TruthOption,
    no_llm: bool = NoLLMOption,
) -> None:
    """Cấp của mọi tiêu đề (chương/bệnh/mục/mục con/khác) → data/p2_tree/heading_levels.jsonl."""
    from dataminer.core.io import read_jsonl, write_json, write_jsonl
    from dataminer.core.llm_client import LLMClient
    from dataminer.core.llm_types import LLMError
    from dataminer.core.prompts import PromptError, load_prompt
    from dataminer.evaluation.p1_eval import format_eval
    from dataminer.evaluation.p2_eval import all_pass, eval_heading_levels
    from dataminer.ingest.blocks import Block
    from dataminer.ingest.pipeline import p1_dir
    from dataminer.structure.heading_levels import classify_headings
    from dataminer.structure.toc import TocResult, extract_toc

    settings = _load(root)
    blocks_path = p1_dir(settings) / "blocks.jsonl"
    if not blocks_path.is_file():
        typer.echo(f"Chưa có {blocks_path} - chạy `dm p1 run` trước.", err=True)
        raise typer.Exit(1)
    blocks = list(read_jsonl(blocks_path, Block))
    out_dir = p2_dir(settings)
    toc_path = out_dir / "toc.json"
    if toc_path.is_file():
        toc = TocResult.model_validate_json(toc_path.read_text(encoding="utf-8"))
    else:
        pdf = settings.paths.raw_dir / settings.project.book_file
        toc = extract_toc(
            pdf,
            book_id=settings.project.book_id,
            cfg=settings.p2.toc,
            furniture=settings.p1.furniture,
        )
        write_json(toc_path, toc.model_dump(mode="json"))

    cfg = settings.p2.headings
    use_llm = cfg.llm_fallback and not no_llm
    try:
        prompt = load_prompt(settings.paths.prompts_dir, cfg.prompt) if use_llm else None
        client = LLMClient(settings) if use_llm else None
        result = classify_headings(blocks, toc.entries, cfg, client=client, prompt=prompt)
    except (LLMError, PromptError, ConfigError) as exc:
        typer.echo(f"✗ {exc}", err=True)
        raise typer.Exit(1) from None
    out = out_dir / "heading_levels.jsonl"
    write_jsonl(out, result.decisions)

    counts = {
        lv: sum(d.level == lv for d in result.decisions)
        for lv in ("chapter", "disease", "section", "subsection", "other")
    }
    sources = {s: sum(d.source == s for d in result.decisions) for s in ("rules", "toc", "llm")}
    typer.echo(
        f"Tiêu đề: {len(result.decisions)} · thân bài cỡ {result.body_size} · "
        + " · ".join(f"{k} {v}" for k, v in counts.items())
    )
    typer.echo(
        f"  nguồn: quy tắc {sources['rules']} · mục lục {sources['toc']} · LLM {sources['llm']} "
        f"({result.llm_calls} lời gọi mới, ${result.llm_cost_usd:.6f})"
    )
    for d in result.decisions:
        if d.confidence != "high" or d.flags:
            typer.echo(f"  ⚑ {d.text} → {d.level} ({d.confidence}, {d.source}) {d.flags}")
    for w in result.warnings:
        typer.echo(f"  ⚠ {w}")
    typer.echo(f"  đầu ra: {out}")

    if evaluate:
        truth_path = truth or (settings.paths.raw_dir / settings.project.book_file).with_suffix(
            ".truth.json"
        )
        if not truth_path.is_file():
            typer.echo(f"Không có đáp án {truth_path} - chỉ đánh giá được với sách mẫu.", err=True)
            raise typer.Exit(1)
        pages = (min(b.page_start for b in blocks), max(b.page_end for b in blocks))
        report = eval_heading_levels(
            result.decisions, json.loads(truth_path.read_text(encoding="utf-8")), pages
        )
        typer.echo("\n" + format_eval(report))
        if not all_pass(report):
            raise typer.Exit(1)


@p2_app.command("tree")
def tree_cmd(
    root: Path | None = RootOption, evaluate: bool = EvalOption, truth: Path | None = TruthOption
) -> None:
    """Dựng cây chương → bệnh → mục → nodes.jsonl, tree.json, tree.md (cần `dm p2 headings`)."""
    from dataminer.core.io import read_jsonl, write_json, write_jsonl
    from dataminer.evaluation.p1_eval import format_eval
    from dataminer.evaluation.p2_eval import all_pass, eval_tree
    from dataminer.ingest.blocks import Block
    from dataminer.ingest.pdf_reader import Line
    from dataminer.ingest.pipeline import p1_dir
    from dataminer.structure.heading_levels import HeadingDecision
    from dataminer.structure.toc import TocResult
    from dataminer.structure.tree_builder import (
        TreeInvariantError,
        build_tree,
        render_tree_md,
        to_nested,
    )

    settings = _load(root)
    out_dir = p2_dir(settings)
    blocks_path = p1_dir(settings) / "blocks.jsonl"
    levels_path = out_dir / "heading_levels.jsonl"
    for path, cmd in ((blocks_path, "dm p1 run"), (levels_path, "dm p2 headings")):
        if not path.is_file():
            typer.echo(f"Chưa có {path} - chạy `{cmd}` trước.", err=True)
            raise typer.Exit(1)
    blocks = list(read_jsonl(blocks_path, Block))
    decisions = list(read_jsonl(levels_path, HeadingDecision))
    toc_path = out_dir / "toc.json"
    toc = (
        TocResult.model_validate_json(toc_path.read_text(encoding="utf-8")).entries
        if toc_path.is_file()
        else []
    )
    try:
        result = build_tree(blocks, decisions, book_id=settings.project.book_id, toc=toc)
    except TreeInvariantError as exc:
        typer.echo(f"✗ {exc}", err=True)
        raise typer.Exit(1) from None
    nodes = result.nodes
    write_jsonl(out_dir / "nodes.jsonl", nodes)
    write_json(out_dir / "tree.json", to_nested(nodes))
    tree_md = render_tree_md(nodes, blocks)
    (out_dir / "tree.md").write_text(tree_md, encoding="utf-8")

    attached = sum(len(n.block_ids) + (n.heading_block_id is not None) for n in nodes)
    count = {lv: sum(n.level == lv for n in nodes) for lv in
             ("chapter", "disease", "section", "subsection", "front")}  # fmt: skip
    typer.echo(
        f"Cây: {count['chapter']} chương · {count['disease']} bệnh · {count['section']} mục · "
        f"{count['subsection']} mục con · {attached}/{len(blocks)} block được gắn"
        + (" · có phần đầu" if count["front"] else "")
    )
    typer.echo(tree_md.rstrip())
    for w in result.warnings:
        typer.echo(f"  ⚠ {w}")
    typer.echo(f"  đầu ra: {out_dir}/nodes.jsonl, tree.json, tree.md")

    if evaluate:
        truth_path = truth or (settings.paths.raw_dir / settings.project.book_file).with_suffix(
            ".truth.json"
        )
        if not truth_path.is_file():
            typer.echo(f"Không có đáp án {truth_path} - chỉ đánh giá được với sách mẫu.", err=True)
            raise typer.Exit(1)
        lines = list(read_jsonl(p1_dir(settings) / "content_lines.jsonl", Line))
        pages = (min(b.page_start for b in blocks), max(b.page_end for b in blocks))
        report = eval_tree(
            nodes, blocks, lines, json.loads(truth_path.read_text(encoding="utf-8")), pages
        )
        typer.echo("\n" + format_eval(report))
        if not all_pass(report):
            raise typer.Exit(1)
