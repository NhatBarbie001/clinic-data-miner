"""P2R I5 - trang soát `spotcheck/index.html`: ảnh trang PDF gốc (vùng chữ máy gán cho bệnh được
tô màu theo loại mục) ↔ nội dung đã tách, 4 ô chấm A9 mỗi bệnh, nút tải phiếu chấm CSV.

Một file HTML + `pages/p0137.jpg`…; không thư viện ngoài, không cần mạng. Mọi chữ của sách đều
được escape. Kết quả chỉ phụ thuộc dữ liệu đầu vào (không ghi giờ) → chạy lại ra giống hệt.
"""

import html
import json
from collections.abc import Sequence
from pathlib import Path

import pymupdf

from dataminer.evaluation.spotcheck import CRITERIA, CRITERIA_LABELS, REVIEW_COLUMNS, UnitView
from dataminer.structure.section_mapper import SECTION_TYPES

JPEG_QUALITY = 75
ASSETS = Path(__file__).parent / "assets"
CSS = (ASSETS / "spotcheck.css").read_text(encoding="utf-8")
JS = (ASSETS / "spotcheck.js").read_text(encoding="utf-8")


def page_file(page: int) -> str:
    return f"pages/p{page:04d}.jpg"


def render_page_images(pdf: Path, pages: Sequence[int], dpi: int, out_dir: Path) -> list[Path]:
    """Ảnh JPEG của các trang PDF (số trang 1-based) vào `out_dir/pages/`."""
    (out_dir / "pages").mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    with pymupdf.open(pdf) as doc:
        for page in sorted(set(pages)):
            target = out_dir / page_file(page)
            pix = doc[page - 1].get_pixmap(dpi=dpi)
            target.write_bytes(pix.tobytes("jpeg", jpg_quality=JPEG_QUALITY))
            written.append(target)
    return written


def type_color(section_type: str | None) -> str:
    """Mỗi loại mục một màu cố định (cùng màu ở mọi bệnh); bệnh/tên = đỏ."""
    if section_type is None:
        return "hsl(0 85% 50%)"
    i = SECTION_TYPES.index(section_type) if section_type in SECTION_TYPES else 0
    return f"hsl({(i * 360 // len(SECTION_TYPES) + 40) % 360} 75% 45%)"


def _e(text: str) -> str:
    return html.escape(text, quote=True)


def _card(v: UnitView, index: int, total: int, *, scored: bool) -> str:
    color = {p.node_id: type_color(p.section_type if p.depth else None) for p in v.parts}
    pages_html = []
    for page in v.pages:
        boxes = "".join(
            f'<i class="box{" title" if b.node_id == v.unit_id else ""}" data-node="{b.node_id}" '
            f'style="left:{b.left}%;top:{b.top}%;width:{b.width}%;height:{b.height}%;'
            f'--c:{color[b.node_id]}"></i>'
            for b in v.boxes
            if b.page == page
        )
        pages_html.append(
            f'<figure class="page"><img src="{page_file(page)}" alt="trang PDF {page}" '
            f'loading="lazy">{boxes}<figcaption>PDF {page}</figcaption></figure>'
        )
    parts_html = []
    for p in v.parts:
        kind = f' <span class="tag">{_e(p.section_type)}</span>' if p.section_type else ""
        body = (
            "".join(f"<p>{_e(t)}</p>" for t in p.texts)
            or '<p class="muted">(không có nội dung riêng)</p>'
        )
        parts_html.append(
            f'<section class="part d{p.depth}" data-node="{p.node_id}" '
            f'style="--c:{color[p.node_id]}">'
            f"<h4>{_e(p.title)}{kind}</h4>{body}</section>"
        )
    facts = [f"Mã: <b>{_e(v.code or '(không mã)')}</b>", f"Nhóm: {_e(v.group)}"]
    facts += [f"{_e(k)}: {_e(', '.join(vals))}" for k, vals in v.attrs.items() if k != "codes"]
    if v.flags:
        facts.append(f'<span class="flag">Cờ: {_e(", ".join(v.flags))}</span>')
    pages = f"PDF {v.pages[0]}" + (f"-{v.pages[-1]}" if len(v.pages) > 1 else "") if v.pages else ""
    review = ""
    if scored:
        checks = "".join(
            f'<label><input type="checkbox" data-crit="{c}"> {_e(CRITERIA_LABELS[c])}</label>'
            for c in CRITERIA
        )
        review = (
            f'<div class="review">{checks}<label class="note">Ghi chú '
            f'<input type="text" data-crit="note"></label>'
            f'<button type="button" class="mark-bad">Có lỗi</button></div>'
        )
    head = f"{index}/{total} · " if scored else ""
    return (
        f'<article class="unit" id="u-{v.unit_id}" data-unit="{v.unit_id}" '
        f'data-code="{_e(v.code)}" data-title="{_e(v.title)}" '
        f'data-pages="{_e(pages.removeprefix("PDF "))}">'
        f"<header><h3>{head}{_e(v.title)}</h3><p>{' · '.join(facts)} · {pages} · "
        f"{v.n_blocks} block</p></header>"
        f'<div class="cols"><div class="pages">{"".join(pages_html)}</div>'
        f'<div class="text">{"".join(parts_html)}</div></div>{review}</article>'
    )


