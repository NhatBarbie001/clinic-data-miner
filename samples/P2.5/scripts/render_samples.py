"""Sinh samples/P2.5/golden_overview.md + golden_validation.txt từ eval/golden_qa_v1.jsonl.
Chạy: uv run python samples/P2.5/scripts/render_samples.py"""

from pathlib import Path

from dataminer.core.io import read_jsonl
from dataminer.evaluation.p1_eval import format_eval
from dataminer.evaluation.p2_eval import eval_golden
from dataminer.model.tree import Node
from dataminer.structure.golden import GoldenItem

OUT = Path("samples/P2.5")
items = list(read_jsonl(Path("eval/book01/golden_qa_v1.jsonl"), GoldenItem))
nodes = list(read_jsonl(Path("data/books/book01/p2_tree/nodes.jsonl"), Node))
(OUT / "golden_validation.txt").write_text(
    "Kiểm G7: eval/golden_qa_v1.jsonl ↔ cây hiện tại (data/p2_tree/nodes.jsonl) - "
    "dm p2 golden --check\n\n" + format_eval(eval_golden(items, nodes)) + "\n",
    encoding="utf-8",
)
names = {"specific": "cụ thể", "list": "liệt kê", "refusal": "từ chối"}
rows = [
    "# Bộ câu hỏi chuẩn v1 - tổng quan (30 câu)\n",
    "File đầy đủ: [eval/golden_qa_v1.jsonl](../../eval/golden_qa_v1.jsonl) · quy tắc: "
    "[eval/README.md](../../eval/README.md) (**không bao giờ dùng để huấn luyện**).\n",
    "| # | Loại | Câu hỏi | Nguồn (path) | Ý bắt buộc | Ghi chú |",
    "|---|---|---|---|---|---|",
]
for i, it in enumerate(items, 1):
    src = "<br>".join(" › ".join(s.path[1:]) for s in it.sources) or "—"
    pts = "<br>".join(f"• {p}" for p in it.answer_points) or it.answer
    rows.append(f"| {i} | {names[it.qtype]} | {it.question} | {src} | {pts} | {it.notes or ''} |")
(OUT / "golden_overview.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
print("ok")
