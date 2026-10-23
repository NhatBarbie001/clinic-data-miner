"""P1.3 - Dựng block: tiêu đề, đoạn văn, gạch đầu dòng, bảng (hàng × cột), chú thích, mục lục.

Nối các dòng bị ngắt (kể cả qua trang) thành đoạn/gạch đầu dòng, gom ô bảng thành hàng.
P1 KHÔNG quyết định cấp tiêu đề - chỉ gắn đặc trưng (numbering, is_upper, font_size, x0) cho P2.
Xem docs/phases/P1/P1.3_plan.md.
"""

import itertools
import re
import statistics
from collections.abc import Callable, Iterable
from typing import Any, Literal

from dataminer.core.config import BlocksCfg
from dataminer.core.schemas import stable_id
from dataminer.core.text_vi import has_vietnamese_marks, nfc
from dataminer.model.block import Block, BlockKind
from dataminer.model.line import Line
from dataminer.pdf.layout import ROW_TOLERANCE

RE_NUMBERED_ITEM = re.compile(r"^(\d{1,2})[.)]\s+\S")
SENTENCE_END = (".", ":", ";", "?", "!", "…")


# --------------------------------------------------------------------------- đặc trưng dòng


def is_upper_text(text: str) -> bool:
    letters = [c for c in nfc(text) if c.isalpha()]
    return len(letters) >= 3 and sum(c.isupper() for c in letters) / len(letters) >= 0.8


def bullet_marker(text: str, markers: Iterable[str]) -> str | None:
    for marker in markers:
        if text.startswith(marker) and len(text) > len(marker) and text[len(marker)].isspace():
            return marker
    return None


LineKind = Literal["toc_entry", "caption", "heading", "bullet_start", "numbered_item", "body"]
# Luật riêng từng sách (books/<sách>/): dòng nào là gì, và số thứ tự của một tiêu đề.
ClassifyLine = Callable[[Line, float, BlocksCfg], LineKind]
Numbering = Callable[[str], str | None]
# (tiêu đề đang mở, dòng tiêu đề kế tiếp) → nối thành một tiêu đề? (khoảng cách dòng xét riêng)
HeadingJoins = Callable[[str, str], bool]


def default_heading_joins(prev: str, text: str, numbering: Numbering) -> bool:
    """Luật nối tiêu đề MẶC ĐỊNH (sách mẫu): dòng sau không đánh số và cùng kiểu IN HOA."""
    return not numbering(text) and is_upper_text(text) == is_upper_text(prev)


# --------------------------------------------------------------------------- block


# mảnh cuối dòng "dis-", "(rec-" - không nhận "side-to-" (từ ghép đã có gạch)
RE_HYPHEN_FRAGMENT = re.compile(r"(?<![A-Za-z-])([A-Za-z]{2,})-$")
# tiền tố thường viết CÓ gạch nối: "anti-" + "inflammatory" giữ gạch dù ngắt ở cuối dòng
HYPHEN_PREFIXES = frozenset(
    {"anti", "non", "self", "co", "semi", "pseudo", "multi", "half", "well", "cross", "post", "pre"}
)
COLUMN_JUMP = 100.0  # dòng tiếp lệch ngang > 100pt = sang cột khác (sách 1 cột không bao giờ)


class Vocab:
    """Từ vựng của chính cuốn sách, để quyết định bỏ hay giữ gạch nối cuối dòng."""

    def __init__(self, texts: Iterable[str]) -> None:
        self.hyphenated: set[str] = set()  # "anti-inflammatory" gặp GIỮA dòng
        self.words: set[str] = set()  # "present" gặp như một từ
        for text in texts:
            tokens = [t.strip(".,;:()[]\"'“”‘’").lower() for t in text.split()]
            for tok in tokens[:-1]:  # bỏ từ cuối dòng (có thể là mảnh bị ngắt)
                (self.hyphenated if "-" in tok else self.words).add(tok)


def _dehyphenate(left: str, right: str, vocab: "Vocab | None") -> bool:
    """Bỏ gạch giữa `left`- và `right`? Ưu tiên bằng chứng trong sách, rồi danh sách tiền tố."""
    if vocab is not None:
        if f"{left}-{right}".lower() in vocab.hyphenated:
            return False  # sách viết có gạch ở chỗ khác ("anti-inflammatory")
        if f"{left}{right}".lower() in vocab.words:
            return True  # sách có từ liền ("present")
    return left.lower() not in HYPHEN_PREFIXES


