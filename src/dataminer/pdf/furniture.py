"""P1.2 - "Đồ đạc trang": header chạy, footer, số trang. Tách khỏi nội dung + ánh xạ số trang in.

Đồ đạc trang bị loại khỏi nội dung nhưng KHÔNG mất: ghi lại trong `removed` để truy vết.
Logic nhận diện đã kiểm chứng ở P0.5 (recall/precision 100% trên 24 sách mẫu).
Xem docs/phases/P1/P1.2_plan.md.
"""

import re
from collections import Counter, defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from dataminer.core.config import FurnitureCfg
from dataminer.core.io import write_json
from dataminer.core.text_vi import nfc
from dataminer.model.line import Line

# Chỉ gồm số trang và dấu: "12", "- 12 -", "– 12 –", "[12]"; có thể có chữ "Trang" phía trước.
RE_PAGE_NUMBER = re.compile(r"^(?:trang\s*)?[^\w]*(\d{1,4})[^\w]*$", re.IGNORECASE)


def page_number_of(text: str) -> int | None:
    """Số trang in nếu dòng chỉ là số trang, ngược lại None."""
    match = RE_PAGE_NUMBER.match(nfc(text).strip())
    return int(match.group(1)) if match else None


def furniture_key(text: str) -> str:
    """Khóa so sánh header/footer giữa các trang: chữ thường, gộp khoảng trắng, mọi số → #."""
    return re.sub(r"\d+", "#", " ".join(nfc(text).casefold().split()))


class FurnitureItem(BaseModel):
    line_id: str
    page: int
    index: int
    zone: Literal["top", "bottom"]
    text: str
    kind: Literal["page_number", "running_head"]
    confidence: Literal["high", "medium"]
    reason: str
    printed_page: int | None = None


class PageInfo(BaseModel):
    page: int  # số trang PDF
    printed_page: int | None
    source: Literal["page_number", "inferred", "none"]
    flags: list[str] = Field(default_factory=list)


class FurnitureResult(BaseModel):
    content: list[Line]
    removed: list[FurnitureItem]
    pages: list[PageInfo]
    warnings: list[str] = Field(default_factory=list)

    def printed(self, page: int) -> int | None:
        return next((p.printed_page for p in self.pages if p.page == page), None)


def classify_furniture(
    lines: list[Line],
    body_size: float,
    cfg: FurnitureCfg | None = None,
    page_number: Callable[[str], int | None] = page_number_of,
) -> tuple[list[Line], list[FurnitureItem]]:
    """Tách (nội dung, đồ đạc trang). Một dòng ở lề là đồ đạc nếu: là số trang, HOẶC lặp lại
    ở ≥ min_repeat_pages trang, HOẶC chữ nhỏ hơn thân bài. Dòng ở lề cỡ thường, không lặp
    (vd. dòng cuối đoạn văn chạm lề) được GIỮ."""
    cfg = cfg or FurnitureCfg()
    pages_by_key: dict[tuple[str, str], set[int]] = defaultdict(set)
    for ln in lines:
        if ln.zone != "body":
            pages_by_key[(ln.zone, furniture_key(ln.text))].add(ln.page)

    content: list[Line] = []
    removed: list[FurnitureItem] = []
    for ln in lines:
        if ln.zone == "body":
            content.append(ln)
            continue
        number = page_number(ln.text)
        repeats = len(pages_by_key[(ln.zone, furniture_key(ln.text))])
        small = ln.size <= body_size * cfg.small_ratio
        kind: Literal["page_number", "running_head"]
        confidence: Literal["high", "medium"]
        if number is not None:
            kind, confidence, reason = "page_number", "high", "chỉ gồm số trang"
        elif repeats >= cfg.min_repeat_pages:
            kind, confidence, reason = "running_head", "high", f"lặp lại ở {repeats} trang"
        elif small:
            kind, confidence = "running_head", "medium"
            reason = f"chữ nhỏ ({ln.size:.1f} ≤ {cfg.small_ratio:.0%} thân bài) nằm ở lề"
        else:
            content.append(ln)  # cỡ thường, không lặp → nội dung chạm lề
            continue
        removed.append(
            FurnitureItem(
                line_id=ln.id,
                page=ln.page,
                index=ln.index,
                zone=ln.zone,
                text=ln.text,
                kind=kind,
                confidence=confidence,
                reason=reason,
                printed_page=number,
            )
        )
    return content, removed


