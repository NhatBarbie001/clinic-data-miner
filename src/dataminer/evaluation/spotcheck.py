"""P2R I5 - soát tay (A9): chọn mẫu bệnh, gom dữ liệu để xem, bảng bệnh, chấm phiếu.

Dùng chung mọi sách: "bệnh" = `BookRules.review_units` (IASP: hội chứng). Chỉ ĐỌC cây / block /
dòng - không đổi dữ liệu P1/P2. Trang HTML: `evaluation/spotcheck_page.py`.
Xem docs/phases/P2R/I5_plan.md.
"""

import csv
import io
import random
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, Field

from dataminer.evaluation.checks import CheckResult
from dataminer.model.block import Block
from dataminer.model.line import Line
from dataminer.model.tree import Node
from dataminer.structure.tree_builder import block_text

CRITERIA = ("ok_title", "ok_boundary", "ok_sections", "ok_columns")
CRITERIA_LABELS = {
    "ok_title": "Đúng tên",
    "ok_boundary": "Đúng ranh giới",
    "ok_sections": "Đủ mục, đúng nội dung",
    "ok_columns": "Không lẫn cột",
}
REVIEW_COLUMNS = ("unit_id", "code", "title", "pdf_pages", *CRITERIA, "note")
# cờ KHÔNG nói gì về chất lượng tách → vẫn được chọn vào mẫu ngẫu nhiên
BENIGN_FLAGS = frozenset({"no_iasp_code", "chapter_is_syndrome"})


class SpotcheckError(Exception):
    """Phiếu chấm / dữ liệu soát không dùng được (thông báo cho người dùng)."""


# --------------------------------------------------------------------------- cây


class Tree:
    """Tra cứu nhanh trên danh sách nút (thứ tự duyệt trước)."""

    def __init__(self, nodes: Sequence[Node]) -> None:
        self.nodes = list(nodes)
        self.by_id = {n.id: n for n in nodes}
        self.kids: dict[str, list[Node]] = {}
        for n in nodes:
            if n.parent_id:
                self.kids.setdefault(n.parent_id, []).append(n)

    def descendants(self, node: Node) -> list[Node]:
        out: list[Node] = []
        for child in sorted(self.kids.get(node.id, []), key=lambda c: c.order):
            out += [child, *self.descendants(child)]
        return out

    def ancestor(self, node: Node, level: str) -> Node | None:
        cur = self.by_id.get(node.parent_id or "")
        while cur is not None and cur.level != level:
            cur = self.by_id.get(cur.parent_id or "")
        return cur

    def stratum(self, node: Node) -> str:
        """Nhóm để rải mẫu: phần (part) gần nhất, không có thì chương, không có nữa thì '-'."""
        for level in ("part", "chapter"):
            if (hit := self.ancestor(node, level)) is not None:
                return hit.numbering or hit.display_title
        return "-"


def code_of(unit: Node) -> str:
    """Mã hiển thị của bệnh: các mã trong attrs["codes"] (mục gộp / GROUP-hội chứng) hoặc
    `numbering`; không có → ''."""
    return ", ".join(unit.attrs.get("codes") or ([unit.numbering] if unit.numbering else []))


# --------------------------------------------------------------------------- chọn mẫu


def eligible(unit: Node) -> bool:
    """Được vào mẫu NGẪU NHIÊN của A9: không mang cờ báo lỗi (bệnh có cờ xem riêng)."""
    return not (set(unit.flags) - BENIGN_FLAGS)


def allocate(sizes: dict[str, int], n: int) -> dict[str, int]:
    """Chia `n` lượt cho các nhóm theo tỉ lệ (phần dư lớn nhất); n ≥ số nhóm thì nhóm nào cũng
    có ≥ 1 lượt; không nhóm nào nhận quá số bệnh nó có."""
    total = sum(sizes.values())
    n = min(n, total)
    if not total:
        return {k: 0 for k in sizes}
    quota = {k: n * v / total for k, v in sizes.items()}
    alloc = {k: int(q) for k, q in quota.items()}
    for k in sorted(sizes, key=lambda k: (-(quota[k] - alloc[k]), list(sizes).index(k))):
        if sum(alloc.values()) >= n:
            break
        alloc[k] += 1
    if n >= len(sizes):
        for k in sizes:
            if alloc[k] == 0 and sizes[k]:
                donor = max(alloc, key=lambda d: (alloc[d], -list(sizes).index(d)))
                alloc[donor] -= 1
                alloc[k] = 1
    return alloc


def choose_sample(units: Sequence[Node], tree: Tree, n: int, seed: int) -> list[Node]:
    """`n` bệnh ngẫu nhiên (hạt giống `seed`), rải theo nhóm, chỉ trong bệnh `eligible`;
    trả theo thứ tự đọc."""
    groups: dict[str, list[Node]] = {}
    for u in units:
        if eligible(u):
            groups.setdefault(tree.stratum(u), []).append(u)
    alloc = allocate({k: len(v) for k, v in groups.items()}, n)
    rng = random.Random(seed)
    picked = {u.id for k, v in groups.items() for u in rng.sample(v, alloc[k])}
    return [u for u in units if u.id in picked]


