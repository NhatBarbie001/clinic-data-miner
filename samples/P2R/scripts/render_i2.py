"""Sinh samples/P2R/I2/: page137_before_after.md, dehyphenation.md.

Chạy sau `dm --book iasp p1 run --scope all`: uv run python samples/P2R/scripts/render_i2.py
"Trước" = lần chạy NGUYÊN TRẠNG (luật sách mẫu) ngày 2026-10-22: baseline_page137_asis.jsonl.
"""

import itertools
import json
import re
from collections import Counter
from pathlib import Path

from dataminer.core.io import read_jsonl
from dataminer.model.block import Block
from dataminer.model.line import Line
from dataminer.text import blocks as text_blocks

OUT = Path("samples/P2R/I2")
P1 = Path("data/books/iasp/p1_clean")
BASELINE = OUT / "baseline_page137_asis.jsonl"
before = [json.loads(x) for x in BASELINE.read_text(encoding="utf-8").splitlines() if x]
after = list(read_jsonl(P1 / "blocks.jsonl", Block))


def cell(text: str, n: int = 110) -> str:
    text = text.replace("\n", " ⏎ ").replace("|", "¦")
    return text if len(text) <= n else text[: n - 1] + "…"


def joins(b: Block) -> str:
    return ", ".join(f for f in b.flags if f.startswith("joined"))


rows = [
    "# Trang PDF 137 (tr.in 121): trước ↔ sau luật IASP\n",
    "**Trước** = chạy nguyên trạng bằng luật sách mẫu (đọc theo hàng ngang, tiêu đề = IN HOA).",
    "**Sau** = luật IASP (đọc theo cột, tiêu đề = chữ đậm, bỏ gạch nối cuối dòng).\n",
    "## Trước (nguyên trạng)\n",
    "| # | Loại | Nội dung |",
    "|---|---|---|",
]
rows += [f"| {i} | {b['kind']} | {cell(b['text'])} |" for i, b in enumerate(before, 1)]
rows += ["\n## Sau (luật IASP)\n", "| # | Loại | Nội dung | Cờ |", "|---|---|---|---|"]
page = [b for b in after if b.page_start == 137]
rows += [f"| {i} | {b.kind} | {cell(b.text)} | {joins(b)} |" for i, b in enumerate(page, 1)]
(OUT / "page137_before_after.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- bỏ gạch nối
lines = {ln.id: ln for ln in read_jsonl(P1 / "lines.jsonl", Line)}
joined: Counter[str] = Counter()
kept: Counter[str] = Counter()
for b in after:
    seq = [lines[i].text for i in b.line_ids]
    for a, nxt in itertools.pairwise(seq):
        left = text_blocks.RE_HYPHEN_FRAGMENT.search(a)
        right = re.match(r"([a-z]+)", nxt)
        if not (left and right):
            continue
        merged = left.group(1) + right.group(1)
        if merged in b.text:
            joined[f"{left.group(1)}- + {right.group(1)} → {merged}"] += 1
        else:
            kept[f"{left.group(1)}- + {right.group(1)} → {left.group(1)}-{right.group(1)}"] += 1
out = [
    "# Bỏ gạch nối cuối dòng (Part II, PDF 53-222)\n",
    f"- **Đã bỏ gạch**: {sum(joined.values())} chỗ ({len(joined)} kiểu)",
    f"- **Giữ gạch** (sách viết có gạch ở chỗ khác, hoặc tiền tố): {sum(kept.values())} chỗ\n",
    "Luật: (1) dạng có gạch gặp GIỮA dòng ở chỗ khác trong sách → giữ; (2) dạng liền gặp như một"
    " từ trong sách → bỏ; (3) không có bằng chứng → giữ nếu là tiền tố (anti-, non-, self-…).\n",
    "Soát nhanh: kết quả bên phải phải là MỘT từ bình thường; thấy từ ghép bị dính"
    " (vd. `antiinflammatory`) thì báo.\n",
    "## Giữ gạch\n",
    *[f"- `{k}` ×{v}" for k, v in kept.most_common()],
    "\n## Đã bỏ gạch (tất cả)\n",
    *[f"- `{k}` ×{v}" for k, v in sorted(joined.items())],
]
(OUT / "dehyphenation.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("đã bỏ", sum(joined.values()), "· giữ", sum(kept.values()))