def join_text(prev: str, nxt: str, dehyphenate: bool = False, vocab: "Vocab | None" = None) -> str:
    """Nối 2 dòng: thêm khoảng trắng; giữ gạch nối giữa 2 phần Latin không dấu (anti- + CCP).

    `dehyphenate` (sách tiếng Anh ngắt từ cuối dòng): "dis-" + "ease" → "disease" khi phần sau
    bắt đầu bằng chữ thường và phần trước là MỘT từ (từ ghép "side-to-" + "side" giữ gạch).
    `vocab`: từ vựng của sách - phân biệt "pre-" + "sent" (present) với "anti-" + "inflammatory"."""
    if dehyphenate and nxt[:1].islower() and prev.split():
        frag = RE_HYPHEN_FRAGMENT.search(prev.split()[-1])
        right = re.match(r"[a-z]+", nxt)
        if frag and right and _dehyphenate(frag.group(1), right.group(0), vocab):
            return prev[:-1] + nxt
    if prev.endswith("-") and nxt[:1].isascii() and nxt[:1].isalpha():
        last = prev.split()[-1] if prev.split() else ""
        # chỉ khi trước gạch là chữ ("anti-"); gạch đứng riêng ("… -") là dấu câu
        if last[:-1][-1:].isalpha() and not has_vietnamese_marks(last):
            return prev + nxt
    return f"{prev} {nxt}"


def _center(ln: Line) -> float:
    return (ln.bbox[1] + ln.bbox[3]) / 2


def group_rows(lines: list[Line]) -> list[list[Line]]:
    """Gom các dòng (đã theo thứ tự đọc) cùng dải dọc thành hàng."""
    rows: list[list[Line]] = []
    for ln in lines:
        if rows and ln.page == rows[-1][0].page:
            first = rows[-1][0]
            if abs(_center(ln) - _center(first)) < ROW_TOLERANCE * min(ln.size, first.size):
                rows[-1].append(ln)
                continue
        rows.append([ln])
    return rows


def _column_positions(cells: list[Line], gap: float = 10.0) -> list[float]:
    xs = sorted(c.bbox[0] for c in cells)
    cols = [xs[0]]
    for x in xs[1:]:
        if x - cols[-1] > gap:
            cols.append(x)
    return cols


def _fits_table(row: list[Line], table: list[list[Line]], neighbour: list[Line]) -> bool:
    """Hàng 1 dòng (thiếu ô) sát bảng có thuộc bảng không: cùng trang, cách hàng kề đúng nhịp
    hàng của bảng, thẳng lề một cột, và KHÔNG tràn sang cột kế tiếp (đoạn văn sau bảng chạy
    hết chiều ngang nên bị loại)."""
    (cell,) = row
    if cell.page != neighbour[0].page:
        return False
    cells = [c for r in table for c in r]
    cols = _column_positions(cells)
    steps = [abs(_center(r2[0]) - _center(r1[0])) for r1, r2 in itertools.pairwise(table)]
    row_step = statistics.median(steps) if steps else 2 * cell.size
    if abs(_center(cell) - _center(neighbour[0])) > 1.5 * row_step:
        return False
    idx = min(range(len(cols)), key=lambda i: abs(cols[i] - cell.bbox[0]))
    if abs(cols[idx] - cell.bbox[0]) > 10:
        return False
    return idx == len(cols) - 1 or cell.bbox[2] < cols[idx + 1]


def find_tables(lines: list[Line], cfg: BlocksCfg) -> list[list[list[Line]]]:
    """Bảng = các hàng liên tiếp cùng trang, trong đó ≥ table_min_rows hàng "đủ" (≥ table_min_cells
    dòng cùng dải dọc - văn bản một cột không bao giờ có 2 dòng cùng dải dọc), cộng các hàng
    thiếu ô (1 dòng) nằm xen giữa hoặc sát bảng và khớp cột (`_fits_table`)."""
    rows = [sorted(r, key=lambda c: c.bbox[0]) for r in group_rows(lines)]
    wide = [len(r) >= cfg.table_min_cells for r in rows]
    member = list(wide)

    def block_around(k: int) -> list[list[Line]]:
        lo = hi = k
        while lo > 0 and member[lo - 1] and rows[lo - 1][0].page == rows[k][0].page:
            lo -= 1
        while hi + 1 < len(rows) and member[hi + 1] and rows[hi + 1][0].page == rows[k][0].page:
            hi += 1
        return rows[lo : hi + 1]

    changed = True
    while changed:
        changed = False
        for k, row in enumerate(rows):
            if member[k] or len(row) != 1:
                continue
            for nb in (k - 1, k + 1):
                if (
                    0 <= nb < len(rows)
                    and member[nb]
                    and _fits_table(row, block_around(nb), rows[nb])
                ):
                    member[k] = changed = True
                    break

    tables: list[list[list[Line]]] = []
    k = 0
    while k < len(rows):
        if not member[k]:
            k += 1
            continue
        run = block_around(k)
        if sum(len(r) >= cfg.table_min_cells for r in run) >= cfg.table_min_rows:
            tables.append(run)
        k += len(run)
    return tables


