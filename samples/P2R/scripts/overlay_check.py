"""Kiểm S2 (I5): vùng tô của trang soát có trùng đúng chữ trên trang PDF không.

Vẽ khung bằng ĐÚNG tọa độ % mà index.html dùng (`build_view` → Box) lên trang PDF (chỉ trong bộ
nhớ, không sửa file sách) → ảnh PNG để người (và tôi) nhìn tận mắt. Mỗi mục một màu, tên = đỏ.

    uv run python samples/P2R/scripts/overlay_check.py <out_dir> [số hội chứng = 3]
Chạy sau `dm --book iasp p2 spotcheck` (lấy mẫu từ spotcheck/meta.json).
"""

import json
import sys
from pathlib import Path

import pymupdf

from dataminer.core.io import read_jsonl
from dataminer.evaluation.spotcheck import Tree, build_view
from dataminer.model.block import Block
from dataminer.model.line import Line
from dataminer.model.tree import Node

PDF = Path("data/books/iasp/raw/classification_of_chronic_pain.pdf")
P1 = Path("data/books/iasp/p1_clean")
P2 = Path("data/books/iasp/p2_tree")
OUT = Path(sys.argv[1])
HOW_MANY = int(sys.argv[2]) if len(sys.argv) > 2 else 3
COLORS = [(0.1, 0.4, 0.9), (0.0, 0.6, 0.3), (0.8, 0.5, 0.0), (0.6, 0.2, 0.7), (0.0, 0.6, 0.7)]

meta = json.loads((P2 / "spotcheck" / "meta.json").read_text(encoding="utf-8"))
nodes = list(read_jsonl(P2 / "nodes.jsonl", Node))
blocks = {b.id: b for b in read_jsonl(P1 / "blocks.jsonl", Block)}
lines = {ln.id: ln for ln in read_jsonl(P1 / "lines.jsonl", Line)}
tree = Tree(nodes)
OUT.mkdir(parents=True, exist_ok=True)

with pymupdf.open(PDF) as doc:
    for uid in meta["sample"][:HOW_MANY]:
        view = build_view(tree.by_id[uid], tree, blocks, lines)
        color = {p.node_id: COLORS[i % len(COLORS)] for i, p in enumerate(view.parts)}
        color[view.unit_id] = (0.9, 0.0, 0.0)
        for page_no in view.pages:
            page = doc[page_no - 1]
            w, h = page.rect.width, page.rect.height
            for b in (b for b in view.boxes if b.page == page_no):
                rect = pymupdf.Rect(
                    b.left * w / 100,
                    b.top * h / 100,
                    (b.left + b.width) * w / 100,
                    (b.top + b.height) * h / 100,
                )
                page.draw_rect(rect, color=color[b.node_id], width=0.8)
            name = f"overlay_check_{view.code.replace(', ', '_') or uid}_p{page_no}.png"
            page.get_pixmap(dpi=90).save(OUT / name)
            print(f"{view.code} {view.title}: PDF {page_no} → {OUT / name}")
