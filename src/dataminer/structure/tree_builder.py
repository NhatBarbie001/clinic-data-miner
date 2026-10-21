"""P2.3 - Dựng cây tài liệu: Sách → Chương → Bệnh → Mục → Mục con.

Duyệt block theo thứ tự đọc với một ngăn xếp: tiêu đề cấp L đóng mọi nút cùng cấp hoặc sâu hơn
rồi mở nút mới; block nội dung gắn vào nút ở đỉnh ngăn xếp. Mỗi block thuộc ĐÚNG MỘT nút.
`Node.id = stable_id(book_id, *path)` - ổn định khi nội dung đổi, dùng làm khóa trích dẫn.
Bất biến (G6) được kiểm sau khi dựng; vi phạm → TreeInvariantError, không im lặng.
Xem docs/phases/P2/P2.3_plan.md.
"""

import re
from collections.abc import Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field

from dataminer.core.schemas import BaseRecord, stable_id
from dataminer.core.text_vi import nfc
from dataminer.ingest.blocks import Block, is_upper_text
from dataminer.structure.heading_levels import HeadingDecision
from dataminer.structure.toc import TocEntry, norm_title

NodeLevel = Literal["book", "chapter", "disease", "section", "subsection", "front"]
RANK: dict[str, int] = {"book": 0, "front": 1, "chapter": 1, "disease": 2, "section": 3,
                        "subsection": 4}  # fmt: skip
RE_SECTION_PREFIX = re.compile(r"^\d{1,2}(\.\d{1,2})?\.?\s+")
RE_CHAPTER_DISPLAY = re.compile(r"^(Chương|Phần|Chuong|Phan)\s+\S+?[.:]\s+")
FRONT_TITLE = "Phần đầu"


class TreeInvariantError(Exception):
    """Cây vi phạm bất biến (block mồ côi/trùng, ID trùng, phạm vi trang sai…)."""


class Node(BaseRecord):
    level: NodeLevel
    parent_id: str | None
    order: int  # thứ tự trong cha
    title: str  # tiêu đề gốc (sau P1), vd. "3. TRIỆU CHỨNG"
    title_norm: str
    display_title: str  # dạng đọc được, vd. "Triệu chứng"
    numbering: str | None = None
    section_type: str | None = None  # P2.4 điền cho section/subsection
    path: list[str]
    heading_block_id: str | None = None
    block_ids: list[str] = Field(default_factory=list)  # nội dung RIÊNG của nút (không gồm con)
    text: str = ""
    page_start: int  # phạm vi trang PDF của CẢ nhánh
    page_end: int
    printed_start: int | None = None
    printed_end: int | None = None
    flags: list[str] = Field(default_factory=list)


class TreeResult(BaseModel):
    nodes: list[Node]  # thứ tự duyệt trước (pre-order) = thứ tự đọc
    warnings: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- tiêu đề


def sentence_case(text: str) -> str:
    """ "VIÊM KHỚP DẠNG THẤP" → "Viêm khớp dạng thấp"; chữ thường/hoa lẫn lộn → giữ nguyên."""
    text = " ".join(nfc(text).split())
    if not is_upper_text(text):
        return text
    lower = text.lower()
    return lower[:1].upper() + lower[1:]


def display_title(text: str, level: str) -> str:
    """Tiêu đề để hiển thị và làm `path`: mục bỏ số thứ tự ("3. TRIỆU CHỨNG" → "Triệu chứng");
    chương giữ "Chương n." ("CHƯƠNG 1. BỆNH…" → "Chương 1. Bệnh…")."""
    if level in ("section", "subsection"):
        text = RE_SECTION_PREFIX.sub("", nfc(text).strip())
    title = sentence_case(text)
    if m := RE_CHAPTER_DISPLAY.match(title):  # "Chương 1. bệnh…" → "Chương 1. Bệnh…"
        rest = title[m.end() :]
        title = title[: m.end()] + rest[:1].upper() + rest[1:]
    return title


def block_text(block: Block) -> str:
    """Văn bản của block khi ghép vào nút: gạch đầu dòng giữ ký hiệu ("- …", "1. …"),
    bảng ở dạng hàng `ô | ô` (đã có sẵn từ P1)."""
    if block.kind == "list_item":
        marker = "-" if block.marker in (None, "-", "•", "–", "+") else block.marker
        return f"{marker} {block.text}"
    return block.text


