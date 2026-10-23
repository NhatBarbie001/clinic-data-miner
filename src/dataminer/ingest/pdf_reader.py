"""P1.1 - Đọc lớp text của PDF thành các dòng (`Line`) đúng thứ tự đọc, đã chuẩn hóa NFC.

Thứ tự đọc: gom các dòng có cùng dải dọc thành "hàng" rồi sắp trái → phải, nên các ô bảng
cùng hàng nằm liền nhau; không phụ thuộc thứ tự block mà PyMuPDF trả về.
Xem docs/phases/P1/P1.1_plan.md.
"""

import logging
from pathlib import Path
from typing import Any

import pymupdf

from dataminer.core.schemas import stable_id
from dataminer.core.text_vi import is_nfc, nfc
from dataminer.model.line import Line, Zone

log = logging.getLogger("dataminer.ingest")

TOP_ZONE = 0.09  # dòng nằm hoàn toàn trong 9% đầu trang → vùng header
BOTTOM_ZONE = 0.09  # dòng nằm hoàn toàn trong 9% cuối trang → vùng footer
ROW_TOLERANCE = 0.4  # hai dòng cùng hàng nếu tâm dọc lệch < 0.4 × cỡ chữ


def _raw_lines(page: pymupdf.Page) -> list[dict[str, Any]]:
    """Các dòng của một trang (chưa sắp thứ tự): text, bbox, cỡ chữ, font, đậm."""
    out = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for raw in block["lines"]:
            spans = [s for s in raw["spans"] if s["text"].strip()]
            if not spans:
                continue
            chars = sum(len(s["text"]) for s in spans)
            out.append(
                {
                    "text_raw": "".join(s["text"] for s in raw["spans"]).strip(),
                    "bbox": tuple(round(v, 1) for v in raw["bbox"]),
                    "size": round(sum(s["size"] * len(s["text"]) for s in spans) / chars, 2),
                    "font": spans[0]["font"],
                    "bold": any(s["flags"] & 16 or "bold" in s["font"].lower() for s in spans),
                }
            )
    return out


def reading_order(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Gom thành hàng theo tâm dọc (dung sai theo cỡ chữ), mỗi hàng sắp trái → phải."""
    by_center = sorted(items, key=lambda it: (it["bbox"][1] + it["bbox"][3]) / 2)
    rows: list[list[dict[str, Any]]] = []
    for item in by_center:
        center = (item["bbox"][1] + item["bbox"][3]) / 2
        if rows:
            first = rows[-1][0]
            first_center = (first["bbox"][1] + first["bbox"][3]) / 2
            tolerance = ROW_TOLERANCE * min(first["size"], item["size"])
            if center - first_center < tolerance:
                rows[-1].append(item)
                continue
        rows.append([item])
    return [it for row in rows for it in sorted(row, key=lambda it: it["bbox"][0])]


def detect_columns(lines: list[Line]) -> bool:
    """Trang có vẻ dàn 2 cột? (chưa xử lý ở P1 - chỉ cảnh báo).

    Một cột: phần lớn dòng thân bài vắt qua giữa trang. Hai cột: rất ít dòng vắt qua giữa,
    và mỗi nửa trang có ≥ 30% số dòng.
    """
    body = [ln for ln in lines if ln.zone == "body"]
    if len(body) < 6 or not body[0].page_width:
        return False
    mid = body[0].page_width / 2
    left = sum(ln.bbox[2] < mid for ln in body)
    right = sum(ln.bbox[0] > mid for ln in body)
    crossing = len(body) - left - right
    return crossing <= 0.1 * len(body) and left >= 0.3 * len(body) and right >= 0.3 * len(body)


def body_font_size(lines: list[Line]) -> float:
    """Cỡ chữ thân bài = trung vị cỡ chữ theo số ký tự của các dòng vùng thân trang."""
    weighted = sorted((ln.size, len(ln.text)) for ln in lines if ln.zone == "body")
    total = sum(w for _, w in weighted)
    acc = 0
    for size, weight in weighted:
        acc += weight
        if acc * 2 >= total:
            return round(size, 1)
    return 0.0


def read_lines(
    source: Path | pymupdf.Document,
    *,
    book_id: str = "book",
    pages: tuple[int, int] | None = None,
    top_zone: float = TOP_ZONE,
    bottom_zone: float = BOTTOM_ZONE,
) -> list[Line]:
    """Đọc mọi dòng text (hoặc chỉ các trang trong `pages`, tính cả hai đầu).

    `top_zone`/`bottom_zone`: tỉ lệ chiều cao trang coi là lề trên/dưới (cấu hình p1.furniture).
    """
    doc = pymupdf.open(source) if isinstance(source, Path) else source
    lines: list[Line] = []
    try:
        for page_no in range(1, doc.page_count + 1):
            if pages and not pages[0] <= page_no <= pages[1]:
                continue
            page = doc[page_no - 1]
            width, height = page.rect.width, page.rect.height
            page_lines: list[Line] = []
            for index, item in enumerate(reading_order(_raw_lines(page))):
                raw = item["text_raw"]
                x0, y0, x1, y1 = item["bbox"]
                zone: Zone = "body"
                if y1 < height * top_zone:
                    zone = "top"
                elif y0 > height * (1 - bottom_zone):
                    zone = "bottom"
                page_lines.append(
                    Line(
                        id=stable_id(book_id, page_no, index, prefix="ln"),
                        page=page_no,
                        index=index,
                        text=nfc(" ".join(raw.split())),
                        text_raw=raw,
                        bbox=(x0, y0, x1, y1),
                        size=item["size"],
                        font=item["font"],
                        bold=item["bold"],
                        zone=zone,
                        page_width=round(width, 1),
                        page_height=round(height, 1),
                        flags=[] if is_nfc(raw) else ["nfd_fixed"],
                    )
                )
            if detect_columns(page_lines):
                log.warning("trang %d có thể dàn 2 cột - thứ tự đọc có thể sai", page_no)
                for ln in page_lines:
                    ln.flags.append("possible_two_columns")
            lines.extend(page_lines)
    finally:
        if isinstance(source, Path):
            doc.close()
    return lines
