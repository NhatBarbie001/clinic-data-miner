"""P2.6 - Báo cáo cấu trúc `tree_report.md`: để người đọc kiểm tra cây trong vài phút.

1. Tổng quan (số nút, mỗi bệnh: trang/block/từ; nguồn của cấp tiêu đề và loại mục)
2. Đối chiếu mục lục ↔ cây (cả hai chiều)
3. Ma trận bệnh × loại mục (P4 biết trường nào có thể trống)
4. Cảnh báo cần người xem (nút rỗng, mục quá dài/ngắn, cờ, loại mục từ LLM/khớp gần…)
5. Cây (tree.md)
"""

import statistics
from pathlib import Path

from dataminer.core.io import read_json, read_jsonl
from dataminer.evaluation.truth.p2_eval import GATE_NAMES
from dataminer.model.toc import TocResult
from dataminer.model.tree import HeadingDecision, Node
from dataminer.structure.section_mapper import SECTION_TYPES

LONG_FACTOR = 4.0  # mục dài hơn 4 × trung vị → có thể nuốt mất tiêu đề kế tiếp
SHORT_FACTOR = 0.25  # mục ngắn hơn 1/4 trung vị → có thể bị cắt
INFO_FLAGS = frozenset({"level_from_llm", "other_heading"})  # ℹ thông tin; còn lại ⚠
FLAG_HINTS = {
    "empty": "nút không có nội dung và không có con",
    "missing_from_toc": "không có trong mục lục - kiểm tra tiêu đề có bị OCR đọc sai không",
    "toc_page_mismatch": "trang khác trang ghi trong mục lục",
    "numbering_gap": "số thứ tự mục nhảy - có thể sót tiêu đề",
    "orphan_subsection": "mục con không có mục cha",
    "orphan_section": "mục không thuộc bệnh nào",
    "other_heading": "có tiêu đề cấp 'other' bị gộp vào nội dung",
    "duplicate_path": "trùng tên mục với một mục khác cùng bệnh",
    "level_from_llm": "cấp tiêu đề do LLM quyết định",
    "section_type_from_llm": "loại mục do LLM đề xuất - duyệt bằng `dm p2 sections export`",
    "section_type_fuzzy": "loại mục từ khớp gần - duyệt bằng `dm p2 sections export`",
    "section_type_unknown": "chưa xác định được loại mục ('other')",
}


def _words(text: str) -> int:
    return len(text.split())


