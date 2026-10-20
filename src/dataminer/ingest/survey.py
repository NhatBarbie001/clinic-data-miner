"""P0.5 - Khảo sát sách PDF: thống kê, dòng text, header/footer, ứng viên tiêu đề, dấu hiệu lỗi OCR.

Không gọi LLM, không sửa dữ liệu - chỉ đo đạc để thiết kế P1/P2 dựa trên dữ liệu thật.
Trích dòng dùng `pdf_reader.read_lines` (P1.1).
"""

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pymupdf
from pydantic import BaseModel

from dataminer.core.io import write_json, write_jsonl
from dataminer.core.text_vi import has_vietnamese_marks, is_nfc, is_valid_syllable, nfc
from dataminer.ingest.blocks import heading_signals
from dataminer.ingest.page_furniture import classify_furniture, furniture_key
from dataminer.ingest.pdf_reader import Line, body_font_size, read_lines

RE_CHAPTER = re.compile(r"^(CHƯƠNG|Chương|PHẦN|Phần|BÀI|Bài)\s+([\dIVXLC]+)\b")
RE_SUB = re.compile(r"^\d{1,2}\.\d{1,2}\.?\s+\S")
RE_SECTION = re.compile(r"^\d{1,2}\.\s+\S")
RE_TOC_ENTRY = re.compile(r"(\.{4,}|…{2,})\s*\d+\s*$")
RE_LETTERS = re.compile(r"[^\W\d_]+")
RE_DIGIT_LOOKALIKE = re.compile(r"\d[OoIl]|[OoIl]\d")  # 5OO, 1O, l0...
RE_DIGIT_IN_WORD = re.compile(r"\d[a-zà-ỹđ]|[a-zà-ỹđ]\d")  # 1à, khớ1 (chữ thường sát chữ số)
# Thiếu khoảng trắng quanh dấu câu: "ngày(Bảng", "đau,sưng" - văn bản in chuẩn không có.
RE_MISSING_SPACE = re.compile(r"[^\W\d_][(\[]|[,;:)\]][^\W\d_]")
UNITS = {"g", "mg", "mcg", "µg", "ml", "l", "ui", "iu"}


# Trích dòng đã chuyển sang P1.1 (`pdf_reader`); giữ tên cũ để code/test P0.5 không đổi.
SurveyLine = Line


def extract_lines(doc: pymupdf.Document, book_id: str = "book") -> list[Line]:
    return read_lines(doc, book_id=book_id)


def compute_stats(doc: pymupdf.Document, lines: list[SurveyLine]) -> dict[str, Any]:
    by_page: dict[int, int] = defaultdict(int)
    fonts: Counter[str] = Counter()
    sizes: Counter[float] = Counter()
    for ln in lines:
        by_page[ln.page] += len(ln.text)
        fonts[ln.font] += len(ln.text)
        sizes[round(ln.size * 2) / 2] += len(ln.text)
    n_chars = sum(by_page.values()) or 1
    bold_chars = sum(len(ln.text) for ln in lines if ln.bold)
    nfd_lines = [ln for ln in lines if not is_nfc(ln.text_raw)]
    return {
        "pages": doc.page_count,
        "pages_with_text": len(by_page),
        "pages_without_text": [p for p in range(1, doc.page_count + 1) if p not in by_page],
        "pages_with_images": [p for p in range(1, doc.page_count + 1) if doc[p - 1].get_images()],
        "chars_per_page": {str(p): by_page.get(p, 0) for p in range(1, doc.page_count + 1)},
        "lines": len(lines),
        "fonts": dict(fonts.most_common()),
        "size_histogram": {str(k): v for k, v in sorted(sizes.items())},
        "body_font_size": body_font_size(lines),
        "bold_char_ratio": round(bold_chars / n_chars, 4),
        "nfd_lines": len(nfd_lines),
        "page_size": [round(doc[0].rect.width, 1), round(doc[0].rect.height, 1)],
    }


def find_header_footer(lines: list[SurveyLine], body_size: float) -> dict[str, Any]:
    """Header/footer cho báo cáo khảo sát - logic nằm ở `page_furniture` (P1.2)."""
    _, removed = classify_furniture(lines, body_size)
    patterns: dict[tuple[str, str], dict[str, Any]] = {}
    instances = []
    for item in removed:
        instances.append(
            {
                "page": item.page,
                "index": item.index,
                "zone": item.zone,
                "text": item.text,
                "kind": item.kind,
                "confidence": item.confidence,
                "printed_page": item.printed_page,
            }
        )
        key = (item.zone, furniture_key(item.text))
        pat = patterns.setdefault(
            key,
            {
                "zone": item.zone,
                "pattern": key[1],
                "kind": item.kind,
                "confidence": item.confidence,
                "pages": [],
                "example": item.text,
            },
        )
        pat["pages"].append(item.page)
    return {"patterns": list(patterns.values()), "instances": instances}


