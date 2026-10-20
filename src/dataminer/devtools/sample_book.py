"""Sinh sách mẫu tổng hợp kiểu "scan + OCR" kèm đáp án - để kiểm thử pipeline.

Mỗi trang PDF gồm 2 lớp giống sách scan đã OCR thật:
  - lớp ẢNH: trang được dàn sạch rồi chụp thành ảnh xám có nhiễu (cái người đọc thấy);
  - lớp TEXT ẨN (render_mode=3): văn bản đã bị làm lỗi kiểu OCR, một font thường duy nhất
    (mất thông tin in đậm), cỡ chữ ước lượng có nhiễu (cái máy đọc được).
Đáp án (`*.truth.json`) ghi lại chính xác cấu trúc, header/footer và từng lỗi OCR đã cài.
Sinh xác định: cùng seed → cùng nội dung và cùng đáp án.

Xem docs/phases/P0/P0.5_plan.md.
"""

import contextlib
import json
import random
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import pymupdf

from dataminer.devtools import sample_book_content as content

PAGE_W, PAGE_H = 420.0, 595.0  # A5
MARGIN_X = 48.0
TOP = 62.0
BOTTOM = PAGE_H - 62.0
TEXT_W = PAGE_W - 2 * MARGIN_X
HEADER_Y = 40.0
FOOTER_Y = PAGE_H - 30.0
DPI = 110
FRONT_PAGES = 3  # bìa, trang trắng, mục lục - không đánh số

# Tên font khi nhúng → font Noto Sans của pymupdf-fonts (đủ glyph tiếng Việt).
FONT_FILES = {"reg": "notos", "bold": "notosbo", "ital": "notosit"}
_FONTS: dict[str, pymupdf.Font] = {}


def _font(key: str) -> pymupdf.Font:
    if key not in _FONTS:
        _FONTS[key] = pymupdf.Font(FONT_FILES[key])
    return _FONTS[key]


@dataclass(frozen=True)
class Style:
    size: float
    font: str = "reg"
    indent: float = 0.0
    before: float = 0.0
    after: float = 0.0
    align: str = "left"
    leading: float = 1.38


STYLES = {
    "chapter": Style(15, "bold", before=4, after=14, align="center"),
    "disease": Style(13.5, "bold", before=12, after=6),
    "section": Style(11.5, "bold", before=8, after=3),
    # Mục con cùng cỡ với thân bài, chỉ khác in đậm → sau OCR (mất đậm) chỉ còn số thứ tự.
    "sub": Style(10.5, "bold", before=5, after=2),
    "p": Style(10.5, after=4),
    "li": Style(10.5, indent=10, after=1.5),
    "caption": Style(9.5, "bold", before=6, after=4, align="center"),
    "table": Style(9.5, leading=1.7),
    "header": Style(8.5, "ital"),
    "footer": Style(9, align="center"),
    "toc_title": Style(14, "bold", before=10, after=16, align="center"),
    "toc_chapter": Style(10.5, "bold", before=6, after=2),
    "toc_disease": Style(10.5, indent=14, after=2),
    "cover_title": Style(22, "bold", before=150, after=10, align="center"),
    "cover_sub": Style(12, "ital", after=60, align="center"),
    "cover_note": Style(9.5, "bold", after=6, align="center"),
    "cover_pub": Style(10, before=120, align="center"),
}
HEADING_LEVEL = {
    "chapter": "chapter",
    "disease": "disease",
    "section": "section",
    "sub": "subsection",
}


@dataclass
class Line:
    """Một dòng (hoặc một ô bảng) đã dàn trang. `text` là bản sạch; `ocr` là bản lớp OCR."""

    x: float
    y: float  # baseline
    size: float
    font: str
    text: str
    role: str  # cover|toc|heading|body|caption|table|header|footer
    level: str | None = None
    section_type: str | None = None
    block: str | None = None  # các dòng cùng một đoạn/gạch đầu dòng có cùng block
    row: int | None = None
    col: int | None = None
    ocr: str = ""
    ocr_size: float = 0.0


