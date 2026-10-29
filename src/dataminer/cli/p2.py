"""Nhóm lệnh `dm p2`: dựng cây cấu trúc sách (mục lục → cấp tiêu đề → cây → loại mục).

Module nặng (PyMuPDF...) được import BÊN TRONG lệnh để `dm` khởi động nhanh.
"""

import json
from pathlib import Path

import typer

from dataminer.cli._common import current_book
from dataminer.core.config import ConfigError, Settings, load_settings

p2_app = typer.Typer(help="P2 - dựng cây cấu trúc sách.", no_args_is_help=True)

RootOption = typer.Option(None, "--root", help="Gốc dự án.", show_default=False)
TruthOption = typer.Option(None, "--truth", help="Đáp án (mặc định <pdf>.truth.json).")
EvalOption = typer.Option(False, "--eval", help="So với đáp án sách mẫu, exit 1 nếu chưa đạt.")


def _load(root: Path | None) -> Settings:
    try:
        return load_settings(root, book=current_book())
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
    from dataminer.books.registry import rules_for
    from dataminer.core.io import write_json
    from dataminer.evaluation.truth.p1_eval import format_eval
    from dataminer.evaluation.truth.p2_eval import all_pass, eval_toc

    settings = _load(root)
    pdf = settings.paths.raw_dir / settings.project.book_file
    if not pdf.is_file():
        typer.echo(f"Không có file sách {pdf} (đặt PDF vào {settings.paths.raw_dir}).", err=True)
        raise typer.Exit(1)
    result = rules_for(settings).read_toc(settings)
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
    from dataminer.books.registry import rules_for
    from dataminer.core.io import read_jsonl, write_json, write_jsonl
    from dataminer.core.llm_client import LLMClient
    from dataminer.core.llm_types import LLMError
    from dataminer.core.prompts import PromptError, load_prompt
    from dataminer.evaluation.truth.p1_eval import format_eval
    from dataminer.evaluation.truth.p2_eval import all_pass, eval_heading_levels
    from dataminer.model.block import Block
    from dataminer.model.toc import TocResult
    from dataminer.pipeline.p1 import p1_dir
    from dataminer.structure.heading_levels import classify_headings

    settings = _load(root)
    blocks_path = p1_dir(settings) / "blocks.jsonl"
    if not blocks_path.is_file():
        typer.echo(f"Chưa có {blocks_path} - chạy `dm p1 run` trước.", err=True)
        raise typer.Exit(1)
    blocks = list(read_jsonl(blocks_path, Block))
    rules = rules_for(settings)
    out_dir = p2_dir(settings)
    toc_path = out_dir / "toc.json"
    if toc_path.is_file():
        toc = TocResult.model_validate_json(toc_path.read_text(encoding="utf-8"))
    else:
        toc = rules.read_toc(settings)
        write_json(toc_path, toc.model_dump(mode="json"))

    cfg = settings.p2.headings
    use_llm = cfg.llm_fallback and not no_llm
    try:
        prompt = load_prompt(settings.paths.prompts_dir, cfg.prompt) if use_llm else None
        client = LLMClient(settings) if use_llm else None
        result = classify_headings(
            blocks,
            toc.entries,
            cfg,
            rule_level=rules.rule_level,
            chapter_prefix=rules.chapter_prefix,
            client=client,
            prompt=prompt,
        )
    except (LLMError, PromptError, ConfigError) as exc:
        typer.echo(f"✗ {exc}", err=True)
        raise typer.Exit(1) from None
    out = out_dir / "heading_levels.jsonl"
    write_jsonl(out, result.decisions)

    counts = {
        lv: sum(d.level == lv for d in result.decisions)
        for lv in ("part", "chapter", "disease", "section", "subsection", "other")
        if lv != "part" or any(d.level == "part" for d in result.decisions)
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
    from dataminer.books.registry import rules_for
    from dataminer.core.io import read_jsonl, write_json, write_jsonl
    from dataminer.evaluation.truth.p1_eval import format_eval
    from dataminer.evaluation.truth.p2_eval import all_pass, eval_tree
    from dataminer.model.block import Block
    from dataminer.model.line import Line
    from dataminer.model.toc import TocResult
    from dataminer.model.tree import HeadingDecision
    from dataminer.pipeline.p1 import p1_dir
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
    rules = rules_for(settings)
    try:
        result = build_tree(
            blocks,
            decisions,
            book_id=settings.project.book_id,
            toc=toc,
            display_title=rules.display_title,
        )
    except TreeInvariantError as exc:
        typer.echo(f"✗ {exc}", err=True)
        raise typer.Exit(1) from None
    nodes = result.nodes
    result.warnings += rules.annotate_tree(nodes)
    write_jsonl(out_dir / "nodes.jsonl", nodes)
    write_json(out_dir / "tree.json", to_nested(nodes))
    tree_md = render_tree_md(nodes, blocks)
    (out_dir / "tree.md").write_text(tree_md, encoding="utf-8")

    attached = sum(len(n.block_ids) + (n.heading_block_id is not None) for n in nodes)
    count = {lv: sum(n.level == lv for n in nodes) for lv in
             ("part", "chapter", "disease", "section", "subsection", "front")}  # fmt: skip
    typer.echo(
        "Cây: "
        + (f"{count['part']} phần · " if count["part"] else "")
        + f"{count['chapter']} chương · {count['disease']} bệnh · {count['section']} mục · "
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


sections_app = typer.Typer(
    help="P2.4 - loại mục (section_type) + vòng duyệt.", no_args_is_help=True
)
p2_app.add_typer(sections_app, name="sections")
ReviewerOption = typer.Option("reviewer", "--reviewer", help="Tên người duyệt (ghi vào từ điển).")
OutOption = typer.Option(
    None, "--out", help="File CSV (mặc định data/p2_tree/section_proposals.csv)."
)


def _proposals_path(settings: Settings) -> Path:
    return p2_dir(settings) / "section_proposals.jsonl"


def _map_path(settings: Settings) -> Path:
    return settings.from_root(settings.p2.sections.map)


@sections_app.command("map")
def sections_map_cmd(
    root: Path | None = RootOption,
    evaluate: bool = EvalOption,
    truth: Path | None = TruthOption,
    no_llm: bool = NoLLMOption,
) -> None:
    """Gán loại mục cho nodes.jsonl (cập nhật tại chỗ) + đề xuất chờ duyệt (cần `dm p2 tree`)."""
    from dataminer.books.registry import rules_for
    from dataminer.core.io import read_jsonl, write_jsonl
    from dataminer.core.llm_client import LLMClient
    from dataminer.core.llm_types import LLMError
    from dataminer.core.prompts import PromptError, load_prompt
    from dataminer.evaluation.truth.p1_eval import format_eval
    from dataminer.evaluation.truth.p2_eval import all_pass, eval_sections
    from dataminer.model.block import Block
    from dataminer.model.tree import Node
    from dataminer.pipeline.p1 import p1_dir
    from dataminer.structure.section_mapper import SectionMapError, load_section_map, map_sections
    from dataminer.structure.tree_builder import render_tree_md

    settings = _load(root)
    out_dir = p2_dir(settings)
    nodes_path = out_dir / "nodes.jsonl"
    if not nodes_path.is_file():
        typer.echo(f"Chưa có {nodes_path} - chạy `dm p2 tree` trước.", err=True)
        raise typer.Exit(1)
    nodes = list(read_jsonl(nodes_path, Node))
    cfg = settings.p2.sections
    use_llm = cfg.llm_fallback and not no_llm
    try:
        mapping = load_section_map(_map_path(settings))
        prompt = load_prompt(settings.paths.prompts_dir, cfg.prompt) if use_llm else None
        client = LLMClient(settings) if use_llm else None
        result = map_sections(
            nodes,
            mapping,
            cfg,
            client=client,
            prompt=prompt,
            section_key=rules_for(settings).section_key,
        )
    except (SectionMapError, LLMError, PromptError, ConfigError) as exc:
        typer.echo(f"✗ {exc}", err=True)
        raise typer.Exit(1) from None
    write_jsonl(nodes_path, nodes)
    write_jsonl(_proposals_path(settings), result.proposals)
    blocks = list(read_jsonl(p1_dir(settings) / "blocks.jsonl", Block))
    (out_dir / "tree.md").write_text(render_tree_md(nodes, blocks), encoding="utf-8")

    c = result.counts
    typer.echo(
        f"Loại mục: {sum(c.values())} mục · từ điển {c['map']} · khớp gần {c['map_fuzzy']} · "
        f"kế thừa {c['inherited']} · LLM {c['llm']} · chưa rõ {c['none']} "
        f"({result.llm_calls} lời gọi mới, ${result.llm_cost_usd:.6f})"
    )
    for p in result.proposals:
        typer.echo(f"  ⚑ chờ duyệt [{p.source}] '{p.titles[0]}' → {p.proposal} ({p.reason})")
    for w in result.warnings:
        typer.echo(f"  ⚠ {w}")
    if result.proposals:
        typer.echo("  → `dm p2 sections export`, điền decision, rồi `dm p2 sections import <csv>`")
    typer.echo(f"  đầu ra: {nodes_path} (cập nhật), {_proposals_path(settings).name}, tree.md")

    if evaluate:
        truth_path = truth or (settings.paths.raw_dir / settings.project.book_file).with_suffix(
            ".truth.json"
        )
        if not truth_path.is_file():
            typer.echo(f"Không có đáp án {truth_path} - chỉ đánh giá được với sách mẫu.", err=True)
            raise typer.Exit(1)
        pages = (min(b.page_start for b in blocks), max(b.page_end for b in blocks))
        report = eval_sections(nodes, json.loads(truth_path.read_text(encoding="utf-8")), pages)
        typer.echo("\n" + format_eval(report))
        if not all_pass(report):
            raise typer.Exit(1)


@sections_app.command("export")
def sections_export_cmd(root: Path | None = RootOption, out: Path | None = OutOption) -> None:
    """Xuất các đề xuất chờ duyệt ra CSV (mở bằng Excel)."""
    from dataminer.core.io import read_jsonl
    from dataminer.structure.section_mapper import SectionProposal, export_proposals

    settings = _load(root)
    src = _proposals_path(settings)
    if not src.is_file():
        typer.echo("Chưa có đề xuất - chạy `dm p2 sections map` trước.", err=True)
        raise typer.Exit(1)
    proposals = list(read_jsonl(src, SectionProposal))
    path = out or p2_dir(settings) / "section_proposals.csv"
    export_proposals(proposals, path)
    typer.echo(
        f"✓ {path}: {len(proposals)} đề xuất. Điền cột decision = accept | edit | skip "
        "(edit: ghi loại đúng vào edited_value)."
    )


@sections_app.command("import")
def sections_import_cmd(
    csv_path: Path, root: Path | None = RootOption, reviewer: str = ReviewerOption
) -> None:
    """Nhập CSV đã duyệt → GHI THÊM vào từ điển tên mục (chạy lại `map` để áp dụng)."""
    from dataminer.core.io import read_jsonl
    from dataminer.structure.section_mapper import (
        SectionMapError,
        SectionProposal,
        import_proposals,
    )

    settings = _load(root)
    src = _proposals_path(settings)
    if not src.is_file():
        typer.echo("Chưa có đề xuất - chạy `dm p2 sections map` trước.", err=True)
        raise typer.Exit(1)
    try:
        added = import_proposals(
            csv_path, list(read_jsonl(src, SectionProposal)), _map_path(settings), reviewer=reviewer
        )
    except SectionMapError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from None
    for key, value in added:
        typer.echo(f"  + {key}: {value}")
    typer.echo(
        f"✓ thêm {len(added)} khóa vào {_map_path(settings).name}. "
        "Chạy lại `dm p2 sections map` để áp dụng."
    )


CheckOption = typer.Option(False, "--check", help="Chỉ kiểm file golden hiện có với cây (G7).")


@p2_app.command("golden")
def golden_cmd(
    root: Path | None = RootOption, check: bool = CheckOption, truth: Path | None = TruthOption
) -> None:
    """Sinh (hoặc --check) bộ câu hỏi chuẩn eval/golden_qa_v1.jsonl từ cây + đáp án sách mẫu."""
    from dataminer.books.book01.golden import clean_texts, draft_golden
    from dataminer.core.io import read_jsonl, write_jsonl
    from dataminer.evaluation.golden import GOLDEN_VERSION, GoldenItem
    from dataminer.evaluation.truth.p1_eval import format_eval
    from dataminer.evaluation.truth.p2_eval import all_pass, eval_golden
    from dataminer.model.block import Block
    from dataminer.model.line import Line
    from dataminer.model.tree import Node
    from dataminer.pipeline.p1 import p1_dir

    settings = _load(root)
    nodes_path = p2_dir(settings) / "nodes.jsonl"
    if not nodes_path.is_file():
        typer.echo(
            f"Chưa có {nodes_path} - chạy `dm p2 tree` và `dm p2 sections map` trước.", err=True
        )
        raise typer.Exit(1)
    nodes = list(read_jsonl(nodes_path, Node))
    if not any(n.section_type for n in nodes):
        typer.echo("Cây chưa có loại mục - chạy `dm p2 sections map` trước.", err=True)
        raise typer.Exit(1)
    golden_path = settings.paths.eval_dir / f"golden_qa_{GOLDEN_VERSION}.jsonl"

    if check:
        if not golden_path.is_file():
            typer.echo(f"Chưa có {golden_path} - chạy `dm p2 golden` trước.", err=True)
            raise typer.Exit(1)
        items = list(read_jsonl(golden_path, GoldenItem))
    else:
        truth_path = truth or (settings.paths.raw_dir / settings.project.book_file).with_suffix(
            ".truth.json"
        )
        if not truth_path.is_file():
            typer.echo(
                f"Không có đáp án {truth_path}. Sinh tự động chỉ dùng cho sách mẫu; với sách thật "
                "câu hỏi phải do người chuyên môn viết (xem eval/README.md).",
                err=True,
            )
            raise typer.Exit(1)
        p1 = p1_dir(settings)
        blocks = list(read_jsonl(p1 / "blocks.jsonl", Block))
        lines = list(read_jsonl(p1 / "content_lines.jsonl", Line))
        texts = clean_texts(
            nodes, blocks, lines, json.loads(truth_path.read_text(encoding="utf-8"))
        )
        items = draft_golden(nodes, texts)

    report = eval_golden(items, nodes)
    g7 = report["G7_golden"]
    typer.echo(
        f"Golden {GOLDEN_VERSION}: {g7['items']} câu · cụ thể {g7['by_type']['specific']} · "
        f"liệt kê {g7['by_type']['list']} · từ chối {g7['by_type']['refusal']}"
    )
    typer.echo(format_eval(report))
    if not all_pass(report):
        typer.echo("✗ Bộ câu hỏi chưa đạt G7 - không ghi file.", err=True)
        raise typer.Exit(1)
    if check:
        typer.echo(f"✓ {golden_path} khớp với cây hiện tại.")
        return
    if golden_path.is_file():
        old = list(read_jsonl(golden_path, GoldenItem))
        if [i.model_dump() for i in old] == [i.model_dump() for i in items]:
            typer.echo(f"✓ {golden_path} đã có, nội dung không đổi.")
            return
        typer.echo(
            f"✗ {golden_path} đã khóa và khác bản vừa sinh. Quy tắc version (eval/README.md): "
            "không sửa câu cũ - tạo golden_qa_v2.jsonl.",
            err=True,
        )
        raise typer.Exit(1)
    write_jsonl(golden_path, items)
    typer.echo(f"✓ ghi {golden_path} ({len(items)} câu).")


@p2_app.command("run")
def run_cmd(root: Path | None = RootOption, no_llm: bool = NoLLMOption) -> None:
    """Chạy P2: mục lục → cấp tiêu đề → cây → loại mục → nodes.jsonl, tree.md (+ manifest)."""
    from dataminer.core.llm_types import LLMError
    from dataminer.core.prompts import PromptError
    from dataminer.pipeline.p2 import run_p2
    from dataminer.structure.section_mapper import SectionMapError
    from dataminer.structure.tree_builder import TreeInvariantError

    settings = _load(root)
    try:
        result = run_p2(settings, use_llm=not no_llm)
    except (
        FileNotFoundError,
        LLMError,
        PromptError,
        SectionMapError,
        TreeInvariantError,
        ConfigError,
    ) as exc:
        typer.echo(f"✗ {exc}", err=True)
        raise typer.Exit(1) from None
    c = result.counts
    typer.echo(
        f"✓ P2 xong: {c['nodes_chapter']} chương · {c['nodes_disease']} bệnh · "
        f"{c['nodes_section']} mục · {c['nodes_subsection']} mục con · {c['blocks']} block"
    )
    typer.echo(
        f"  mục lục {c['toc_entries']} mục · cấp tiêu đề: quy tắc {c['headings_rules']}, "
        f"mục lục {c['headings_toc']}, LLM {c['headings_llm']} · loại mục: từ điển "
        f"{c['sections_map']}, khớp gần {c['sections_map_fuzzy']}, kế thừa "
        f"{c['sections_inherited']}, LLM {c['sections_llm']}, chưa rõ {c['sections_none']}"
    )
    typer.echo(
        f"  chi phí LLM: ${result.llm_cost_usd:.6f} · đề xuất chờ duyệt {c['section_proposals']}"
        f" · manifest: {result.run_id}"
    )
    for w in result.warnings:
        typer.echo(f"  ⚠ {w}")
    typer.echo(f"  nodes.jsonl sha256 {result.nodes_sha256}")
    typer.echo(f"  đầu ra: {result.out_dir}")


@p2_app.command("eval")
def eval_cmd(root: Path | None = RootOption, truth: Path | None = TruthOption) -> None:
    """So với đáp án → eval.json + bảng chỉ tiêu G1-G7 (exit 1 nếu chưa đạt)."""
    from dataminer.core.io import write_json
    from dataminer.evaluation.golden import GOLDEN_VERSION
    from dataminer.evaluation.truth.p1_eval import format_eval
    from dataminer.evaluation.truth.p2_eval import all_pass, evaluate_p2
    from dataminer.pipeline.p1 import p1_dir

    settings = _load(root)
    truth_path = truth or (settings.paths.raw_dir / settings.project.book_file).with_suffix(
        ".truth.json"
    )
    if not truth_path.is_file():
        typer.echo(
            f"Không có đáp án {truth_path} - chỉ đánh giá tự động được với sách mẫu "
            "(sách thật: duyệt tay tree_report.md).",
            err=True,
        )
        raise typer.Exit(1)
    out = p2_dir(settings)
    if not (out / "nodes.jsonl").is_file():
        typer.echo("Chưa có kết quả P2 - chạy `dm p2 run` trước.", err=True)
        raise typer.Exit(1)
    golden = settings.paths.eval_dir / f"golden_qa_{GOLDEN_VERSION}.jsonl"
    report = evaluate_p2(
        out, p1_dir(settings), json.loads(truth_path.read_text(encoding="utf-8")), golden
    )
    write_json(out / "eval.json", report)
    typer.echo(format_eval(report))
    ok = all_pass(report)
    typer.echo(f"\nKẾT LUẬN: {'ĐẠT mọi chỉ tiêu G1-G7' if ok else 'CHƯA ĐẠT'}")
    if not ok:
        raise typer.Exit(1)


@p2_app.command("report")
def report_cmd(root: Path | None = RootOption) -> None:
    """Sinh data/p2_tree/tree_report.md (tổng quan, đối chiếu mục lục, ma trận, cảnh báo, cây)."""
    from dataminer.structure.report import render_tree_report

    out = p2_dir(_load(root))
    if not (out / "manifest.json").is_file():
        typer.echo("Chưa có kết quả P2 - chạy `dm p2 run` trước.", err=True)
        raise typer.Exit(1)
    (out / "tree_report.md").write_text(render_tree_report(out), encoding="utf-8")
    typer.echo(f"✓ {out / 'tree_report.md'}")


# ---------------------------------------------------------------- P2R I5: soát tay

spotcheck_app = typer.Typer(
    help="Soát tay (A9): trang HTML ảnh trang PDF ↔ nội dung đã tách, phiếu chấm, bảng bệnh."
)
p2_app.add_typer(spotcheck_app, name="spotcheck")


SampleSizeOption = typer.Option(None, "--n", help="Cỡ mẫu (mặc định p2.spotcheck.n).")
SeedOption = typer.Option(None, "--seed", help="Hạt giống chọn mẫu (mặc định p2.spotcheck.seed).")
CodesOption = typer.Option("", "--codes", help="Xem thêm (không tính A9): mã, cách nhau ','.")
DpiOption = typer.Option(None, "--dpi", help="Độ phân giải ảnh trang (mặc định p2.spotcheck.dpi).")
ReviewFileOption = typer.Option(
    None, "--file", help="Phiếu chấm (mặc định spotcheck/review.csv; hoặc file tải từ trang soát)."
)


def _spotcheck_dir(settings: Settings) -> Path:
    return p2_dir(settings) / "spotcheck"


@spotcheck_app.callback(invoke_without_command=True)
def spotcheck_cmd(
    ctx: typer.Context,
    root: Path | None = RootOption,
    n: int | None = SampleSizeOption,
    seed: int | None = SeedOption,
    codes: str = CodesOption,
    dpi: int | None = DpiOption,
) -> None:
    """Chọn mẫu ngẫu nhiên → spotcheck/index.html + review.csv; bảng mọi bệnh <unit_name>.csv."""
    if ctx.invoked_subcommand is not None:
        return
    from dataminer.books.registry import rules_for
    from dataminer.core.io import read_jsonl, sha256_file, write_json
    from dataminer.evaluation import spotcheck as sc
    from dataminer.evaluation.spotcheck_page import render_html, render_page_images
    from dataminer.model.block import Block
    from dataminer.model.line import Line
    from dataminer.model.tree import Node
    from dataminer.pipeline.p1 import p1_dir
    from dataminer.structure.section_mapper import SECTION_TYPES

    settings = _load(root)
    cfg = settings.p2.spotcheck
    n, seed, dpi = n or cfg.n, cfg.seed if seed is None else seed, dpi or cfg.dpi
    nodes_path = p2_dir(settings) / "nodes.jsonl"
    pdf = settings.paths.raw_dir / settings.project.book_file
    needed = (nodes_path, p1_dir(settings) / "blocks.jsonl", p1_dir(settings) / "lines.jsonl", pdf)
    for path in needed:
        if not path.is_file():
            typer.echo(f"Chưa có {path} - chạy `dm p1 run` và `dm p2 run` trước.", err=True)
            raise typer.Exit(1)
    nodes = list(read_jsonl(nodes_path, Node))
    blocks = {b.id: b for b in read_jsonl(p1_dir(settings) / "blocks.jsonl", Block)}
    lines = {ln.id: ln for ln in read_jsonl(p1_dir(settings) / "lines.jsonl", Line)}
    tree = sc.Tree(nodes)
    units = rules_for(settings).review_units(nodes)
    if not units:
        typer.echo("Cây không có bệnh nào để soát.", err=True)
        raise typer.Exit(1)

    sample = sc.choose_sample(units, tree, n, seed)
    wanted = [c.strip() for c in codes.split(",") if c.strip()]
    by_code = {c.strip(): u for u in units for c in sc.code_of(u).split(",") if c.strip()}
    unknown = [c for c in wanted if c not in by_code and c not in tree.by_id]
    if unknown:
        typer.echo(f"Không có bệnh mã {', '.join(unknown)}.", err=True)
        raise typer.Exit(1)
    chosen = {u.id for u in sample}
    extra_ids = [u.id for u in units if not sc.eligible(u)]
    extra_ids += [(by_code.get(c) or tree.by_id[c]).id for c in wanted]
    extras = [u for u in units if u.id in set(extra_ids) - chosen]

    out = _spotcheck_dir(settings)
    views = [sc.build_view(u, tree, blocks, lines) for u in sample]
    extra_views = [sc.build_view(u, tree, blocks, lines) for u in extras]
    pages = sorted({p for v in [*views, *extra_views] for p in v.pages})
    render_page_images(pdf, pages, dpi, out)
    nodes_sha = sha256_file(nodes_path)
    meta = {
        "book_id": settings.project.book_id,
        "nodes_sha256": nodes_sha,
        "seed": seed,
        "n": n,
        "dpi": dpi,
        "sample": [u.id for u in sample],
        "extras": [u.id for u in extras],
    }
    unit_label = "hội chứng" if cfg.unit_name == "syndromes" else "bệnh"
    page = render_html(
        views, extra_views, book_title=settings.project.book_id, unit_label=unit_label, meta=meta
    )
    (out / "index.html").write_text(page, encoding="utf-8")
    write_json(out / "meta.json", meta)

    review = out / "review.csv"
    kept = False
    if review.is_file():
        try:
            rows = sc.read_review(review)
            kept = any(r.get(c, "").strip() for r in rows for c in sc.CRITERIA)
        except sc.SpotcheckError:
            kept = False
    if kept:
        typer.echo(f"  ⚠ giữ nguyên {review} (đã có điểm chấm) - xóa file nếu muốn phiếu mới.")
    else:
        sc.write_csv(review, sc.REVIEW_COLUMNS, sc.review_rows(views))

    used = [t for t in SECTION_TYPES if any(x.section_type == t for x in nodes)]
    columns, rows = sc.units_table(units, tree, used)
    table = p2_dir(settings) / f"{cfg.unit_name}.csv"
    sc.write_csv(table, columns, rows)

    typer.echo(
        f"✓ {len(sample)} {unit_label} ngẫu nhiên (seed {seed}) + {len(extras)} xem thêm · "
        f"{len(pages)} trang ảnh ({dpi} dpi)"
    )
    for v in views:
        typer.echo(f"  · {v.code or '-':>10}  {v.title}  (PDF {v.pages[0] if v.pages else '-'})")
    typer.echo(f"  mở: {out / 'index.html'}")
    typer.echo(f"  phiếu chấm: {review} · bảng {len(units)} {unit_label}: {table}")


@spotcheck_app.command("score")
def spotcheck_score_cmd(
    root: Path | None = RootOption,
    file: Path | None = ReviewFileOption,
) -> None:
    """Chấm A9 từ phiếu: đạt khi ≥ min_pass bệnh đúng cả 4 tiêu chí. Exit 1 nếu chưa đạt."""
    from dataminer.core.io import read_json, sha256_file
    from dataminer.evaluation import spotcheck as sc

    settings = _load(root)
    out = _spotcheck_dir(settings)
    if not (out / "meta.json").is_file():
        typer.echo("Chưa có trang soát - chạy `dm p2 spotcheck` trước.", err=True)
        raise typer.Exit(1)
    meta = read_json(out / "meta.json")
    try:
        rows = sc.read_review(file or out / "review.csv")
        result = sc.score(rows, meta["sample"], settings.p2.spotcheck.min_pass)
    except sc.SpotcheckError as exc:
        typer.echo(f"✗ {exc}", err=True)
        raise typer.Exit(1) from None
    nodes_path = p2_dir(settings) / "nodes.jsonl"
    stale = nodes_path.is_file() and sha256_file(nodes_path) != meta["nodes_sha256"]
    lines = [f"# Soát tay (A9) - {settings.project.book_id}", "", f"- {result.check.line()}"]
    if stale:
        lines.append(
            "- ⚠ cây đã được chạy lại SAU khi sinh trang soát - phiếu này chấm bản cây cũ; "
            "chạy lại `dm p2 spotcheck` rồi soát lại."
        )
    lines += [f"- chưa chấm: {u}" for u in result.unscored]
    lines += [f"- sai: {f}" for f in result.failed]
    (out / "score.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines[2:]:
        typer.echo(line.removeprefix("- "))
    if not result.check.passed or stale:
        raise typer.Exit(1)
