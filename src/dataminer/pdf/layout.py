"""Thứ tự đọc của các dòng trên một trang.

Hiện có: theo HÀNG (gom dòng cùng dải dọc, sắp trái → phải) - đúng với sách 1 cột.
Sách 2 cột cần thứ tự theo CỘT (xem docs/phases/P2R/plan.md, luật L4)."""

from typing import Any

from dataminer.model.line import Line

ROW_TOLERANCE = 0.4  # hai dòng cùng hàng nếu tâm dọc lệch < 0.4 × cỡ chữ


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