@dataclass
class Page:
    lines: list[Line] = field(default_factory=list)
    rules: list[tuple[float, float, float, float]] = field(default_factory=list)  # kẻ bảng
    chapter_start: bool = False


def _wrap(text: str, size: float, font: str, first_w: float, rest_w: float) -> list[str]:
    f = _font(font)
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}" if current else word
        width = first_w if not lines else rest_w
        if current and f.text_length(trial, fontsize=size) > width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


class _Layout:
    def __init__(self) -> None:
        self.pages: list[Page] = [Page()]
        self.y = TOP
        self._blocks = 0

    @property
    def page(self) -> Page:
        return self.pages[-1]

    def new_page(self) -> None:
        self.pages.append(Page())
        self.y = TOP

    def _ensure(self, height: float) -> None:
        if self.y + height > BOTTOM:
            self.new_page()

    def _place(self, text: str, style: Style, x: float, role: str, **meta: Any) -> Line:
        line = Line(
            x=x,
            y=self.y + style.size,
            size=style.size,
            font=style.font,
            text=text,
            role=role,
            **meta,
        )
        self.page.lines.append(line)
        self.y += style.size * style.leading
        return line

    def block(
        self,
        kind: str,
        text: str,
        role: str,
        *,
        keep: float = 0.0,
        bullet: bool = False,
        **meta: Any,
    ) -> None:
        style = STYLES[kind]
        line_h = style.size * style.leading
        if self.page.lines:
            self.y += style.before
        self._ensure(line_h + keep)
        self._blocks += 1
        block_id = f"b{self._blocks:03d}"
        prefix = "- " if bullet else ""
        hang = _font(style.font).text_length(prefix, fontsize=style.size)
        avail = TEXT_W - style.indent
        wrapped = _wrap(prefix + text, style.size, style.font, avail, avail - hang)
        for i, part in enumerate(wrapped):
            self._ensure(line_h)
            x = MARGIN_X + style.indent + (hang if i else 0.0)
            if style.align == "center":
                x = (PAGE_W - _font(style.font).text_length(part, fontsize=style.size)) / 2
            self._place(part, style, x, role, block=block_id, **meta)
        self.y += style.after

    def table(self, caption: str, rows: list[list[str]]) -> None:
        cap, cell = STYLES["caption"], STYLES["table"]
        row_h = cell.size * cell.leading
        self._ensure(cap.size * cap.leading + cap.before + row_h * len(rows) + 8)
        self.block("caption", caption, "caption")
        cols = [0.0, 0.36, 0.62, 0.82]
        top = self.y
        for r, row in enumerate(rows):
            for c, text in enumerate(row):
                font = "bold" if r == 0 else "reg"
                line = Line(
                    x=MARGIN_X + 4 + cols[c] * TEXT_W,
                    y=self.y + cell.size,
                    size=cell.size,
                    font=font,
                    text=text,
                    role="table",
                    row=r,
                    col=c,
                )
                self.page.lines.append(line)
            self.y += row_h
        for k in range(len(rows) + 1):  # kẻ ngang
            y = top - 2 + k * row_h
            self.page.rules.append((MARGIN_X, y, MARGIN_X + TEXT_W, y))
        self.y += 6


