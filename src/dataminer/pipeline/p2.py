"""P2.6 - Chạy cả phase P2: mục lục → cấp tiêu đề → cây → loại mục, có manifest.

`nodes.jsonl` chỉ phụ thuộc `blocks.jsonl` (P1), PDF (mục lục), cấu hình và từ điển tên mục →
chạy lại cho kết quả giống hệt từng byte (G8). LLM chỉ được gọi cho tiêu đề / tên mục mơ hồ; trên
sách mẫu: 0 lời gọi. Xem docs/phases/P2/P2.6_plan.md.
"""

from pathlib import Path

from pydantic import BaseModel

from dataminer.core.config import Settings
from dataminer.core.io import read_jsonl, sha256_file, write_json, write_jsonl
from dataminer.core.llm_client import LLMClient
from dataminer.core.prompts import load_prompt
from dataminer.core.run import RunRecorder
from dataminer.model.block import Block
from dataminer.structure.heading_levels import classify_headings
from dataminer.structure.section_mapper import load_section_map, map_sections
from dataminer.structure.toc import extract_toc
from dataminer.structure.tree_builder import build_tree, render_tree_md, to_nested

PHASE = "p2_tree"
OUTPUTS = (
    "toc.json",
    "heading_levels.jsonl",
    "nodes.jsonl",
    "tree.json",
    "tree.md",
    "section_proposals.jsonl",
)


class P2Result(BaseModel):
    out_dir: str
    run_id: str
    counts: dict[str, int]
    warnings: list[str]
    llm_cost_usd: float
    nodes_sha256: str


def p2_dir(settings: Settings) -> Path:
    return settings.paths.data_dir / PHASE


def run_p2(
    settings: Settings, *, use_llm: bool = True, client: LLMClient | None = None
) -> P2Result:
    """Chạy P2 trên đầu ra của P1 (`data/p1_clean/blocks.jsonl`)."""
    from dataminer.pipeline.p1 import p1_dir

    blocks_path = p1_dir(settings) / "blocks.jsonl"
    if not blocks_path.is_file():
        raise FileNotFoundError(f"Chưa có {blocks_path} - chạy `dm p1 run` trước.")
    pdf = settings.paths.raw_dir / settings.project.book_file
    if not pdf.is_file():
        raise FileNotFoundError(f"Không thấy {pdf} (cần để đọc trang mục lục).")
    root = settings.paths.data_dir.parent
    cfg = settings.p2
    map_path = root / cfg.sections.map
    out = p2_dir(settings)
    warnings: list[str] = []

    with RunRecorder(settings, PHASE, out_dir=out) as run:
        for path, records in ((blocks_path, True), (pdf, False), (map_path, False)):
            run.add_input(path, records=records)
        blocks = list(read_jsonl(blocks_path, Block))

        # P2.1 mục lục
        toc = extract_toc(
            pdf, book_id=settings.project.book_id, cfg=cfg.toc, furniture=settings.p1.furniture
        )
        write_json(out / "toc.json", toc.model_dump(mode="json"))
        warnings += [f"mục lục: {w}" for w in toc.warnings]

        # P2.2 cấp tiêu đề (LLM chỉ cho tiêu đề tin cậy thấp)
        llm_headings = use_llm and cfg.headings.llm_fallback
        llm_sections = use_llm and cfg.sections.llm_fallback
        if (llm_headings or llm_sections) and client is None:
            client = LLMClient(settings)
        prompts = settings.paths.prompts_dir
        heading_prompt = load_prompt(prompts, cfg.headings.prompt) if llm_headings else None
        headings = classify_headings(
            blocks, toc.entries, cfg.headings, client=client, prompt=heading_prompt
        )
        write_jsonl(out / "heading_levels.jsonl", headings.decisions)
        warnings += [f"cấp tiêu đề: {w}" for w in headings.warnings]
        if headings.prompt and heading_prompt:
            run.use_prompt(heading_prompt.id, heading_prompt.version)

        # P2.3 cây
        tree = build_tree(
            blocks, headings.decisions, book_id=settings.project.book_id, toc=toc.entries
        )
        warnings += [f"cây: {w}" for w in tree.warnings]

        # P2.4 loại mục (LLM chỉ cho tên mục lạ)
        section_prompt = load_prompt(prompts, cfg.sections.prompt) if llm_sections else None
        sections = map_sections(
            tree.nodes,
            load_section_map(map_path),
            cfg.sections,
            client=client,
            prompt=section_prompt,
        )
        warnings += [f"loại mục: {w}" for w in sections.warnings]
        if sections.prompt and section_prompt:
            run.use_prompt(section_prompt.id, section_prompt.version)

        nodes = tree.nodes
        write_jsonl(out / "nodes.jsonl", nodes)
        write_jsonl(out / "section_proposals.jsonl", sections.proposals)
        write_json(out / "tree.json", to_nested(nodes))
        (out / "tree.md").write_text(render_tree_md(nodes, blocks), encoding="utf-8")

        for name in OUTPUTS:
            run.add_output(out / name, records=name.endswith(".jsonl"))
        levels = [n.level for n in nodes]
        counts = {
            "blocks": len(blocks),
            "toc_entries": len(toc.entries),
            "headings": len(headings.decisions),
            "headings_rules": sum(d.source == "rules" for d in headings.decisions),
            "headings_toc": sum(d.source == "toc" for d in headings.decisions),
            "headings_llm": sum(d.source == "llm" for d in headings.decisions),
            "nodes": len(nodes),
            **{
                f"nodes_{lv}": levels.count(lv)
                for lv in ("chapter", "disease", "section", "subsection", "front")
            },
            **{f"sections_{k}": v for k, v in sections.counts.items()},
            "section_proposals": len(sections.proposals),
            "warnings": len(warnings),
        }
        for key, value in counts.items():
            run.count(key, value)
        for w in warnings:
            run.note(w)
        nodes_sha = sha256_file(out / "nodes.jsonl")
        run.note(f"nodes.jsonl sha256 {nodes_sha}")

    return P2Result(
        out_dir=str(out),
        run_id=run.run_id,
        counts=counts,
        warnings=warnings,
        llm_cost_usd=run.manifest.llm.cost_usd,
        nodes_sha256=nodes_sha,
    )