def find_heading_candidates(lines: list[SurveyLine], body_size: float) -> dict[str, Any]:
    candidates, toc_entries = [], []
    for ln in lines:
        if ln.zone != "body":
            continue
        text = nfc(ln.text)
        if RE_TOC_ENTRY.search(text):
            toc_entries.append({"page": ln.page, "index": ln.index, "text": ln.text})
            continue
        reasons, level = heading_signals(text, ln.size, body_size, ln.bold)
        if reasons:
            candidates.append(
                {
                    "page": ln.page,
                    "index": ln.index,
                    "text": ln.text,
                    "size": ln.size,
                    "level_guess": level,
                    "reasons": reasons,
                }
            )
    return {"candidates": candidates, "toc_entries": toc_entries}


def find_ocr_signals(lines: list[SurveyLine]) -> list[dict[str, Any]]:
    """Dấu hiệu lỗi OCR phát hiện được KHÔNG cần từ điển. Lỗi mất dấu/sai dấu tạo ra từ
    hợp lệ (vd. "khop", "đáu") không bắt được ở đây - việc của P1."""
    signals: list[dict[str, Any]] = []

    def add(ln: SurveyLine, kind: str, token: str, detail: str) -> None:
        signals.append(
            {
                "page": ln.page,
                "index": ln.index,
                "kind": kind,
                "token": token,
                "detail": detail,
                "line": ln.text,
            }
        )

    for ln in lines:
        if not is_nfc(ln.text_raw):
            add(ln, "nfd_line", "", "dòng mã hóa Unicode tổ hợp (NFD) - cần chuẩn hóa NFC")
        text = nfc(ln.text)
        tokens = text.split()
        for i, tok in enumerate(tokens):
            core = tok.strip(".,;:!?()[]\"'“”-–")
            if RE_DIGIT_LOOKALIKE.search(core) and any(c.isdigit() for c in core):
                add(ln, "digit_lookalike", core, "chữ O/I/l lẫn trong số (vd. 5OO)")
            elif core in ("l", "I", "O") and i + 1 < len(tokens) and tokens[i + 1].lower() in UNITS:
                add(
                    ln,
                    "digit_lookalike",
                    f"{core} {tokens[i + 1]}",
                    "chữ cái đứng thay số trước đơn vị",
                )
            elif RE_DIGIT_IN_WORD.search(core.lower()) and not core.isupper():
                add(ln, "digit_in_word", core, "chữ số dính trong từ (vd. 1à)")
            if RE_MISSING_SPACE.search(tok):
                add(ln, "missing_space", tok, "thiếu khoảng trắng quanh dấu câu (dính từ?)")
        for word in RE_LETTERS.findall(text):
            if has_vietnamese_marks(word) and not is_valid_syllable(word):
                add(
                    ln,
                    "invalid_syllable",
                    word,
                    "không phải âm tiết tiếng Việt hợp lệ (nhầm ký tự hoặc dính từ)",
                )
    return signals


def _pick_sample_pages(
    stats: dict[str, Any],
    headings: dict[str, Any],
    signals: list[dict[str, Any]],
    lines: list[SurveyLine],
) -> dict[str, int]:
    picks: dict[str, int] = {}
    if headings["toc_entries"]:
        picks["muc_luc"] = headings["toc_entries"][0]["page"]
    chapters = [c for c in headings["candidates"] if c["level_guess"] == "chapter"]
    if chapters:
        picks["dau_chuong"] = chapters[0]["page"]
    rows: Counter[tuple[int, int]] = Counter(
        (ln.page, round((ln.bbox[1] + ln.bbox[3]) / 4)) for ln in lines if ln.zone == "body"
    )
    table_pages = Counter(page for (page, _), n in rows.items() if n >= 3)
    if table_pages:
        picks["co_bang"] = table_pages.most_common(1)[0][0]
    if signals:
        picks["nhieu_loi_ocr"] = Counter(s["page"] for s in signals).most_common(1)[0][0]
    return picks


def _page_detail(page: pymupdf.Page) -> dict[str, Any]:
    spans = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for s in line["spans"]:
                if s["text"].strip():
                    spans.append(
                        {
                            "text": s["text"],
                            "bbox": [round(v, 1) for v in s["bbox"]],
                            "size": round(s["size"], 2),
                            "font": s["font"],
                            "flags": s["flags"],
                        }
                    )
    return {
        "page": page.number + 1,
        "size": [page.rect.width, page.rect.height],
        "images": len(page.get_images()),
        "spans": spans,
    }