# --------------------------------------------------------------------------- dựng cây


class _Draft:
    def __init__(self, level: str, parent: "_Draft | None", title: str, heading: Block | None):
        self.level = level
        self.parent = parent
        self.title = title
        self.heading = heading
        self.content: list[Block] = []
        self.children: list[_Draft] = []
        self.flags: list[str] = []
        self.numbering = heading.numbering if heading else None
        self.display = title if heading is None else display_title(title, level)


def build_tree(
    blocks: Sequence[Block],
    decisions: Sequence[HeadingDecision],
    *,
    book_id: str,
    book_title: str | None = None,
    toc: Sequence[TocEntry] = (),
) -> TreeResult:
    """Dựng cây từ block (thứ tự đọc) + cấp tiêu đề (P2.2). Kiểm bất biến trước khi trả."""
    level_of = {d.block_id: d for d in decisions}
    root = _Draft("book", None, book_title or book_id, None)
    stack = [root]
    front: _Draft | None = None
    for b in blocks:
        d = level_of.get(b.id) if b.kind == "heading" else None
        if d is None or d.level == "other":
            top = stack[-1]
            if top is root:  # nội dung trước chương/bệnh đầu tiên → nút "Phần đầu"
                if front is None:
                    front = _Draft("front", root, FRONT_TITLE, None)
                    root.children.append(front)
                top = front
            top.content.append(b)
            if d is not None and "other_heading" not in top.flags:
                top.flags.append("other_heading")
            continue
        rank = RANK[d.level]
        while RANK[stack[-1].level] >= rank:
            stack.pop()
        parent = stack[-1]
        node = _Draft(d.level, parent, b.text, b)
        node.flags.extend(d.flags)
        if d.level == "subsection" and parent.level != "section":
            node.flags.append("orphan_subsection")
        if d.level == "section" and parent.level != "disease":
            node.flags.append("orphan_section")
        parent.children.append(node)
        stack.append(node)

    nodes = _finalize(root, book_id)
    result = TreeResult(nodes=nodes, warnings=_toc_warnings(nodes, decisions, toc, blocks))
    for n in nodes:
        if "orphan_subsection" in n.flags or "orphan_section" in n.flags:
            result.warnings.append(
                f"'{n.title}' (trang PDF {n.page_start}) không có nút cha đúng cấp - "
                f"gắn tạm vào '{n.path[-2] if len(n.path) > 1 else book_id}'."
            )
    violations = check_invariants(nodes, blocks)
    if violations:
        raise TreeInvariantError("Cây vi phạm bất biến:\n  - " + "\n  - ".join(violations))
    return result


def _finalize(root: _Draft, book_id: str) -> list[Node]:
    """Duyệt trước → Node: path, ID ổn định (trùng path → thêm hậu tố + cờ), phạm vi trang."""
    out: list[Node] = []
    used: set[str] = set()

    def visit(draft: _Draft, parent: Node | None, order: int, path: list[str]) -> Node:
        own = ([draft.heading] if draft.heading else []) + draft.content
        node_id = stable_id(book_id, *path, prefix="nd")
        flags = list(draft.flags)
        dup = 1
        while node_id in used:
            dup += 1
            node_id = stable_id(book_id, *path, dup, prefix="nd")
        if dup > 1:
            flags.append("duplicate_path")
        used.add(node_id)
        pages = [p for b in own for p in (b.page_start, b.page_end)]
        printed = [p for b in own for p in (b.printed_start, b.printed_end) if p is not None]
        node = Node(
            id=node_id,
            level=draft.level,  # type: ignore[arg-type]
            parent_id=parent.id if parent else None,
            order=order,
            title=draft.title,
            title_norm=norm_title(draft.title),
            display_title=draft.display,
            numbering=draft.numbering,
            path=path,
            heading_block_id=draft.heading.id if draft.heading else None,
            block_ids=[b.id for b in draft.content],
            text="\n".join(block_text(b) for b in draft.content),
            page_start=min(pages, default=0),
            page_end=max(pages, default=0),
            printed_start=min(printed, default=None),
            printed_end=max(printed, default=None),
            flags=flags,
        )
        out.append(node)
        kids = [visit(c, node, i, [*path, c.display]) for i, c in enumerate(draft.children)]
        # phạm vi trang của nút = của chính nó ∪ mọi con
        spans = [(node.page_start, node.page_end)] if pages else []
        spans += [(k.page_start, k.page_end) for k in kids if k.page_start]
        if spans:
            node.page_start = min(s for s, _ in spans)
            node.page_end = max(e for _, e in spans)
        printed_all = printed + [
            p for k in kids for p in (k.printed_start, k.printed_end) if p is not None
        ]
        node.printed_start = min(printed_all, default=None)
        node.printed_end = max(printed_all, default=None)
        if not draft.content and not kids and draft.level != "book":
            node.flags.append("empty")
        return node

    visit(root, None, 0, [])
    return out