def _table_block(rows: list[list[Line]], book_id: str) -> Block:
    cells = [c for row in rows for c in row]
    cols = _column_positions(cells)
    grid: list[list[str]] = []
    for row in rows:
        values = [""] * len(cols)
        for cell in row:
            idx = min(range(len(cols)), key=lambda i: abs(cols[i] - cell.bbox[0]))
            values[idx] = f"{values[idx]} {cell.text}".strip()
        grid.append(values)
    first = rows[0][0]
    return Block(
        id=stable_id(book_id, first.page, first.index, prefix="blk"),
        kind="table",
        text="\n".join(" | ".join(r) for r in grid),
        text_rules="\n".join(" | ".join(r) for r in grid),
        page_start=first.page,
        page_end=rows[-1][0].page,
        line_ids=[c.id for c in cells],
        bbox=first.bbox,
        x0=min(c.bbox[0] for c in cells),
        font_size=round(statistics.fmean(c.size for c in cells), 2),
        rows=grid,
    )


def _line_step(lines: list[Line]) -> float:
    """Khoảng cách dọc điển hình giữa 2 dòng liên tiếp (trung vị), đo bằng MÉP DƯỚI:
    mép trên dao động theo cỡ chữ OCR ước lượng (±6% × phần trên chữ ≈ ±1.3pt), mép dưới
    chỉ ≈ ±0.4pt - đủ ổn định để phân biệt dòng tiếp (0pt dôi) với đoạn mới (~4pt dôi)."""
    steps = [
        b.bbox[3] - a.bbox[3]
        for a, b in itertools.pairwise(lines)
        if a.page == b.page and 0 < b.bbox[3] - a.bbox[3] < 3 * a.size
    ]
    return statistics.median(steps) if steps else 14.0


class _Open:
    """Block đang được nối thêm dòng."""

    def __init__(self, kind: BlockKind, ln: Line, text: str, marker: str | None) -> None:
        self.kind = kind
        self.lines = [ln]
        self.text = text
        self.marker = marker
        self.flags: list[str] = []

    @property
    def last(self) -> Line:
        return self.lines[-1]


def build_blocks(
    lines: list[Line],
    body_size: float,
    cfg: BlocksCfg | None = None,
    printed: dict[int, int | None] | None = None,
    book_id: str = "book",
    *,
    classify: ClassifyLine,
    numbering: Numbering,
    heading_joins: HeadingJoins | None = None,
) -> list[Block]:
    """Dựng block từ dòng NỘI DUNG (đã bỏ header/footer), theo thứ tự đọc.

    `classify` (dòng nào là tiêu đề / gạch đầu dòng / …), `numbering` (số thứ tự của tiêu đề) và
    `heading_joins` (tiêu đề nhiều dòng nối thế nào; mặc định `default_heading_joins`) là LUẬT
    RIÊNG của từng sách - truyền vào từ books/<sách>/."""
    cfg = cfg or BlocksCfg()
    joins = heading_joins or (lambda prev, text: default_heading_joins(prev, text, numbering))
    printed = printed or {}
    step = _line_step(lines)
    vocab = Vocab(ln.text for ln in lines) if cfg.dehyphenate else None
    table_of: dict[str, int] = {}
    tables = find_tables(lines, cfg) if cfg.detect_tables else []
    for t_idx, rows in enumerate(tables):
        for row in rows:
            for cell in row:
                table_of[cell.id] = t_idx

    out: list[Block] = []
    current: _Open | None = None

    def close() -> None:
        nonlocal current
        if current is not None:
            out.append(_to_block(current, book_id, printed, numbering))
            current = None

    emitted_tables: set[int] = set()
    for ln in lines:
        if ln.id in table_of:
            t_idx = table_of[ln.id]
            if t_idx not in emitted_tables:
                close()
                block = _table_block(tables[t_idx], book_id)
                block.printed_start = printed.get(block.page_start)
                block.printed_end = printed.get(block.page_end)
                out.append(block)
                emitted_tables.add(t_idx)
            continue

        kind = classify(ln, body_size, cfg)
        text = nfc(ln.text)
        if kind == "body" and current is not None and _continues(current, ln, step, cfg):
            if ln.page != current.last.page:
                current.flags.append("joined_across_pages")
            current.text = join_text(current.text, text, cfg.dehyphenate, vocab)
            current.lines.append(ln)
            continue
        if (
            kind == "heading"
            and current is not None
            and _heading_continues(current, ln, step, joins)
        ):
            current.text = join_text(current.text, text, cfg.dehyphenate, vocab)
            current.lines.append(ln)
            continue

        close()
        if kind == "bullet_start":
            marker = bullet_marker(text, cfg.bullet_markers)
            assert marker is not None
            current = _Open("list_item", ln, text[len(marker) :].strip(), marker)
        elif kind == "numbered_item":
            m = RE_NUMBERED_ITEM.match(text)
            assert m is not None
            marker = text[: m.end(1) + 1]
            current = _Open("list_item", ln, text[len(marker) :].strip(), marker)
        elif kind == "body":
            current = _Open("paragraph", ln, text, None)
        else:
            current = _Open(kind, ln, text, None)
    close()
    return out