def render_tree_report(out_dir: Path) -> str:
    manifest = read_json(out_dir / "manifest.json")
    nodes = list(read_jsonl(out_dir / "nodes.jsonl", Node))
    decisions = list(read_jsonl(out_dir / "heading_levels.jsonl", HeadingDecision))
    toc = TocResult.model_validate_json((out_dir / "toc.json").read_text(encoding="utf-8"))
    kids: dict[str, list[Node]] = {}
    for n in nodes:
        kids.setdefault(n.parent_id or "", []).append(n)

    def subtree(n: Node) -> list[Node]:
        out = [n]
        for c in kids.get(n.id, []):
            out += subtree(c)
        return out

    counts = manifest.get("counts", {})
    llm = manifest["llm"]
    prompts = ", ".join(f"{k}@{v}" for k, v in manifest.get("prompts", {}).items()) or "không"
    diseases = [n for n in nodes if n.level == "disease"]
    git = (manifest.get("git_commit") or "")[:7]
    lines = [
        "# Báo cáo cấu trúc P2: cây chương → bệnh → mục",
        "",
        "## 1. Tổng quan",
        "",
        f"- Lần chạy `{manifest['run_id']}` · **{manifest['status']}** · "
        f"{manifest.get('duration_s')}s · git `{git}` · LLM: {llm['calls']} lời gọi, "
        f"${llm['cost_usd']:.6f} · prompt dùng: {prompts}",
        f"- Cây: **{counts.get('nodes_chapter', 0)} chương · {len(diseases)} bệnh · "
        f"{counts.get('nodes_section', 0)} mục · {counts.get('nodes_subsection', 0)} mục con**"
        + (" · có phần đầu" if counts.get("nodes_front") else "")
        + f" · {counts.get('blocks', 0)} block",
        f"- Cấp tiêu đề: quy tắc {counts.get('headings_rules', 0)} · xác nhận/sửa bằng mục lục "
        f"{counts.get('headings_toc', 0)} · LLM {counts.get('headings_llm', 0)}",
        f"- Loại mục: từ điển {counts.get('sections_map', 0)} · khớp gần "
        f"{counts.get('sections_map_fuzzy', 0)} · kế thừa {counts.get('sections_inherited', 0)} · "
        f"LLM {counts.get('sections_llm', 0)} · chưa rõ {counts.get('sections_none', 0)}",
        "",
        "| Bệnh | Trang PDF | Trang in | Mục / mục con | Block | Số từ |",
        "|---|---|---|---|---|---|",
    ]
    for d in diseases:
        tree = subtree(d)
        secs = [n for n in tree if n.level in ("section", "subsection")]
        blocks = sum(len(n.block_ids) + (n.heading_block_id is not None) for n in tree)
        lines.append(
            f"| {d.display_title} | {d.page_start}–{d.page_end} | "
            f"{d.printed_start}–{d.printed_end} | {len(secs)} | {blocks} | "
            f"{sum(_words(n.text) for n in tree)} |"
        )

    # ------------------------------------------------ 2. mục lục
    lines += ["", "## 2. Đối chiếu mục lục", ""]
    if not toc.entries:
        lines.append("Không có mục lục (`toc.json` rỗng) - không đối chiếu được.")
    else:
        lo = min((n.page_start for n in nodes if n.page_start), default=0)
        hi = max((n.page_end for n in nodes), default=0)
        node_by_heading = {n.heading_block_id: n for n in nodes if n.heading_block_id}
        in_toc = {e.title_norm for e in toc.entries}  # chỉ tính mục lục HIỆN TẠI của toc.json
        node_of = {
            d.toc_match: node_by_heading[d.block_id]
            for d in decisions
            if d.toc_match in in_toc and d.block_id in node_by_heading
        }
        lines += [
            f"Trang mục lục: PDF {toc.toc_pages} · trang PDF = trang in {toc.page_offset:+d}"
            if toc.page_offset is not None
            else f"Trang mục lục: PDF {toc.toc_pages}",
            "",
            "| Mục lục | Cấp | Tr.in (mục lục) | Nút trong cây | Trang khớp |",
            "|---|---|---|---|---|",
        ]
        for e in toc.entries:
            hit = node_of.get(e.title_norm)
            if e.pdf_page is None or not lo <= e.pdf_page <= hi:
                where, page_ok = "*(ngoài phạm vi đã xử lý)*", "-"
            elif hit is None:
                where, page_ok = "✗ **không tìm thấy**", "-"
            else:
                where = f"✓ {hit.display_title}"
                page_ok = (
                    f"✓ PDF {hit.page_start}"
                    if hit.page_start == e.pdf_page
                    else f"✗ cây PDF {hit.page_start} ≠ {e.pdf_page}"
                )
            lines.append(f"| {e.title} | {e.level} | {e.printed_page} | {where} | {page_ok} |")
        extra = [
            n for n in nodes if n.level in ("chapter", "disease") and n not in node_of.values()
        ]
        lines.append("")
        lines.append(
            "Nút chương/bệnh trong cây nhưng **không có trong mục lục**: "
            + (", ".join(f"`{n.display_title}`" for n in extra) if extra else "không có.")
        )

    # ------------------------------------------------ 3. ma trận
    have = {d.id: {n.section_type for n in subtree(d) if n.section_type} for d in diseases}
    present = [t for t in SECTION_TYPES if t != "other" and any(t in h for h in have.values())]
    absent = [t for t in SECTION_TYPES if t != "other" and t not in present]
    lines += [
        "",
        "## 3. Ma trận bệnh × loại mục",
        "",
        "| Bệnh | " + " | ".join(present) + " |",
        "|---|" + "---|" * len(present),
    ]
    for d in diseases:
        lines.append(
            f"| {d.display_title} | "
            + " | ".join("✓" if t in have[d.id] else "—" for t in present)
            + " |"
        )
    partial = [t for t in present if not all(t in h for h in have.values())]
    lines += [
        "",
        f"- Loại mục **chỉ có ở một số bệnh** (P4 phải chấp nhận trường trống): "
        f"{', '.join(f'`{t}`' for t in partial) or 'không có'}",
        f"- Loại mục **không bệnh nào có**: {', '.join(f'`{t}`' for t in absent) or 'không có'}",
    ]

    # ------------------------------------------------ 4. cảnh báo
    warnings: list[tuple[str, str, str]] = []  # (mức, nút, nội dung)
    for n in nodes:
        for f in n.flags:
            level = "ℹ" if f in INFO_FLAGS else "⚠"
            where = " › ".join(n.path) or n.title
            warnings.append((level, where, f"`{f}`: {FLAG_HINTS.get(f, f)}"))
    for dec in decisions:
        if "numbering_gap" in dec.flags:
            warnings.append(("⚠", dec.text, f"`numbering_gap`: {FLAG_HINTS['numbering_gap']}"))
    sized = [(n, _words(n.text)) for n in nodes if n.level in ("section", "subsection") and n.text]
    if len(sized) >= 4:
        median = statistics.median(w for _, w in sized)
        for n, w in sized:
            if w > LONG_FACTOR * median:
                warnings.append(
                    (
                        "⚠",
                        " › ".join(n.path),
                        f"dài {w} từ (> {LONG_FACTOR:g} × trung vị {median:g}) - "
                        "có thể nuốt tiêu đề kế tiếp",
                    )
                )
            elif w < SHORT_FACTOR * median:
                warnings.append(
                    (
                        "ℹ",
                        " › ".join(n.path),
                        f"ngắn {w} từ (< {SHORT_FACTOR:g} × trung vị {median:g}) - "
                        "kiểm tra có bị cắt không",
                    )
                )
    notes = [x for x in manifest.get("notes", []) if not x.startswith("nodes.jsonl sha256")]
    lines += ["", "## 4. Cảnh báo cần người xem", ""]
    if warnings or notes:
        lines += ["| Mức | Nút | Nội dung |", "|---|---|---|"]
        lines += [f"| {lv} | {where} | {what} |" for lv, where, what in warnings]
        lines += [f"| ⚠ | (lần chạy) | {x} |" for x in notes]
    else:
        lines.append("✅ Không có cảnh báo: không nút rỗng, không cờ, không mục quá dài/ngắn, "
                     "không ghi chú nào từ lần chạy.")  # fmt: skip

    # ------------------------------------------------ 5. chỉ tiêu + cây
    eval_path = out_dir / "eval.json"
    if eval_path.is_file():
        report = read_json(eval_path)
        lines += [
            "",
            "## Chỉ tiêu (so với đáp án sách mẫu)",
            "",
            "| Chỉ tiêu | Kết quả |",
            "|---|---|",
        ]
        lines += [
            f"| {name} | {'✅' if report[key].get('pass') else '❌'} |"
            for key, name in GATE_NAMES.items()
            if key in report
        ]
    tree_md = (out_dir / "tree.md").read_text(encoding="utf-8").rstrip()
    lines += ["", "## 5. Cây", "", "```", tree_md, "```", ""]
    return "\n".join(lines)
