"""P2.1 - Mục lục: tự tìm trang mục lục, tách từng dòng thành (tiêu đề, cấp, số trang in).

Mục lục là "đáp án do chính sách cung cấp" để P2.2-P2.3 đối chiếu. Không dùng LLM: tiêu đề
được giữ NGUYÊN VĂN OCR (có thể còn lỗi, vd. "Bệnh tiêu hỏa"); so khớp ở các bước sau dùng
`title_norm` / `match_key` (không dấu) nên lỗi dấu và lỗi dính từ không ảnh hưởng.
Xem docs/phases/P2/P2.1_plan.md.
"""

import re
from collections.abc import Sequence
from itertools import pairwise
from pathlib import Path
from typing import Literal

from dataminer.core.config import FurnitureCfg, TocCfg
from dataminer.core.text_vi import nfc
from dataminer.model.line import Line
from dataminer.model.toc import TocEntry, TocLevel, TocResult
from dataminer.pdf.reader import read_lines
from dataminer.structure.toc_match import content_page_offset, norm_title

# Chấm dẫn: "....", ". . . .", "……" (≥ 3 dấu chấm, có thể cách nhau 1 khoảng trắng) + số trang.
RE_LEADER_ENTRY = re.compile(
    r"^(?P<title>.*?\S)\s*(?:(?:\.\s?){3,}|(?:…\s?)+)\s*(?P<page>\d{1,4})$"
)
# Không có chấm dẫn (PDF chỉ có khoảng trắng): "Hen phế quản 57", "Đái tháo đường type 2 61".
# Chỉ dùng TRONG trang mục lục; tiêu đề phải có chữ cái.
RE_PLAIN_ENTRY = re.compile(r"^(?P<title>.*[^\W\d_].*?)\s+(?P<page>\d{1,4})$")
# Mẫu chương, so trên chữ đã bỏ dấu + chữ thường: "Chương 1.", "CHUONG II", "Phần 2".
RE_CHAPTER_NORM = re.compile(r"^(chuong|phan)\s+([0-9]+|[ivxlc]+)\b")
TOC_TITLES = frozenset({"muc luc", "noi dung", "contents", "table of contents"})
INDENT_TOLERANCE = 3.0  # hai dòng cùng mức thụt lề nếu x0 lệch ≤ 3pt


# --------------------------------------------------------------------------- tìm trang


def parse_entry_line(text: str, *, allow_plain: bool = False) -> tuple[str, int] | None:
    """Tách "<tiêu đề> ........ <số trang>" → (tiêu đề, số trang); không khớp → None."""
    text = " ".join(nfc(text).split())
    match = RE_LEADER_ENTRY.match(text)
    if match is None and allow_plain:
        match = RE_PLAIN_ENTRY.match(text)
    if match is None:
        return None
    title = match.group("title").rstrip(" .…")
    return (title, int(match.group("page"))) if title else None


def find_toc_pages(lines: Sequence[Line], search_pages: int, min_entries: int) -> list[int]:
    """Trang mục lục = trang trong `search_pages` trang đầu có ≥ `min_entries` dòng chấm dẫn.

    Mục lục nhiều trang: lấy dải trang LIÊN TIẾP bắt đầu từ trang đầu tiên đạt ngưỡng (một trang
    lẻ loi về sau, vd. bảng tra cứu có chấm dẫn, không bị gộp vào).
    """
    counts: dict[int, int] = {}
    for ln in lines:
        if ln.page <= search_pages and ln.zone == "body" and parse_entry_line(ln.text):
            counts[ln.page] = counts.get(ln.page, 0) + 1
    hits = sorted(p for p, n in counts.items() if n >= min_entries)
    if not hits:
        return []
    pages = [hits[0]]
    while pages[-1] + 1 in hits:
        pages.append(pages[-1] + 1)
    return pages


# --------------------------------------------------------------------------- phân tích


def _indent_ranks(xs: Sequence[float]) -> list[int]:
    """Gom các lề trái gần nhau thành mức thụt lề; trả hạng (0 = ít thụt nhất) cho từng x."""
    levels: list[float] = []
    for x in sorted(xs):
        if not levels or x - levels[-1] > INDENT_TOLERANCE:
            levels.append(x)
    return [max(i for i, lv in enumerate(levels) if x >= lv - INDENT_TOLERANCE) for x in xs]


def _is_toc_title(text: str) -> bool:
    return norm_title(text).rstrip(" .:") in TOC_TITLES


def _is_chapter(title: str) -> bool:
    return RE_CHAPTER_NORM.match(norm_title(title)) is not None


