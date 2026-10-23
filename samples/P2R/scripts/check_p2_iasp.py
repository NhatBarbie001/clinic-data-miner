"""Kiểm I3 (cây IASP) + sinh mẫu samples/P2R/I3/.

Chạy sau `dm --book iasp p1 run --scope all && dm --book iasp p2 run`:
    uv run python samples/P2R/scripts/check_p2_iasp.py [blocks_I2.jsonl]
A3 đếm mã hội chứng ĐỘC LẬP trên PDF bằng PyMuPDF (không dùng code P1/P2/books.iasp).
Tham số tùy chọn: blocks.jsonl của I2 (trước khi sửa luật nối tiêu đề) → heading_merges.md.
"""

import re
import sys
from pathlib import Path

import pymupdf as fitz

from dataminer.books.iasp.headings import code_of, is_syndrome
from dataminer.core.io import read_jsonl
from dataminer.evaluation.checks import code_sequence, count_match, section_coverage
from dataminer.model.block import Block
from dataminer.model.tree import Node
from dataminer.structure.tree_builder import check_invariants

PDF = Path("data/books/iasp/raw/classification_of_chronic_pain.pdf")
P1 = Path("data/books/iasp/p1_clean")
P2 = Path("data/books/iasp/p2_tree")
OUT = Path("samples/P2R/I3")
PAGES = range(53, 223)  # Part II
# mã hội chứng trong chữ đậm cỡ lớn; mã có thể vắt dòng "(11-" ↵ "13)" → đếm trên cả trang
RE_CODE = re.compile(r"\(\s*[0-9IVXLC]+\s*-\s*[0-9Il]+(\.[0-9Il]+)?\s*\)")
REQUIRED = re.compile(r"^(Definition|Codes?\b|Code\(s\))")
# chỗ SÁCH tự nhảy mã (đã soát trên PDF, xem docs/phases/P2R/I3_report.md):
BOOK_GAPS = (
    "XXIV-6→XXIV-8",  # PDF 185: thiếu dòng tên "Retroversion of the Uterus (XXIV-7)"
    "XXIX-4→XXIX-4.2",  # PDF 209: sách chỉ mô tả XXIX-4.2 (4.1, 4.3, 4.4 chỉ có trong danh mục)
)

# ---------------------------------------------------------------- đếm độc lập trên PDF
pdf_codes = 0
with fitz.open(PDF) as doc:
    for pno in PAGES:
        big_bold = [
            s["text"]
            for block in doc[pno - 1].get_text("dict")["blocks"]
            for line in block.get("lines", [])
            for s in line["spans"]
            if s["size"] >= 12 and s["flags"] & 16
        ]
        pdf_codes += len(RE_CODE.findall(" ".join(big_bold)))

# ---------------------------------------------------------------- cây
blocks = list(read_jsonl(P1 / "blocks.jsonl", Block))
nodes = list(read_jsonl(P2 / "nodes.jsonl", Node))
kids: dict[str, list[Node]] = {}
for n in nodes:
    if n.parent_id:
        kids.setdefault(n.parent_id, []).append(n)
syndromes = [n for n in nodes if is_syndrome(n)]
codes = [c for n in syndromes for c in (n.attrs.get("codes") or [code_of(n)]) if c]

results = [
    code_sequence(codes, BOOK_GAPS),
    count_match(len(codes), pdf_codes),
    section_coverage(syndromes, lambda s: kids.get(s.id, []), REQUIRED),
]
problems = check_invariants(nodes, blocks)
levels = {lv: sum(n.level == lv for n in nodes) for lv in
          ("part", "chapter", "disease", "section", "subsection", "front")}  # fmt: skip
with_iasp = sum("iasp_codes" in n.attrs for n in syndromes)
report = [
    f"Cây Part II: {len(nodes)} nút · " + " · ".join(f"{k} {v}" for k, v in levels.items()),
    f"Hội chứng: {len(syndromes)} nút, {len(codes)} mã"
    f" (nút không mã {sum('no_code' in n.flags for n in syndromes)})"
    f" · có mã IASP 5 trục: {with_iasp}",
    "",
    *(r.line() + "".join(f"\n    - {d}" for d in r.details) for r in results),
    f"A8 bất biến cây: {len(problems)} vi phạm → {'ĐẠT' if not problems else 'CHƯA ĐẠT'}",
    *(f"    - {p}" for p in problems),
]
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "p2_checks.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))

# ---------------------------------------------------------------- mẫu: GROUP XI
tree = (P2 / "tree.md").read_text(encoding="utf-8").splitlines()
start = next(i for i, ln in enumerate(tree) if "GROUP XI:" in ln)
indent = tree[start].index("GROUP")
end = next(
    (i for i in range(start + 1, len(tree)) if tree[i].index(tree[i].lstrip("│ ├└─")) <= indent),
    len(tree),
)
(OUT / "tree_group_xi.md").write_text(
    "# Cây GROUP XI (pilot, PDF 137-143)\n\n```\n" + "\n".join(tree[start:end]) + "\n```\n",
    encoding="utf-8",
)

# ---------------------------------------------------------------- mẫu: mọi hội chứng
by_id = {n.id: n for n in nodes}
rows = [
    "# Mọi hội chứng của Part II\n",
    "| # | Mã | Tên | GROUP | Trang PDF | Số mục | Mã IASP 5 trục | Cờ |",
    "|---|---|---|---|---|---|---|---|",
]
for i, s in enumerate(syndromes, 1):
    parent = by_id.get(s.parent_id or "")
    group = s.numbering if s.level == "chapter" else (parent.numbering if parent else "")
    flags = ", ".join(f for f in s.flags if f not in ("section_type_unknown",))
    rows.append(
        f"| {i} | {', '.join(s.attrs.get('codes') or [code_of(s) or '-'])} | "
        f"{s.display_title} | {group or '-'} | "
        f"{s.page_start}-{s.page_end} | {len(kids.get(s.id, []))} | "
        f"{', '.join(s.attrs.get('iasp_codes', [])) or '-'} | {flags} |"
    )
(OUT / "syndromes_all.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- mẫu: tiêu đề được nối lại ở P1
if len(sys.argv) > 1:
    old = [b for b in read_jsonl(Path(sys.argv[1]), Block) if b.kind == "heading"]
    new = {b.line_ids[0]: b for b in blocks if b.kind == "heading"}
    old_first = {b.line_ids[0]: b for b in old}
    merged = [
        (b, [old_first[x].text for x in b.line_ids if x in old_first])
        for b in new.values()
        if sum(x in old_first for x in b.line_ids) > 1
    ]
    out = [
        "# Tiêu đề được nối lại ở P1 (luật `heading_joins` của IASP)\n",
        f"{len(merged)} tiêu đề: trước là nhiều block, nay là 1 block.\n",
        "| Trang PDF | Trước (các block) | Sau (1 block) |",
        "|---|---|---|",
        *(f"| {b.page_start} | {' ‖ '.join(parts)} | {b.text} |" for b, parts in merged),
    ]
    (OUT / "heading_merges.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"tiêu đề được nối lại: {len(merged)}")