def render_html(
    sample: Sequence[UnitView],
    extras: Sequence[UnitView],
    *,
    book_title: str,
    unit_label: str,
    meta: dict[str, object],
) -> str:
    """Trang soát: phần 1 = mẫu ngẫu nhiên (có ô chấm, tính A9); phần 2 = bệnh có cờ / chọn thêm
    (chỉ để xem). `meta` (sha cây, seed, n) được nhúng để phiếu chấm gắn đúng bản cây."""
    legend = "".join(
        f'<span class="tag" style="--c:{type_color(t)}">{t}</span>' for t in SECTION_TYPES
    )
    cards = "".join(_card(v, i, len(sample), scored=True) for i, v in enumerate(sample, 1))
    extra_cards = "".join(_card(v, 0, 0, scored=False) for v in extras)
    extra = (
        f"<h2>Để bạn xem thêm ({len(extras)}) - KHÔNG tính vào A9</h2>"
        "<p>Bệnh có cờ cảnh báo và bệnh bạn chọn thêm (--codes).</p>" + extra_cards
        if extras
        else ""
    )
    data = json.dumps({**meta, "columns": REVIEW_COLUMNS, "criteria": CRITERIA}, ensure_ascii=False)
    data = data.replace("</", "<\\/")  # chữ trong dữ liệu không được đóng thẻ <script>
    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Soát tay - {_e(book_title)}</title>
<style>{CSS}</style></head>
<body>
<header class="top"><h1>Soát tay: {_e(book_title)}</h1>
<p>{len(sample)} {_e(unit_label)} ngẫu nhiên (seed {_e(str(meta.get("seed")))}) · cây
<code>{_e(str(meta.get("nodes_sha256", ""))[:12])}</code> ·
<b id="progress">0/{len(sample)} đã chấm</b>
<button type="button" id="download">Tải phiếu chấm (CSV)</button></p>
<details><summary>Cách soát (đọc 1 lần)</summary>
<ol><li><b>Bên trái</b> là ảnh trang PDF gốc. Vùng chữ máy gán cho {_e(unit_label)} này được
<b>tô màu</b> (tên: viền đỏ; mỗi loại mục một màu).</li>
<li>Chữ của {_e(unit_label)} này mà <b>không được tô</b> = bị sót / bị gán cho nút khác.
Vùng tô <b>lan sang</b> {_e(unit_label)} khác = sai ranh giới.</li>
<li><b>Bên phải</b> là nội dung máy tách ra. Rê chuột lên một mục → vùng chữ của mục đó
nháy viền.</li>
<li>Tích đủ 4 ô nếu đúng; sai tiêu chí nào thì để trống ô đó, bấm <b>Có lỗi</b> và ghi chú ngắn.
Bấm <b>Tải phiếu chấm</b> → chạy <code>dm p2 spotcheck score --file &lt;file vừa tải&gt;</code>.
(Hoặc sửa thẳng <code>review.csv</code> bằng Excel: 1 = đúng, 0 = sai.)</li></ol>
<p>Màu loại mục: {legend}</p></details></header>
<main>{cards}{extra}</main>
<script id="meta" type="application/json">{data}</script>
<script>{JS}</script>
</body></html>
"""