def _layout_content() -> tuple[list[Page], list[dict[str, Any]]]:
    lay = _Layout()
    toc: list[dict[str, Any]] = []
    body_lh = STYLES["p"].size * STYLES["p"].leading
    for item in content.BOOK:
        kind = item[0]
        if kind == "chapter":
            if lay.page.lines:
                lay.new_page()
            lay.page.chapter_start = True
            toc.append({"title": item[2], "level": "chapter", "page_index": len(lay.pages) - 1})
            lay.block("chapter", item[1], "heading", level="chapter", keep=body_lh * 3)
        elif kind == "disease":
            lay.block("disease", item[1], "heading", level="disease", keep=body_lh * 4)
            toc.append({"title": item[2], "level": "disease", "page_index": len(lay.pages) - 1})
        elif kind in ("section", "sub"):
            lay.block(
                kind,
                item[1],
                "heading",
                level=HEADING_LEVEL[kind],
                section_type=item[2],
                keep=body_lh * 2,
            )
        elif kind == "p":
            lay.block("p", item[1], "body")
        elif kind == "ul":
            for text in item[1]:
                lay.block("li", text, "body", bullet=True)
        elif kind == "table":
            lay.table(item[1], item[2])
        else:  # pragma: no cover - lỗi dữ liệu nội dung
            raise ValueError(f"loại phần tử không hợp lệ: {kind}")
    return lay.pages, toc


def _centered(text: str, style: Style, y: float, role: str) -> Line:
    width = _font(style.font).text_length(text, fontsize=style.size)
    return Line(x=(PAGE_W - width) / 2, y=y, size=style.size, font=style.font, text=text, role=role)


def _front_matter(toc: list[dict[str, Any]]) -> list[Page]:
    cover = Page()
    y = TOP
    for kind, text in content.COVER:
        style = STYLES[kind]
        y += style.before + style.size
        cover.lines.append(_centered(text, style, y, "cover"))
        y += style.size * (style.leading - 1) + style.after

    toc_page = Page()
    title = STYLES["toc_title"]
    y = TOP + title.before + title.size
    toc_page.lines.append(_centered("MỤC LỤC", title, y, "heading"))
    toc_page.lines[-1].level = "toc_title"
    y += title.after
    for entry in toc:
        style = STYLES["toc_chapter" if entry["level"] == "chapter" else "toc_disease"]
        f = _font(style.font)
        page_txt = str(entry["printed_page"])
        avail = TEXT_W - style.indent
        used = f.text_length(f"{entry['title']}  {page_txt}", fontsize=style.size)
        dots = "." * max(3, int((avail - used) / f.text_length(".", fontsize=style.size)))
        y += style.before + style.size
        toc_page.lines.append(
            Line(
                x=MARGIN_X + style.indent,
                y=y,
                size=style.size,
                font=style.font,
                text=f"{entry['title']} {dots} {page_txt}",
                role="toc",
                level=entry["level"],
            )
        )
        y += style.size * (style.leading - 1) + style.after
    return [cover, Page(), toc_page]


def _add_running_heads(pages: list[Page], toc: list[dict[str, Any]]) -> None:
    chapters = [e for e in toc if e["level"] == "chapter"]
    for idx, page in enumerate(pages):
        printed = idx + 1
        if not page.chapter_start:
            current = [c for c in chapters if c["page_index"] <= idx][-1]["title"]
            text = content.RUNNING_TITLE if printed % 2 == 0 else current
            style = STYLES["header"]
            width = _font(style.font).text_length(text, fontsize=style.size)
            x = MARGIN_X if printed % 2 == 0 else PAGE_W - MARGIN_X - width
            page.lines.insert(
                0, Line(x=x, y=HEADER_Y, size=style.size, font=style.font, text=text, role="header")
            )
        page.lines.append(_centered(f"– {printed} –", STYLES["footer"], FOOTER_Y, "footer"))


# --------------------------------------------------------------------------- lỗi OCR

TONE_MARKS = ("̀", "́", "̃", "̉", "̣")
_WORD = re.compile(r"^(\W*)(\w+)(\W*)$")


def _strip_diacritics(word: str) -> str:
    nfd = unicodedata.normalize("NFD", word)
    plain = "".join(c for c in nfd if not unicodedata.combining(c))
    return plain.replace("đ", "d").replace("Đ", "D")


