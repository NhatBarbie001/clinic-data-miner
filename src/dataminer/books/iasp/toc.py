"""Sách IASP - mục lục (L12, PDF 5-6). Xem docs/phases/P2R/I4_plan.md mục 4.

Dạng: tên ở bên trái, số trang in CÙNG HÀNG, căn phải (x ≈ 490-507); tên dài xuống dòng thì
dòng sau thụt vào và không có số:
    E.  Local Syndromes of the Upper Limbs and Relatively Generalized        121
        Syndromes of the Upper and Lower Limbs
        XI. Pain in the Shoulder, Arm, and Hand                              121
Chỉ lấy phần giữa "Part II" và "Part III" (mục lục Part I cũng có A.-H. nhưng trỏ danh mục mã).
Cấp: "A."-"H." → part; "XI." → chapter; tên khác ("Headache Crosswalk") → chapter (không số).
"""

import re
from collections.abc import Sequence
from pathlib import Path

from dataminer.books.iasp import layout, lines
from dataminer.core.config import FurnitureCfg, TocCfg
from dataminer.core.text_vi import nfc
from dataminer.model.line import Line
from dataminer.model.toc import TocEntry, TocLevel, TocResult
from dataminer.pdf.furniture import strip_furniture
from dataminer.pdf.reader import body_font_size, read_lines
from dataminer.structure.toc_match import norm_title

NUMBER_X = 450.0  # số trang căn phải: x ≥ 450; tên mục: x < 450
SAME_ROW = 4.0  # tên và số trang cùng hàng: lệch mép trên ≤ 4pt
RE_NUMBER = re.compile(r"^\d{1,3}$")
RE_FOOTER = re.compile(r"^[ivxlc]+$")  # số trang La Mã ở chân trang mục lục: "v", "vi"
RE_PART_START = re.compile(r"^Part\s+II\b(?!I)")  # "Part II   Detailed Descriptions …"
RE_PART_END = re.compile(r"^Part\s+III\b")
RE_TOC_LETTER = re.compile(r"^[A-H]\.\s")  # "E.  Local Syndromes …"
RE_TOC_ROMAN = re.compile(r"^([IVXLC]+)\.\s")  # "XI. Pain in the Shoulder …"
# so khớp với thân sách: bỏ "group xi:" / "xi." ở đầu (trên chữ đã chuẩn hóa)
RE_CHAPTER_PREFIX = re.compile(r"^(group\s+)?[ivxlc]+[.:]\s*")


def _norm(text: str) -> str:
    return " ".join(nfc(text).split())


def level_of(title: str) -> TocLevel:
    return "part" if RE_TOC_LETTER.match(title) else "chapter"


def parse_toc(toc_lines: Sequence[Line]) -> tuple[list[TocEntry], list[str]]:
    """Dòng của các trang mục lục → mục Part II (chưa có pdf_page) + cảnh báo."""
    rows = sorted(toc_lines, key=lambda ln: (ln.page, ln.bbox[1], ln.bbox[0]))
    numbers = [ln for ln in rows if ln.bbox[0] >= NUMBER_X and RE_NUMBER.match(_norm(ln.text))]
    titles = [
        ln
        for ln in rows
        if ln.bbox[0] < NUMBER_X
        and _norm(ln.text) != "CONTENTS"
        and not RE_FOOTER.match(_norm(ln.text))
    ]
    entries: list[TocEntry] = []
    warnings: list[str] = []
    inside = False
    for ln in titles:
        text = _norm(ln.text)
        if RE_PART_END.match(text):
            break
        if RE_PART_START.match(text):
            inside = True
            continue
        if not inside:
            continue
        number = next(
            (n for n in numbers if n.page == ln.page and abs(n.bbox[1] - ln.bbox[1]) <= SAME_ROW),
            None,
        )
        if number is None:
            if entries and ln.bbox[0] > entries[-1].x0 and ln.page == entries[-1].toc_pdf_page:
                last = entries[-1]
                last.title = f"{last.title} {text}"
                last.title_norm = norm_title(last.title)
            else:
                warnings.append(f"Mục lục: dòng '{text}' (PDF {ln.page}) không có số trang.")
            continue
        entries.append(
            TocEntry(
                title=text,
                title_norm=norm_title(text),
                level=level_of(text),
                printed_page=int(_norm(number.text)),
                pdf_page=None,
                toc_pdf_page=ln.page,
                line_id=ln.id,
                x0=ln.bbox[0],
            )
        )
    if not inside:
        warnings.append("Mục lục: không thấy dòng 'Part II' - không đọc được mục nào.")
    return entries, warnings


def printed_to_pdf_map(
    pdf: Path, book_id: str, pages: tuple[int, int], furniture: FurnitureCfg
) -> tuple[dict[int, int], list[str]]:
    """Trang in → trang PDF, từ số trang "Page 121" của các trang nội dung (như P1.2)."""
    content = read_lines(
        pdf,
        book_id=book_id,
        pages=pages,
        top_zone=furniture.top_zone,
        bottom_zone=furniture.bottom_zone,
        order=layout.column_order,
    )
    result = strip_furniture(
        content,
        body_font_size(content),
        furniture,
        pdf_pages=list(range(pages[0], pages[1] + 1)),
        page_number=lines.page_number,
    )
    mapping = {p.printed_page: p.page for p in result.pages if p.printed_page is not None}
    return mapping, result.warnings


def extract_toc(
    pdf: Path,
    *,
    book_id: str,
    cfg: TocCfg,
    content_pages: tuple[int, int],
    furniture: FurnitureCfg | None = None,
) -> TocResult:
    """Đọc mục lục (trang `cfg.pages`) + ánh xạ trang in → PDF trên `content_pages`."""
    furniture = furniture or FurnitureCfg()
    if cfg.pages == "auto":
        return TocResult(
            toc_pages=[],
            source="none",
            page_offset=None,
            entries=[],
            warnings=["IASP: cần đặt p2.toc.pages = [5, 6] (mục lục không có chấm dẫn)."],
        )
    toc_pages = list(range(cfg.pages[0], cfg.pages[1] + 1))
    toc_lines = read_lines(pdf, book_id=book_id, pages=cfg.pages, top_zone=0.0, bottom_zone=0.0)
    entries, warnings = parse_toc(toc_lines)
    printed_to_pdf, map_warnings = printed_to_pdf_map(pdf, book_id, content_pages, furniture)
    warnings += map_warnings
    offsets = {pdf_page - printed for printed, pdf_page in printed_to_pdf.items()}
    for e in entries:
        e.pdf_page = printed_to_pdf.get(e.printed_page)
        if e.pdf_page is None:
            e.flags.append("page_out_of_range")
            warnings.append(
                f"Mục lục '{e.title}': trang in {e.printed_page} không có trong phạm vi đã đọc."
            )
    return TocResult(
        toc_pages=toc_pages,
        source="config",
        page_offset=next(iter(offsets)) if len(offsets) == 1 else None,
        entries=entries,
        warnings=warnings,
    )


def toc_key(title: str) -> str | None:
    """Số hiệu của mục lục: "XI. Pain in …" → "XI"; "E. Local …" → "E"; tên khác → None."""
    text = _norm(title)
    if RE_TOC_LETTER.match(text):
        return text[0]
    m = RE_TOC_ROMAN.match(text)
    return m.group(1) if m else None