def parse_toc(lines: Sequence[Line], toc_pages: Sequence[int]) -> tuple[list[TocEntry], list[str]]:
    """Phân tích các dòng của trang mục lục → mục (chưa có pdf_page) + cảnh báo.

    - Dòng không có số trang mà dòng NGAY SAU là một mục → tiêu đề bị ngắt 2 dòng, nối lại
      (trừ tiêu đề "MỤC LỤC" và dòng cách xa).
    - Cấp: khớp mẫu "Chương n"/"Phần n" → chapter (bằng chứng mạnh). Không khớp mẫu mà mục lục
      có ≥ 2 mức thụt lề → theo thụt lề (mức 0 = chapter): lỗi OCR có thể phá chữ ("Cbương 1")
      nhưng không phá được vị trí. Mẫu chữ và thụt lề mâu thuẫn → cờ `level_conflict`.
    """
    pages = set(toc_pages)
    body = [ln for ln in lines if ln.page in pages and ln.zone == "body"]
    raw: list[tuple[str, int, Line]] = []  # (tiêu đề, số trang, dòng đầu)
    pending: Line | None = None
    for i, ln in enumerate(body):
        parsed = parse_entry_line(ln.text, allow_plain=True)
        if parsed is None:
            pending = None if _is_toc_title(ln.text) else ln
            continue
        title, page = parsed
        first = ln
        if pending is not None and pending.page == ln.page and i > 0 and body[i - 1] is pending:
            gap = ln.bbox[1] - pending.bbox[3]
            if gap <= 1.0 * max(ln.size, pending.size):
                title = f"{pending.text} {title}"
                first = pending
        pending = None
        raw.append((" ".join(title.split()), page, first))

    warnings: list[str] = []
    if not raw:
        return [], warnings
    ranks = _indent_ranks([first.bbox[0] for _, _, first in raw])
    multi_indent = max(ranks) > 0
    entries: list[TocEntry] = []
    for (title, page, first), rank in zip(raw, ranks, strict=True):
        flags: list[str] = []
        by_pattern = _is_chapter(title)
        by_indent: TocLevel | None = (
            ("chapter" if rank == 0 else "disease") if multi_indent else None
        )
        level: TocLevel
        if by_pattern:
            level = "chapter"
        elif by_indent is not None:
            level = by_indent
        else:
            level = "disease"
        if by_indent is not None and by_indent != ("chapter" if by_pattern else "disease"):
            flags.append("level_conflict")
            warnings.append(
                f"Mục lục '{title}': mẫu chữ cho {'chapter' if by_pattern else 'disease'} nhưng "
                f"thụt lề cho {by_indent} → chọn {level} (lỗi OCR ở chữ 'Chương'?)."
            )
        entries.append(
            TocEntry(
                title=title,
                title_norm=norm_title(title),
                level=level,
                printed_page=page,
                pdf_page=None,
                toc_pdf_page=first.page,
                line_id=first.id,
                x0=round(first.bbox[0], 1),
                flags=flags,
            )
        )
    for prev, cur in pairwise(entries):
        if cur.printed_page < prev.printed_page:
            cur.flags.append("page_decreasing")
            warnings.append(
                f"Mục lục: số trang giảm ở '{cur.title}' ({prev.printed_page} → "
                f"{cur.printed_page}) - OCR đọc nhầm số?"
            )
    return entries, warnings


# --------------------------------------------------------------------------- toàn bộ


def build_toc(
    lines: Sequence[Line],
    cfg: TocCfg | None = None,
    furniture: FurnitureCfg | None = None,
) -> TocResult:
    """Mục lục từ các dòng của CẢ sách (cần các trang nội dung để ánh xạ số trang in)."""
    cfg = cfg or TocCfg()
    if cfg.pages == "auto":
        toc_pages = find_toc_pages(lines, cfg.search_pages, cfg.min_entries)
        source: Literal["auto", "config", "none"] = "auto" if toc_pages else "none"
    else:
        toc_pages = list(range(cfg.pages[0], cfg.pages[1] + 1))
        source = "config"
    if not toc_pages:
        return TocResult(
            toc_pages=[],
            source="none",
            page_offset=None,
            entries=[],
            warnings=[
                f"Không tìm thấy mục lục trong {cfg.search_pages} trang đầu (cần ≥ "
                f"{cfg.min_entries} dòng chấm dẫn/trang). P2 vẫn chạy, chỉ thiếu bước đối chiếu; "
                "nếu sách có mục lục, đặt p2.toc.pages = [a, b]."
            ],
        )

    entries, warnings = parse_toc(lines, toc_pages)
    if not entries:
        warnings.append(f"Trang mục lục {toc_pages} không có dòng nào tách được thành mục.")
    content = [ln for ln in lines if ln.page not in set(toc_pages)]
    offset, printed_to_pdf, map_warnings = content_page_offset(content, furniture)
    warnings.extend(map_warnings)
    max_printed = max(printed_to_pdf, default=None)
    for e in entries:
        e.pdf_page = printed_to_pdf.get(e.printed_page)
        if e.pdf_page is None:
            e.flags.append("page_out_of_range")
            warnings.append(
                f"Mục lục '{e.title}': trang in {e.printed_page} không có trong sách "
                f"(trang in lớn nhất {max_printed})."
            )
    return TocResult(
        toc_pages=list(toc_pages),
        source=source,
        page_offset=offset,
        entries=entries,
        warnings=warnings,
    )


def extract_toc(
    pdf: Path,
    *,
    book_id: str,
    cfg: TocCfg | None = None,
    furniture: FurnitureCfg | None = None,
) -> TocResult:
    """Đọc PDF (mọi trang: trang mục lục + footer các trang nội dung) → mục lục."""
    furniture = furniture or FurnitureCfg()
    lines = read_lines(
        pdf, book_id=book_id, top_zone=furniture.top_zone, bottom_zone=furniture.bottom_zone
    )
    return build_toc(lines, cfg, furniture)