def _swap_tone(word: str, rng: random.Random) -> str | None:
    """Đổi dấu thanh: "đặc" → "đắc". Dấu mới đặt SAU các dấu mũ/trăng/móc của cùng nguyên âm,
    nếu không NFC không ghép được và sinh ký tự lạ ("đá̆c")."""
    nfd = unicodedata.normalize("NFD", word)
    for i, ch in enumerate(nfd):
        if ch in TONE_MARKS:
            new = rng.choice([t for t in TONE_MARKS if t != ch])
            rest = nfd[:i] + nfd[i + 1 :]
            end = i
            while end < len(rest) and unicodedata.combining(rest[end]):
                end += 1
            return unicodedata.normalize("NFC", rest[:end] + new + rest[end:])
    return None


def _confuse_chars(word: str) -> str | None:
    if "m" in word:
        return word.replace("m", "rn", 1)
    if "l" in word:
        return word.replace("l", "1", 1)
    if "h" in word:
        return word.replace("h", "b", 1)
    return None


def _letters(token: str) -> str | None:
    match = _WORD.match(token)
    if match and match.group(2).isalpha():
        return match.group(2)
    return None


def _corrupt(text: str, kind: str, rng: random.Random) -> tuple[str, str, str] | None:
    """Áp một lỗi OCR lên `text`. Trả (text_mới, nguyên_bản, bản_lỗi), hoặc None nếu không áp
    được."""
    tokens = text.split(" ")
    idxs = [i for i, t in enumerate(tokens) if _letters(t)]
    rng.shuffle(idxs)
    if kind == "merge_words":
        # Chỉ dính hai từ liền nhau khi từ trước không kết thúc bằng dấu câu.
        pairs = [
            i
            for i in idxs
            if i + 1 < len(tokens) and _letters(tokens[i + 1]) and tokens[i][-1].isalnum()
        ]
        if not pairs:
            return None
        i = pairs[0]
        original = f"{tokens[i]} {tokens[i + 1]}"
        merged = tokens[i] + tokens[i + 1]
        return " ".join([*tokens[:i], merged, *tokens[i + 2 :]]), original, merged
    for i in idxs:
        word = _letters(tokens[i])
        assert word is not None
        if kind == "drop_diacritics":
            new = _strip_diacritics(word)
        elif kind == "wrong_tone":
            new = _swap_tone(word, rng) or word
        elif kind == "char_confusion":
            new = _confuse_chars(word) or word
        else:  # pragma: no cover
            raise ValueError(kind)
        if new != word:
            tokens[i] = tokens[i].replace(word, new, 1)
            return " ".join(tokens), word, new
    return None


RANDOM_KINDS = (
    ("drop_diacritics", 0.35),
    ("wrong_tone", 0.2),
    ("char_confusion", 0.2),
    ("merge_words", 0.25),
)
# Lỗi số liệu cố ý (nguy hiểm nhất trong sách y khoa) - P1 phải bắt được.
# (mẫu, chuỗi_cũ, chuỗi_mới, khớp_nguyên_ô): ô bảng "1 g" phải khớp đúng cả ô,
# nếu không sẽ trúng nhầm "trên 1 giờ".
FORCED_DIGIT_ERRORS = (
    ("Paracetamol 500 mg", "500", "5OO", False),
    ("1 g", "1", "l", True),
)