def _toc_warnings(
    nodes: Sequence[Node],
    decisions: Sequence[HeadingDecision],
    toc: Sequence[TocEntry],
    blocks: Sequence[Block],
) -> list[str]:
    """Đối chiếu mục lục sau khi dựng: mỗi chương/bệnh của mục lục (trong phạm vi trang đã xử
    lý) phải có đúng 1 nút; trang bắt đầu của nút = trang PDF trong mục lục."""
    if not toc or not blocks:
        return []
    lo = min(b.page_start for b in blocks)
    hi = max(b.page_end for b in blocks)
    match_of = {d.block_id: d.toc_match for d in decisions}
    warnings: list[str] = []
    for e in toc:
        if e.pdf_page is None or not lo <= e.pdf_page <= hi:
            continue
        hits = [
            n
            for n in nodes
            if n.level == e.level
            and n.heading_block_id
            and match_of.get(n.heading_block_id) == e.title_norm
        ]
        if len(hits) != 1:
            warnings.append(f"Mục lục '{e.title}': {len(hits)} nút khớp trong cây (cần đúng 1).")
        elif hits[0].page_start != e.pdf_page:
            warnings.append(
                f"Mục lục '{e.title}': nút bắt đầu ở trang PDF {hits[0].page_start}, "
                f"mục lục ghi {e.pdf_page}."
            )
    return warnings


# --------------------------------------------------------------------------- bất biến


def check_invariants(nodes: Sequence[Node], blocks: Sequence[Block]) -> list[str]:
    """G6. Trả danh sách vi phạm (rỗng = đạt):
    1. mỗi block thuộc đúng 1 nút; 2. ID duy nhất, cha tồn tại; 3. phạm vi trang cha ⊇ con;
    4. thứ tự duyệt trước của các block = thứ tự đọc; 5. nút rỗng (không nội dung, không con)
    phải có cờ `empty`."""
    problems: list[str] = []
    owner: dict[str, list[str]] = {}
    for n in nodes:
        for bid in ([n.heading_block_id] if n.heading_block_id else []) + n.block_ids:
            owner.setdefault(bid, []).append(n.id)
    for b in blocks:
        holders = owner.get(b.id, [])
        if len(holders) != 1:
            problems.append(f"block {b.id} thuộc {len(holders)} nút (cần đúng 1)")
    known = {b.id for b in blocks}
    problems.extend(f"nút trỏ tới block không tồn tại {bid}" for bid in owner if bid not in known)

    by_id: dict[str, Node] = {}
    for n in nodes:
        if n.id in by_id:
            problems.append(f"ID nút trùng: {n.id} ('{n.title}')")
        by_id[n.id] = n
    children: dict[str, list[Node]] = {}
    for n in nodes:
        if n.parent_id is None:
            continue
        parent = by_id.get(n.parent_id)
        if parent is None:
            problems.append(f"nút '{n.title}' có cha không tồn tại {n.parent_id}")
            continue
        children.setdefault(parent.id, []).append(n)
        if not parent.page_start <= n.page_start <= n.page_end <= parent.page_end:
            problems.append(
                f"phạm vi trang của '{n.title}' ({n.page_start}-{n.page_end}) nằm ngoài cha "
                f"'{parent.title}' ({parent.page_start}-{parent.page_end})"
            )

    order: list[str] = []
    visited: set[int] = set()  # theo object: ID trùng/cha sai có thể tạo chu trình

    def walk(n: Node) -> None:
        if id(n) in visited:
            problems.append(f"chu trình trong cây tại '{n.title}'")
            return
        visited.add(id(n))
        order.extend(([n.heading_block_id] if n.heading_block_id else []) + n.block_ids)
        for c in sorted(children.get(n.id, []), key=lambda x: x.order):
            walk(c)

    roots = [n for n in nodes if n.parent_id is None]
    if len(roots) != 1:
        problems.append(f"cây phải có đúng 1 gốc, có {len(roots)}")
    for root in roots:
        walk(root)
    unreachable = [n.title for n in nodes if id(n) not in visited]
    if unreachable:
        problems.append(f"{len(unreachable)} nút không đi tới được từ gốc: {unreachable[:3]}")
    if order != [b.id for b in blocks]:
        problems.append("thứ tự block trong cây khác thứ tự đọc")
    for n in nodes:
        is_empty = not n.block_ids and not children.get(n.id) and n.level != "book"
        if is_empty and "empty" not in n.flags:
            problems.append(f"nút rỗng '{n.title}' không có cờ 'empty'")
    return problems


