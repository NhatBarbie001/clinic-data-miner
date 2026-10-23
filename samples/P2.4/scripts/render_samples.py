"""Sinh samples/P2.4/: sections.md (pilot), section_eval.txt, edge_cases.md và
section_proposals_demo.csv (vòng duyệt với LLM GIẢ LẬP - không gọi mạng, không tốn tiền).
Chạy sau `dm p2 sections map`: uv run python samples/P2.4/scripts/render_samples.py"""

import json
import shutil
import tempfile
from pathlib import Path

import httpx

from dataminer.core.config import load_settings
from dataminer.core.io import read_jsonl
from dataminer.core.llm_client import LLMClient
from dataminer.core.prompts import load_prompt
from dataminer.evaluation.p1_eval import format_eval
from dataminer.evaluation.p2_eval import eval_sections
from dataminer.model.block import Block
from dataminer.model.tree import HeadingDecision, Node
from dataminer.structure.section_mapper import (
    export_proposals,
    load_section_map,
    lookup,
    map_sections,
    normalize_section_title,
)
from dataminer.structure.tree_builder import build_tree, render_tree_md
from dataminer.text.blocks import is_upper_text, numbering_of

OUT = Path("samples/P2.4")
MAP = Path("configs/section_map.yaml")
mapping = load_section_map(MAP)

# ------------------------------------------------ pilot
nodes = list(read_jsonl(Path("data/p2_tree/nodes.jsonl"), Node))
truth = json.loads(Path("data/raw/book01.truth.json").read_text(encoding="utf-8"))
blocks = list(read_jsonl(Path("data/p1_clean/blocks.jsonl"), Block))
pages = (min(b.page_start for b in blocks), max(b.page_end for b in blocks))
(OUT / "section_eval.txt").write_text(
    "Đánh giá G5 (sách mẫu seed 7, pilot trang PDF 4-9) - dm p2 sections map --eval\n\n"
    + format_eval(eval_sections(nodes, truth, pages))
    + "\n",
    encoding="utf-8",
)
by_id = {n.id: n for n in nodes}
rows = [
    "# Loại mục - pilot sách mẫu (seed 7)\n",
    f"Từ điển: `{MAP}` ({len(mapping)} khóa). Mỗi tên mục → chuẩn hóa → tra từ điển.\n",
    "| Bệnh | Tên mục (sau P1) | Chuẩn hóa | → Loại | Nguồn |",
    "|---|---|---|---|---|",
]
for n in nodes:
    if n.level not in ("section", "subsection"):
        continue
    cur = n
    while cur.level != "disease":
        cur = by_id[cur.parent_id or ""]
    rows.append(
        f"| {cur.display_title} | `{n.title}` | `{normalize_section_title(n.title)}` | "
        f"**{n.section_type}** | {n.section_source} |"
    )
types = ["definition", "cause", "risk_factor", "symptom", "paraclinical", "complication",
         "diagnosis", "treatment", "prevention"]  # fmt: skip
rows += ["\n## Ma trận bệnh × loại mục\n", "| Bệnh | " + " | ".join(types) + " |",
         "|---|" + "---|" * len(types)]  # fmt: skip
for d in (n for n in nodes if n.level == "disease"):
    have = set()
    stack = [d.id]
    while stack:
        pid = stack.pop()
        for c in nodes:
            if c.parent_id == pid:
                stack.append(c.id)
                if c.section_type:
                    have.add(c.section_type)
    rows.append(
        f"| {d.display_title} | " + " | ".join("✓" if t in have else "—" for t in types) + " |"
    )
