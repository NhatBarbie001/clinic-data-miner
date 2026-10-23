"""Sinh samples/P2.2/heading_levels.md, heading_eval.txt, edge_cases.md từ dữ liệu hiện có.
Chạy sau `dm p1 run` + `dm p2 headings`: uv run python samples/P2.2/scripts/render_samples.py"""

import json
from pathlib import Path

from dataminer.core.io import read_jsonl
from dataminer.evaluation.p1_eval import format_eval
from dataminer.evaluation.p2_eval import eval_heading_levels
from dataminer.ingest.blocks import is_upper_text, numbering_of
from dataminer.model.block import Block
from dataminer.model.toc import TocEntry
from dataminer.model.tree import HeadingDecision
from dataminer.structure.heading_levels import classify_headings
from dataminer.structure.toc import norm_title

OUT = Path("samples/P2.2")
blocks = list(read_jsonl(Path("data/p1_clean/blocks.jsonl"), Block))
by_id = {b.id: b for b in blocks}
decisions = list(read_jsonl(Path("data/p2_tree/heading_levels.jsonl"), HeadingDecision))
truth = json.loads(Path("data/raw/book01.truth.json").read_text(encoding="utf-8"))
pages = (min(b.page_start for b in blocks), max(b.page_end for b in blocks))
(OUT / "heading_eval.txt").write_text(
    "Đánh giá G2 (sách mẫu seed 7, pilot trang PDF 4-9) - dm p2 headings --eval\n\n"
    + format_eval(eval_heading_levels(decisions, truth, pages))
    + "\n",
    encoding="utf-8",
)

rows = [
    "# Cấp tiêu đề - pilot sách mẫu (seed 7)\n",
    "Đầu vào: 27 block `heading` của P1 (`data/p1_clean/blocks.jsonl`) + `toc.json` (P2.1).\n",
    "| # | Trang | Tiêu đề | Cỡ | IN HOA | Số | → Cấp | Tin cậy | Nguồn | Lý do |",
    "|---|---|---|---|---|---|---|---|---|---|",
]
for i, d in enumerate(decisions, 1):
    b = by_id[d.block_id]
    rows.append(
        f"| {i} | {d.page} | `{d.text}` | {b.font_size} | {'✓' if b.is_upper else ''} | "
        f"{d.numbering or ''} | **{d.level}** | {d.confidence} | {d.source} | "
        f"{' · '.join(d.reasons)} |"
    )
(OUT / "heading_levels.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

# ----------------------------- tình huống ngoài sách mẫu (block tự dựng, không LLM)
n = 0


def hb(text: str, size: float, page: int = 4) -> Block:
    global n
    n += 1
    return Block(
        id=f"h{n}",
        kind="heading",
        text=text,
        text_rules=text,
        page_start=page,
        page_end=page,
        line_ids=[],
        bbox=(48, 0, 300, 13),
        x0=48,
        font_size=size,
        is_upper=is_upper_text(text),
        numbering=numbering_of(text),
    )


def para(page: int = 4) -> Block:
    global n
    n += 1
    t = "Nội dung thân bài của mục, đủ dài để làm cỡ chữ chuẩn."
    return Block(
        id=f"p{n}",
        kind="paragraph",
        text=t,
        text_rules=t,
        page_start=page,
        page_end=page,
        line_ids=[],
        bbox=(48, 0, 300, 13),
        x0=48,
        font_size=10.5,
    )


def entry(title: str, level: str, pdf_page: int) -> TocEntry:
    return TocEntry(
        title=title,
        title_norm=norm_title(title),
        level=level,  # type: ignore[arg-type]
        printed_page=pdf_page - 3,
        pdf_page=pdf_page,
        toc_pdf_page=3,
        line_id="x",
        x0=48,
    )


demo = [
    hb("CHUONG 3. BENH THAN", 14, 10),
    hb("SỎI THẬN", 13.5, 10),
    hb("1. ĐẠI CƯƠNG", 12, 10),
    para(10),
    hb("2. NGUYÊN NHÂN", 12, 10),
    para(10),
    hb("LƯU Ý", 10.6, 10),
    para(10),
    hb("4. ĐIỀU TRỊ", 12, 11),
    para(11),
    hb("4.2. Ngoại khoa", 10.6, 11),
    para(11),
    hb("HEN PHẾ QUẢN", 13, 12),
    hb("1. ĐẠI CƯƠNG", 12, 12),
    para(12),
]
toc = [
    entry("Chương 3. Bệnh thận", "chapter", 10),
    entry("Sỏi thận", "disease", 10),
    entry("Gout", "disease", 12),
]
res = classify_headings(demo, toc)
lines = [
    "# Tình huống ngoài sách mẫu (block tự dựng, chạy thật bằng `classify_headings`, KHÔNG LLM)\n",
    "Mục lục giả lập: `Chương 3. Bệnh thận` (PDF 10), `Sỏi thận` (PDF 10), `Gout` (PDF 12).\n",
    "| Trang | Tiêu đề | Cỡ | → Cấp | Tin cậy | Nguồn | Cờ | Lý do |",
    "|---|---|---|---|---|---|---|---|",
]
size_of = {b.id: b.font_size for b in demo}
for d in res.decisions:
    lines.append(
        f"| {d.page} | `{d.text}` | {size_of[d.block_id]} | **{d.level}** | {d.confidence} | "
        f"{d.source} | {', '.join(d.flags)} | {' · '.join(d.reasons)} |"
    )
lines.append("\n**Cảnh báo:**\n")
lines += [f"- {w}" for w in res.warnings]
lines.append(
    "\nGhi chú: chạy thật (có LLM), 2 tiêu đề tin cậy `low` (`LƯU Ý`, `HEN PHẾ QUẢN`) sẽ được "
    "hỏi LLM (tác vụ `classify`); ở đây tắt LLM để minh họa lớp 1-2. Đường LLM được kiểm bằng "
    "LLM giả lập trong test #8.\n"
)
(OUT / "edge_cases.md").write_text("\n".join(lines), encoding="utf-8")
print("ok")