def map_printed_pages(
    pdf_pages: list[int], removed: list[FurnitureItem]
) -> tuple[list[PageInfo], list[str]]:
    """Ánh xạ trang PDF → số trang in.

    Độ lệch (số in - số PDF) phổ biến nhất được coi là đúng. Trang có số mâu thuẫn với độ lệch
    đó (OCR đọc nhầm) → dùng số suy ra + cảnh báo. Trang thiếu số nằm SAU trang có số đầu tiên
    → suy ra từ độ lệch. Trang trước đó (bìa, mục lục) → None.
    """
    observed: dict[int, int] = {}
    for item in removed:
        if item.kind == "page_number" and item.printed_page is not None:
            observed.setdefault(item.page, item.printed_page)
    warnings: list[str] = []
    if not observed:
        warnings.append("Không tìm thấy số trang in nào - mọi trang để printed_page = None.")
        return [PageInfo(page=p, printed_page=None, source="none") for p in pdf_pages], warnings

    offset, votes = Counter(n - p for p, n in observed.items()).most_common(1)[0]
    if votes < len(observed):
        others = sorted({n - p for p, n in observed.items()} - {offset})
        warnings.append(
            f"Độ lệch số trang không nhất quán: dùng {offset:+d} ({votes}/{len(observed)} trang), "
            f"lệch khác: {others}."
        )
    first = min(observed)
    infos: list[PageInfo] = []
    for page in pdf_pages:
        if page < first:
            infos.append(PageInfo(page=page, printed_page=None, source="none"))
        elif page in observed and observed[page] == page + offset:
            infos.append(PageInfo(page=page, printed_page=observed[page], source="page_number"))
        elif page in observed:
            warnings.append(
                f"Trang PDF {page}: số trang in đọc được là {observed[page]} nhưng theo các trang "
                f"khác phải là {page + offset} (OCR đọc nhầm?) - dùng {page + offset}."
            )
            infos.append(
                PageInfo(
                    page=page,
                    printed_page=page + offset,
                    source="inferred",
                    flags=["printed_page_conflict"],
                )
            )
        else:
            infos.append(
                PageInfo(
                    page=page,
                    printed_page=page + offset,
                    source="inferred",
                    flags=["printed_page_inferred"],
                )
            )
    return infos, warnings


def save_furniture(result: FurnitureResult, path: Path) -> None:
    """Ghi `furniture.json`: các dòng đã bỏ (kèm lý do), ánh xạ trang, cảnh báo - không gồm
    nội dung (nội dung đi tiếp sang P1.3)."""
    write_json(path, result.model_dump(mode="json", exclude={"content"}))


def strip_furniture(
    lines: list[Line],
    body_size: float,
    cfg: FurnitureCfg | None = None,
    pdf_pages: list[int] | None = None,
    page_number: Callable[[str], int | None] = page_number_of,
) -> FurnitureResult:
    """Bỏ đồ đạc trang và ánh xạ số trang in cho `pdf_pages` (mặc định: các trang có dòng).
    `page_number`: dòng nào là số trang - luật của sách (mặc định: page_number_of)."""
    content, removed = classify_furniture(lines, body_size, cfg, page_number)
    pages = pdf_pages if pdf_pages is not None else sorted({ln.page for ln in lines})
    infos, warnings = map_printed_pages(pages, removed)
    return FurnitureResult(content=content, removed=removed, pages=infos, warnings=warnings)