(OUT / "sections.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

# ------------------------------- ngoài sách mẫu + vòng duyệt (LLM giả lập)
n_id = 0


def make(spec: list[tuple[str, str]]) -> tuple[list[Block], list[HeadingDecision]]:
    global n_id
    bs: list[Block] = []
    ds: list[HeadingDecision] = []
    for kind, text in spec:
        n_id += 1
        heading = kind != "p"
        b = Block(
            id=f"b{n_id}",
            kind="heading" if heading else "paragraph",
            text=text,
            text_rules=text,
            page_start=4,
            page_end=4,
            line_ids=[f"l{n_id}"],
            bbox=(48, 0, 300, 13),
            x0=48,
            font_size=12 if heading else 10.5,
            is_upper=heading and is_upper_text(text),
            numbering=numbering_of(text) if heading else None,
        )
        bs.append(b)
        if heading:
            ds.append(
                HeadingDecision(
                    block_id=b.id,
                    text=text,
                    page=4,
                    level=kind,  # type: ignore[arg-type]
                    confidence="high",
                    reasons=[],
                    numbering=b.numbering,
                )
            )
    return bs, ds


spec = [
    ("disease", "ĐÁI THÁO ĐƯỜNG"),
    ("section", "2. NGUYÊN NHÂU"),
    ("p", "Thiếu insulin tương đối hoặc tuyệt đối."),
    ("section", "3. TRIỆU CHỨNG"),
    ("subsection", "3.3. Đặc điểm"),
    ("p", "Ăn nhiều, uống nhiều, tiểu nhiều, gầy nhiều."),
    ("section", "5. ĐIỀU KHIỂN"),
    ("p", "Theo dõi đường huyết."),
    ("section", "7. THEO DÕI SAU ĐIỀU TRỊ"),
    ("p", "Tái khám mỗi 3 tháng, theo dõi biến chứng."),
]
demo_blocks, demo_decisions = make(spec)
demo = build_tree(demo_blocks, demo_decisions, book_id="demo").nodes
answer = {"section_type": "prevention", "reason": "nội dung là tái khám, theo dõi biến chứng"}


def fake(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={
        "id": "gen-demo", "model": "deepseek/deepseek-v4.1-flash-1017", "provider": "giả lập",
        "choices": [{"index": 0, "finish_reason": "stop", "message": {
            "role": "assistant", "content": json.dumps(answer, ensure_ascii=False)}}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0},
    })  # fmt: skip


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:  # Windows: SQLite còn mở
    root = Path(tmp)
    shutil.copytree("configs", root / "configs")
    (root / "pyproject.toml").write_text("", encoding="utf-8")
    settings = load_settings(root, env={"OPENROUTER_API_KEY": "sk-gia-lap"})
    client = LLMClient(settings, transport=httpx.MockTransport(fake))
    prompt = load_prompt(Path("prompts"), "p2_classify_section")
    result = map_sections(demo, mapping, client=client, prompt=prompt)
export_proposals(result.proposals, OUT / "section_proposals_demo.csv")

lines = [
    "# Tình huống ngoài sách mẫu (cây tự dựng, chạy thật `map_sections`, LLM GIẢ LẬP)\n",
    "Trên sách mẫu cả 22 tên mục đều trúng từ điển; các đường dưới đây chỉ thấy được ở đây.\n",
    "| Tên mục | Chuẩn hóa | Tra từ điển | → Loại | Nguồn | Cờ |",
    "|---|---|---|---|---|---|",
]
for n in demo:
    if n.level not in ("section", "subsection"):
        continue
    key = normalize_section_title(n.title)
    hit = lookup(key, mapping, 0.9)
    how = "không khớp" if hit is None else (
        "trùng khóa" if hit[2] == 1.0 else f"gần '{hit[1]}' ({hit[2]:.3f})")  # fmt: skip
    lines.append(
        f"| `{n.title}` | `{key}` | {how} | **{n.section_type}** | {n.section_source} | "
        f"{', '.join(n.flags)} |"
    )
lines += [
    "\nGhi chú:",
    "- `5. ĐIỀU KHIỂN` (`dieu khien`) chỉ giống `dieu tri` 0.667 → KHÔNG khớp gần (ngưỡng 0.9 đủ "
    "chặt), nên được hỏi LLM; LLM giả lập ở đây trả cùng một nhãn cho mọi câu hỏi - chỉ minh họa "
    "đường đi, không phải nhãn thật.",
    "- Đề xuất cần duyệt (khớp gần + LLM) → "
    "[section_proposals_demo.csv](section_proposals_demo.csv)"
    " → người duyệt điền `decision` → `dm p2 sections import` ghi thêm vào từ điển.",
    f"\nLời gọi LLM (giả lập): {result.llm_calls}; đề xuất: {len(result.proposals)}.\n",
    "```\n" + render_tree_md(demo, demo_blocks).rstrip() + "\n```\n",
]
(OUT / "edge_cases.md").write_text("\n".join(lines), encoding="utf-8")
print("ok")