def _continues(cur: _Open, ln: Line, step: float, cfg: BlocksCfg) -> bool:
    """Dòng thân bài `ln` có phải phần tiếp của block đang mở không?"""
    if cur.kind not in ("paragraph", "list_item"):
        return False
    prev = cur.last
    # sang cột khác (sách nhiều cột): lệch ngang lớn, và đi lên trên hoặc sang trang
    column_jump = abs(ln.bbox[0] - prev.bbox[0]) > COLUMN_JUMP and (
        ln.page != prev.page or ln.bbox[1] < prev.bbox[1]
    )
    if ln.page != prev.page or column_jump:  # chỉ nối khi câu trước chưa kết thúc
        if not cfg.join_across_pages or cur.text.rstrip().endswith(SENTENCE_END):
            return False
        if column_jump:  # lề trái của cột mới khác cột cũ → không so lề
            cur.flags.append("joined_across_columns")
            return True
    elif ln.bbox[3] - prev.bbox[3] - step >= cfg.para_gap_ratio * ln.size:
        return False  # khoảng cách dôi ra → đoạn mới
    if cur.kind == "list_item":
        # dòng tiếp của gạch đầu dòng thụt vào so với ký hiệu
        return ln.bbox[0] > cur.lines[0].bbox[0] + cfg.x_tolerance
    margin = min(x.bbox[0] for x in cur.lines)
    if abs(ln.bbox[0] - margin) <= cfg.x_tolerance:
        return True
    # đoạn thụt dòng đầu: dòng tiếp lùi về lề trái
    return len(cur.lines) == 1 and ln.bbox[0] < cur.lines[0].bbox[0] - cfg.x_tolerance


def _heading_continues(cur: _Open, ln: Line, step: float, joins: HeadingJoins) -> bool:
    """Tiêu đề dài xuống dòng: cùng trang, cùng cỡ, sát ngay dòng trước, và luật của sách cho
    nối (`joins`)."""
    if cur.kind != "heading" or ln.page != cur.last.page:
        return False
    close = ln.bbox[3] - cur.last.bbox[3] <= 1.3 * max(step, cur.last.size * 1.2)
    return abs(ln.size - cur.last.size) < 0.8 and close and joins(cur.text, ln.text)


def _to_block(
    cur: _Open, book_id: str, printed: dict[int, int | None], numbering: Numbering
) -> Block:
    first = cur.lines[0]
    sizes = [(ln.size, len(ln.text)) for ln in cur.lines]
    total = sum(w for _, w in sizes) or 1
    flags = sorted(set(cur.flags) | {f for ln in cur.lines for f in ln.flags})
    return Block(
        id=stable_id(book_id, first.page, first.index, prefix="blk"),
        kind=cur.kind,
        text=cur.text,
        text_rules=cur.text,
        page_start=first.page,
        page_end=cur.last.page,
        printed_start=printed.get(first.page),
        printed_end=printed.get(cur.last.page),
        line_ids=[ln.id for ln in cur.lines],
        bbox=first.bbox,
        x0=first.bbox[0],
        font_size=round(sum(s * w for s, w in sizes) / total, 2),
        is_upper=is_upper_text(cur.text),
        numbering=numbering(cur.text) if cur.kind == "heading" else None,
        marker=cur.marker,
        flags=flags,
    )


def blocks_summary(blocks: list[Block]) -> dict[str, Any]:
    kinds: dict[str, int] = {}
    for b in blocks:
        kinds[b.kind] = kinds.get(b.kind, 0) + 1
    return {
        "blocks": len(blocks),
        "by_kind": kinds,
        "joined_across_pages": sum("joined_across_pages" in b.flags for b in blocks),
    }