# --------------------------------------------------------------------------- dữ liệu 1 bệnh


class Box(BaseModel):
    """Một dòng chữ trên trang, tính bằng % khổ trang (ảnh ở dpi nào cũng khớp)."""

    page: int
    left: float
    top: float
    width: float
    height: float
    node_id: str


class Part(BaseModel):
    """Một nút trong bệnh (chính bệnh, mục, mục con) + văn bản riêng của nó."""

    node_id: str
    title: str
    level: str
    section_type: str | None = None
    depth: int = 0  # 0 = bệnh, 1 = mục, 2 = mục con
    texts: list[str] = Field(default_factory=list)  # block nội dung riêng, theo thứ tự đọc


class UnitView(BaseModel):
    unit_id: str
    title: str
    code: str
    group: str  # chương
    stratum: str
    pages: list[int]
    attrs: dict[str, list[str]]
    flags: list[str]
    parts: list[Part]
    boxes: list[Box]
    n_blocks: int


def build_view(
    unit: Node, tree: Tree, blocks: dict[str, Block], lines: dict[str, Line]
) -> UnitView:
    """Gom mọi thứ cần để soát 1 bệnh: các nút (bệnh + mục), văn bản, ô chữ trên trang."""
    members = [unit, *tree.descendants(unit)]
    depth = {unit.id: 0}
    parts: list[Part] = []
    boxes: list[Box] = []
    n_blocks = 0
    for node in members:
        if node.id != unit.id:
            depth[node.id] = depth.get(node.parent_id or "", 0) + 1
        own = ([node.heading_block_id] if node.heading_block_id else []) + node.block_ids
        n_blocks += len(own)
        parts.append(
            Part(
                node_id=node.id,
                title=node.display_title if node.id == unit.id else node.title,
                level=node.level,
                section_type=node.section_type,
                depth=depth[node.id],
                texts=[block_text(blocks[b]) for b in node.block_ids],  # giữ "1." / "-" đầu dòng
            )
        )
        for bid in own:
            for lid in blocks[bid].line_ids:
                ln = lines[lid]
                w, h = ln.page_width or 1.0, ln.page_height or 1.0
                x0, y0, x1, y1 = ln.bbox
                boxes.append(
                    Box(
                        page=ln.page,
                        left=round(100 * x0 / w, 3),
                        top=round(100 * y0 / h, 3),
                        width=round(100 * (x1 - x0) / w, 3),
                        height=round(100 * (y1 - y0) / h, 3),
                        node_id=node.id,
                    )
                )
    chapter = unit if unit.level == "chapter" else tree.ancestor(unit, "chapter")
    return UnitView(
        unit_id=unit.id,
        title=unit.display_title,
        code=code_of(unit),
        group=chapter.display_title if chapter else "-",
        stratum=tree.stratum(unit),
        pages=sorted({b.page for b in boxes}),
        attrs=unit.attrs,
        flags=unit.flags,
        parts=parts,
        boxes=boxes,
        n_blocks=n_blocks,
    )


# --------------------------------------------------------------------------- bảng bệnh


def units_table(
    units: Sequence[Node], tree: Tree, section_types: Sequence[str]
) -> tuple[list[str], list[dict[str, str]]]:
    """Mỗi bệnh một dòng (mở bằng Excel): mã, tên, nhóm, trang, số mục, số từ, cột `has_<loại>`
    (✓ nếu bệnh có mục loại đó), thuộc tính (attrs), cờ. Trả (cột, dòng)."""
    attr_keys = sorted({k for u in units for k in u.attrs if k != "codes"})
    columns = ["code", "title", "group", "part", "pdf_start", "pdf_end", "printed_start",
               "printed_end", "n_sections", "words", *(f"has_{t}" for t in section_types),
               *attr_keys, "flags", "unit_id"]  # fmt: skip
    rows: list[dict[str, str]] = []
    for u in units:
        inner = tree.descendants(u)
        sections = [n for n in inner if n.level in ("section", "subsection")]
        have = {n.section_type for n in sections}
        chapter = u if u.level == "chapter" else tree.ancestor(u, "chapter")
        part = tree.ancestor(u, "part")
        row = {
            "code": code_of(u),
            "title": u.display_title,
            "group": chapter.display_title if chapter else "",
            "part": part.display_title if part else "",
            "pdf_start": str(u.page_start),
            "pdf_end": str(u.page_end),
            "printed_start": "" if u.printed_start is None else str(u.printed_start),
            "printed_end": "" if u.printed_end is None else str(u.printed_end),
            "n_sections": str(len(sections)),
            "words": str(sum(len(n.text.split()) for n in [u, *inner])),
            **{f"has_{t}": "✓" if t in have else "" for t in section_types},
            **{k: "; ".join(u.attrs.get(k, [])) for k in attr_keys},
            "flags": ", ".join(u.flags),
            "unit_id": u.id,
        }
        rows.append(row)
    return columns, rows