def _apply_ocr_errors(pages: list[Page], rng: random.Random, rate: float) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for line in (ln for p in pages for ln in p.lines):
        line.ocr = line.text
        line.ocr_size = round(line.size * rng.uniform(0.94, 1.06), 1)

    def record(page_no: int, line: Line, kind: str, original: str, corrupted: str) -> None:
        errors.append(
            {
                "pdf_page": page_no,
                "kind": kind,
                "original": original,
                "corrupted": corrupted,
                "line_clean": line.text,
            }
        )

    eligible: list[tuple[int, Line]] = [
        (n, ln)
        for n, p in enumerate(pages, start=1)
        for ln in p.lines
        if ln.role in ("body", "heading", "table", "toc", "caption")
    ]

    # Lỗi số liệu cài TRƯỚC và khóa dòng đó: nếu cài sau, lỗi ngẫu nhiên có thể đã sửa mất
    # chữ mốc ("Paracetamol"); nếu không khóa, lỗi ngẫu nhiên có thể "sửa ngược" ("l g" → "1 g").
    protected: set[int] = set()
    for anchor, old, new, whole_cell in FORCED_DIGIT_ERRORS:
        for page_no, line in eligible:
            hit = line.ocr == anchor if whole_cell else anchor in line.ocr
            if hit:
                fixed = anchor.replace(old, new, 1)
                line.ocr = line.ocr.replace(anchor, fixed, 1)
                record(page_no, line, "digit_confusion", anchor, fixed)
                protected.add(id(line))
                break
        else:  # pragma: no cover - nội dung sách đổi mà quên cập nhật mẫu
            raise ValueError(f"không tìm thấy '{anchor}' để cài lỗi số liệu")
    eligible = [(n, ln) for n, ln in eligible if id(ln) not in protected]

    kinds = [kind for kind, _ in RANDOM_KINDS]
    weights = [weight for _, weight in RANDOM_KINDS]
    for page_no, line in eligible:
        is_heading = line.role == "heading"
        if rng.random() >= (0.15 if is_heading else rate):
            continue
        kind = "drop_diacritics" if is_heading else rng.choices(kinds, weights)[0]
        result = _corrupt(line.ocr, kind, rng)
        if result:
            line.ocr = result[0]
            record(page_no, line, kind, result[1], result[2])

    # Bảo đảm mỗi loại lỗi xuất hiện ít nhất một lần.
    body = [(n, ln) for n, ln in eligible if ln.role == "body"]
    for kind, _ in RANDOM_KINDS:
        if not any(e["kind"] == kind for e in errors):
            for page_no, line in rng.sample(body, len(body)):
                result = _corrupt(line.ocr, kind, rng)
                if result:
                    line.ocr = result[0]
                    record(page_no, line, kind, result[1], result[2])
                    break

    # Một vài dòng bị mã hóa Unicode tổ hợp (NFD) - lỗi mã hóa, chữ vẫn đúng.
    candidates = [(n, ln) for n, ln in body if not unicodedata.is_normalized("NFD", ln.ocr)]
    for page_no, line in rng.sample(candidates, 2):
        line.ocr = unicodedata.normalize("NFD", line.ocr)
        record(page_no, line, "nfd_line", line.text, "(cả dòng ở dạng NFD)")
    return errors


# --------------------------------------------------------------------------- vẽ PDF


def _embed_fonts(page: pymupdf.Page, keys: tuple[str, ...]) -> None:
    for key in keys:
        page.insert_font(fontname=key, fontbuffer=_font(key).buffer)


def _scan_image(page: Page, rng: random.Random) -> bytes:
    """Dàn trang sạch → ảnh xám có màu giấy + nhiễu lấm tấm, nén JPEG (giống bản scan)."""
    tmp = pymupdf.open()
    pg = tmp.new_page(width=PAGE_W, height=PAGE_H)
    _embed_fonts(pg, tuple(FONT_FILES))
    for ln in page.lines:
        pg.insert_text((ln.x, ln.y), ln.text, fontsize=ln.size, fontname=ln.font)
    for x0, y0, x1, y1 in page.rules:
        pg.draw_line((x0, y0), (x1, y1), width=0.6)
    pix = pg.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY)
    tone = bytes(int(22 + v * 0.86) for v in range(256))  # giấy hơi xám, mực không đen tuyệt đối
    samples = bytearray(pix.samples.translate(tone))
    for _ in range(700):
        samples[rng.randrange(len(samples))] = rng.randrange(60, 160)
    noisy = pymupdf.Pixmap(pymupdf.csGRAY, pix.width, pix.height, bytes(samples), False)
    data: bytes = noisy.tobytes("jpg", jpg_quality=55)
    tmp.close()
    return data


