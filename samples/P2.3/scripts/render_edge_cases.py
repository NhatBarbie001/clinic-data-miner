"""Sinh samples/P2.3/edge_cases.md: các tình huống sách mẫu không có, dựng thật bằng build_tree.
Chạy: uv run python samples/P2.3/scripts/render_edge_cases.py"""

from pathlib import Path

from dataminer.books.book01.lines import numbering_of
from dataminer.books.book01.rules import build_tree
from dataminer.model.block import Block
from dataminer.model.tree import HeadingDecision
from dataminer.structure.tree_builder import render_tree_md
from dataminer.text.blocks import is_upper_text

n = 0


def make(spec: list[tuple[str, str]]) -> tuple[list[Block], list[HeadingDecision]]:
    global n
    blocks: list[Block] = []
    decisions: list[HeadingDecision] = []
    for kind, text in spec:
        n += 1
        heading = kind not in ("p", "li")
        b = Block(
            id=f"b{n}",
            kind="heading" if heading else ("list_item" if kind == "li" else "paragraph"),
            text=text,
            text_rules=text,
            page_start=4,
            page_end=4,
            printed_start=1,
            printed_end=1,
            line_ids=[f"l{n}"],
            bbox=(48, 0, 300, 13),
            x0=48,
            font_size=12 if heading else 10.5,
            is_upper=heading and is_upper_text(text),
            numbering=numbering_of(text) if heading else None,
            marker="-" if kind == "li" else None,
        )
        blocks.append(b)
        if heading:
            decisions.append(
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
    return blocks, decisions


CASES = {
    "Có lời nói đầu trước chương đầu tiên → nút `front` (Phần đầu)": [
        ("p", "Sách này dành cho sinh viên y khoa."),
        ("chapter", "CHƯƠNG 1. HÔ HẤP"),
        ("p", "Giới thiệu chương."),
        ("disease", "HEN PHẾ QUẢN"),
        ("section", "1. ĐẠI CƯƠNG"),
        ("p", "…"),
    ],
    "Sách không chia chương → bệnh là con trực tiếp của sách": [
        ("disease", "HEN PHẾ QUẢN"),
        ("section", "1. ĐẠI CƯƠNG"),
        ("p", "…"),
        ("disease", "VIÊM PHỔI"),
        ("section", "1. ĐẠI CƯƠNG"),
        ("p", "…"),
    ],
    "Mục con thiếu mục cha (`2.1.` ngay dưới bệnh) → cờ `orphan_subsection`": [
        ("disease", "SỎI THẬN"),
        ("subsection", "2.1. Thể lâm sàng"),
        ("p", "…"),
    ],
    "Tiêu đề `other` (LƯU Ý) → nội dung của mục đang mở; mục rỗng → `empty`; tên mục lặp → "
    "`duplicate_path`": [
        ("disease", "GOUT"),
        ("section", "1. ĐIỀU TRỊ"),
        ("p", "Allopurinol…"),
        ("other", "LƯU Ý"),
        ("p", "Không tự ý dùng thuốc."),
        ("section", "2. PHÒNG BỆNH"),
        ("section", "3. ĐIỀU TRỊ"),
        ("li", "…"),
    ],
}
out = ["# Tình huống ngoài sách mẫu (block tự dựng, dựng thật bằng `build_tree`)\n"]
for title, spec in CASES.items():
    blocks, decisions = make(spec)
    result = build_tree(blocks, decisions, book_id="demo", book_title="Sách thử")
    out.append(f"## {title}\n")
    out.append("Đầu vào (theo thứ tự đọc): " + " → ".join(f"`{t}`" for _, t in spec) + "\n")
    out.append("```\n" + render_tree_md(result.nodes, blocks).rstrip() + "\n```\n")
    if result.warnings:
        out.extend(f"- ⚠ {w}" for w in result.warnings)
        out.append("")
Path("samples/P2.3/edge_cases.md").write_text("\n".join(out), encoding="utf-8")
print("ok")