def write_csv(path: Path, columns: Sequence[str], rows: Sequence[dict[str, str]]) -> None:
    """CSV cho Excel: UTF-8 có BOM, phân cách `,` (như phiếu duyệt loại mục của P2.4)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns))
        writer.writeheader()
        writer.writerows(rows)


def review_rows(views: Sequence[UnitView]) -> list[dict[str, str]]:
    """Phiếu chấm trống: mỗi bệnh trong mẫu một dòng."""
    return [
        {
            "unit_id": v.unit_id,
            "code": v.code,
            "title": v.title,
            "pdf_pages": "-".join(str(p) for p in (v.pages[0], v.pages[-1]) if v.pages)
            if len(v.pages) > 1
            else str(v.pages[0] if v.pages else ""),
            **{c: "" for c in CRITERIA},
            "note": "",
        }
        for v in views
    ]


# --------------------------------------------------------------------------- chấm


class ScoreResult(BaseModel):
    check: CheckResult
    unscored: list[str]  # "mã tên" của bệnh còn ô trống
    failed: list[str]  # "mã tên: tiêu chí sai - ghi chú"


def read_review(path: Path) -> list[dict[str, str]]:
    """Đọc phiếu chấm; chấp nhận `,` hoặc `;` (Excel tiếng Việt hay lưu bằng `;`)."""
    if not path.is_file():
        raise SpotcheckError(f"Không có phiếu chấm {path}")
    text = path.read_text(encoding="utf-8-sig")
    first = text.splitlines()[0] if text else ""
    delimiter = ";" if first.count(";") > first.count(",") else ","
    rows = list(csv.DictReader(io.StringIO(text), delimiter=delimiter))
    missing = [c for c in ("unit_id", *CRITERIA) if rows and c not in rows[0]]
    if not rows or missing:
        raise SpotcheckError(
            f"{path.name}: thiếu cột {', '.join(missing) or '(file rỗng)'} - dùng file do "
            "`p2 spotcheck` sinh ra hoặc nút 'Tải phiếu chấm' trong trang soát."
        )
    return rows


def score(
    rows: Sequence[dict[str, str]], sample_ids: Sequence[str], min_pass: float
) -> ScoreResult:
    """A9: bệnh đạt khi cả 4 tiêu chí = 1. Ô trống → chưa chấm (không tính điểm); giá trị khác
    0/1 → lỗi; bệnh không thuộc mẫu → lỗi (phiếu của lần chọn mẫu khác)."""
    by_id = {r.get("unit_id", "").strip(): r for r in rows}
    stray = [uid for uid in by_id if uid not in sample_ids]
    if stray:
        raise SpotcheckError(
            f"Phiếu chấm có {len(stray)} bệnh không thuộc mẫu hiện tại (vd. {stray[0]}) - phiếu "
            "của lần chọn mẫu khác? Chạy lại `p2 spotcheck` với đúng --n/--seed."
        )
    unscored: list[str] = []
    failed: list[str] = []
    bad: list[str] = []
    passed = 0
    for uid in sample_ids:
        row = by_id.get(uid)
        label = f"{row.get('code', '')} {row.get('title', '')}".strip() if row else uid
        values = {c: (row or {}).get(c, "").strip() for c in CRITERIA}
        if row is None or any(v == "" for v in values.values()):
            unscored.append(label)
            continue
        if any(v not in ("0", "1") for v in values.values()):
            bad.append(f"{label}: chỉ nhận 0 hoặc 1, gặp {sorted(set(values.values()))}")
            continue
        wrong = [CRITERIA_LABELS[c] for c, v in values.items() if v == "0"]
        if wrong:
            note = (row or {}).get("note", "").strip()
            failed.append(f"{label}: sai {', '.join(wrong)}" + (f" - {note}" if note else ""))
        else:
            passed += 1
    if bad:
        raise SpotcheckError("Giá trị chấm không hợp lệ:\n  - " + "\n  - ".join(bad))
    total = len(sample_ids)
    need = -(-min_pass * total // 1)  # làm tròn lên: 0.9 × 10 → 9
    done = total - len(unscored)
    check = CheckResult(
        id="A9",
        name="soát tay (đúng tên, ranh giới, mục, cột)",
        value=f"{passed}/{total} đạt" + (f" · {len(unscored)} chưa chấm" if unscored else ""),
        threshold=f"≥ {int(need)}/{total}",
        passed=not unscored and passed >= need and done == total,
        details=failed,
    )
    return ScoreResult(check=check, unscored=unscored, failed=failed)