@dataclass
class SampleBook:
    pdf_path: Path
    truth_path: Path
    truth: dict[str, Any]


def make_sample_book(
    out_dir: Path, *, name: str = "book01", seed: int = 7, error_rate: float = 0.35
) -> SampleBook:
    """Sinh `<name>.pdf` + `<name>.truth.json` vào `out_dir`."""
    rng = random.Random(seed)
    body_pages, toc = _layout_content()
    for entry in toc:
        entry["printed_page"] = entry["page_index"] + 1
    _add_running_heads(body_pages, toc)
    pages = [*_front_matter(toc), *body_pages]
    errors = _apply_ocr_errors(pages, rng, error_rate)

    doc = pymupdf.open()
    doc.set_metadata(
        {
            "title": f"{content.TITLE} (sách mẫu tổng hợp)",
            "creator": "dataminer.devtools.sample_book",
            "producer": "dataminer",
        }
    )
    for page in pages:
        pg = doc.new_page(width=PAGE_W, height=PAGE_H)
        pg.insert_image(pg.rect, stream=_scan_image(page, rng))
        if page.lines:
            _embed_fonts(pg, ("reg",))
            for ln in page.lines:
                pg.insert_text(
                    (ln.x, ln.y), ln.ocr, fontsize=ln.ocr_size, fontname="reg", render_mode=3
                )
    with contextlib.suppress(Exception):  # thiếu fonttools: chỉ làm file lớn hơn
        doc.subset_fonts()
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{name}.pdf"
    doc.save(pdf_path, garbage=4, deflate=True)
    doc.close()

    truth = _truth(pages, toc, errors, seed)
    truth_path = out_dir / f"{name}.truth.json"
    truth_path.write_text(json.dumps(truth, ensure_ascii=False, indent=1), encoding="utf-8")
    return SampleBook(pdf_path, truth_path, truth)


def _truth(
    pages: list[Page], toc: list[dict[str, Any]], errors: list[dict[str, Any]], seed: int
) -> dict[str, Any]:
    out_pages, lines, headings, tables = [], [], [], []
    for n, page in enumerate(pages, start=1):
        printed = n - FRONT_PAGES if n > FRONT_PAGES else None
        heads = [ln for ln in page.lines if ln.role == "header"]
        foots = [ln for ln in page.lines if ln.role == "footer"]
        out_pages.append(
            {
                "pdf_page": n,
                "printed_page": printed,
                "has_text": bool(page.lines),
                "header": heads[0].ocr if heads else None,
                "footer": foots[0].ocr if foots else None,
                "chapter_start": page.chapter_start,
            }
        )
        for ln in page.lines:
            item = {k: v for k, v in asdict(ln).items() if v is not None}
            item["pdf_page"] = n
            lines.append(item)
            if ln.role == "heading":
                headings.append(
                    {
                        "pdf_page": n,
                        "text": ln.text,
                        "ocr": ln.ocr,
                        "level": ln.level,
                        "section_type": ln.section_type,
                        "size": ln.size,
                    }
                )
        cells = [ln for ln in page.lines if ln.role == "table"]
        if cells:
            n_rows = max(c.row or 0 for c in cells) + 1
            grid = [[c.text for c in cells if c.row == r] for r in range(n_rows)]
            caption = next(ln.text for ln in page.lines if ln.role == "caption")
            tables.append({"pdf_page": n, "caption": caption, "rows": grid})
    return {
        "generator": "dataminer.devtools.sample_book",
        "seed": seed,
        "front_pages": FRONT_PAGES,
        "page_size": [PAGE_W, PAGE_H],
        "body_size": STYLES["p"].size,
        "pages": out_pages,
        "toc": [
            {
                "title": e["title"],
                "level": e["level"],
                "printed_page": e["printed_page"],
                "pdf_page": e["page_index"] + 1 + FRONT_PAGES,
            }
            for e in toc
        ],
        "headings": headings,
        "tables": tables,
        "ocr_errors": errors,
        "lines": lines,
    }