# --------------------------------------------------------------------------- hiển thị


def to_nested(nodes: Sequence[Node]) -> dict[str, Any]:
    """Cây lồng nhau (tree.json): mỗi nút gồm các trường chính + `children`."""
    kids: dict[str | None, list[Node]] = {}
    for n in nodes:
        kids.setdefault(n.parent_id, []).append(n)

    def build(n: Node) -> dict[str, Any]:
        data = n.model_dump(mode="json", exclude={"text", "block_ids", "schema_version"})
        data["n_blocks"] = len(n.block_ids)
        data["children"] = [build(c) for c in sorted(kids.get(n.id, []), key=lambda x: x.order)]
        return data

    roots = kids.get(None, [])
    if len(roots) != 1:  # pragma: no cover - build_tree luôn có đúng 1 gốc
        raise TreeInvariantError(f"cây phải có đúng 1 gốc, có {len(roots)}")
    return build(roots[0])


def _content_summary(n: Node, blocks: dict[str, Block]) -> str:
    names = {"paragraph": "đoạn văn", "list_item": "gạch đầu dòng", "table": "bảng",
             "caption": "chú thích", "heading": "tiêu đề khác", "toc_entry": "dòng mục lục",
             "other": "khác"}  # fmt: skip
    counts: dict[str, int] = {}
    for bid in n.block_ids:
        kind = blocks[bid].kind
        counts[kind] = counts.get(kind, 0) + 1
    return ", ".join(f"{v} {names.get(k, k)}" for k, v in counts.items())


def render_tree_md(nodes: Sequence[Node], blocks: Sequence[Block]) -> str:
    """Cây chữ để người đọc kiểm tra nhanh: cấp, loại mục, nội dung riêng, trang in, cờ."""
    by_block = {b.id: b for b in blocks}
    kids: dict[str | None, list[Node]] = {}
    for n in nodes:
        kids.setdefault(n.parent_id, []).append(n)
    lines: list[str] = []

    def pages(n: Node) -> str:
        if n.printed_start is None:
            return f"PDF {n.page_start}–{n.page_end}" if n.page_start else ""
        if n.printed_start == n.printed_end:
            return f"tr.in {n.printed_start}"
        return f"tr.in {n.printed_start}–{n.printed_end}"

    def label(n: Node) -> str:
        prefix = f"{n.numbering}. " if n.level in ("section", "subsection") and n.numbering else ""
        parts = [f"{prefix}{n.display_title}"]
        if n.section_type:
            parts.append(f"[{n.section_type}]")
        summary = _content_summary(n, by_block)
        if summary:
            parts.append(f"· {summary}")
        elif kids.get(n.id) and n.level in ("section", "subsection"):
            parts.append("· (chỉ có mục con)")
        parts.append(f"· {pages(n)}")
        if n.flags:
            parts.append(f"⚑ {', '.join(n.flags)}")
        return " ".join(parts)

    def walk(n: Node, prefix: str, last: bool, top: bool) -> None:
        if top:
            lines.append(label(n))
        else:
            lines.append(f"{prefix}{'└─ ' if last else '├─ '}{label(n)}")
        children = sorted(kids.get(n.id, []), key=lambda x: x.order)
        inner = "" if top else prefix + ("   " if last else "│  ")
        for i, c in enumerate(children):
            walk(c, inner, i == len(children) - 1, False)

    for root in kids.get(None, []):
        walk(root, "", True, True)
    return "\n".join(lines) + "\n"