class SurveyResult(BaseModel):
    stats: dict[str, Any]
    header_footer: dict[str, Any]
    headings: dict[str, Any]
    signals: list[dict[str, Any]]
    sample_pages: dict[str, int]


def survey_pdf(
    pdf_path: Path, out_dir: Path, *, book_id: str = "book", render_dpi: int = 90
) -> SurveyResult:
    """Khảo sát `pdf_path`, ghi kết quả vào `out_dir`."""
    doc = pymupdf.open(pdf_path)
    lines = extract_lines(doc, book_id)
    stats = compute_stats(doc, lines)
    body = stats["body_font_size"]
    hf = find_header_footer(lines, body)
    headings = find_heading_candidates(lines, body)
    signals = find_ocr_signals(lines)
    picks = _pick_sample_pages(stats, headings, signals, lines)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "stats.json", stats)
    write_jsonl(out_dir / "lines.jsonl", lines)
    write_json(out_dir / "header_footer.json", hf)
    write_json(out_dir / "heading_candidates.json", headings)
    write_json(out_dir / "ocr_signals.json", signals)
    pages_dir = out_dir / "pages"
    pages_dir.mkdir(exist_ok=True)
    for label, page_no in picks.items():
        page = doc[page_no - 1]
        write_json(pages_dir / f"page_{page_no:03d}.json", {"label": label, **_page_detail(page)})
        page.get_pixmap(dpi=render_dpi).save(pages_dir / f"page_{page_no:03d}.png")
    doc.close()

    result = SurveyResult(
        stats=stats, header_footer=hf, headings=headings, signals=signals, sample_pages=picks
    )
    (out_dir / "survey_report.md").write_text(render_report(pdf_path, result), encoding="utf-8")
    return result


def render_report(pdf_path: Path, r: SurveyResult) -> str:
    s = r.stats
    kinds = Counter(sig["kind"] for sig in r.signals)
    levels = Counter(c["level_guess"] for c in r.headings["candidates"])
    out = [
        f"# Báo cáo khảo sát: `{pdf_path.name}`",
        "",
        "## Tổng quan",
        f"- Số trang: **{s['pages']}** (khổ {s['page_size'][0]}×{s['page_size'][1]} pt); "
        f"có text: {s['pages_with_text']}; có ảnh: {len(s['pages_with_images'])}",
        f"- Trang KHÔNG có text: {s['pages_without_text'] or 'không có'}",
        f"- Số dòng: {s['lines']}; font: {', '.join(s['fonts'])}",
        f"- Cỡ chữ thân bài ước lượng: **{s['body_font_size']} pt**",
        f"- Tỉ lệ ký tự in đậm: {s['bold_char_ratio']:.1%}"
        + ("  → ⚠️ lớp OCR **không giữ thông tin in đậm**" if s["bold_char_ratio"] < 0.01 else ""),
        f"- Dòng mã hóa NFD: {s['nfd_lines']}",
        "",
        "## Phân bố cỡ chữ (số ký tự)",
        "",
        "| cỡ (pt) | ký tự |",
        "|---|---|",
        *[f"| {k} | {v} |" for k, v in s["size_histogram"].items()],
        "",
        "## Header / footer",
        "",
        "| vùng | mẫu | loại | độ tin cậy | trang |",
        "|---|---|---|---|---|",
        *[
            f"| {p['zone']} | `{p['example']}` | {p['kind']} | {p['confidence']} | "
            f"{', '.join(map(str, p['pages']))} |"
            for p in r.header_footer["patterns"]
        ],
        "",
        f"## Ứng viên tiêu đề ({len(r.headings['candidates'])})",
        f"Theo cấp đoán: {dict(levels)}. Dòng mục lục (bỏ qua): {len(r.headings['toc_entries'])}.",
        "",
        "| trang | text | cấp đoán | lý do |",
        "|---|---|---|---|",
        *[
            f"| {c['page']} | {c['text']} | {c['level_guess']} | {'; '.join(c['reasons'])} |"
            for c in r.headings["candidates"]
        ],
        "",
        f"## Dấu hiệu lỗi OCR ({len(r.signals)})",
        f"Theo loại: {dict(kinds)}",
        "",
        "| trang | loại | token | dòng |",
        "|---|---|---|---|",
        *[f"| {g['page']} | {g['kind']} | `{g['token']}` | {nfc(g['line'])} |" for g in r.signals],
        "",
        "## Trang mẫu đã trích (`pages/`)",
        *[f"- {label}: trang {page}" for label, page in r.sample_pages.items()],
        "",
    ]
    return "\n".join(out)
