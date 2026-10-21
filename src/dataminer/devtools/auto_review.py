"""Điền quyết định duyệt TỪ ĐÁP ÁN - CHỈ cho sách mẫu (không có người duyệt chuyên môn).

Đọc CSV hàng đợi đã xuất, điền cột decision/edited_value/reviewer như một người duyệt, ghi ra
CSV mới → nhập lại qua đúng `import_csv` như người thật. Nhờ vậy kiểm chứng TRỌN đường đi
xuất → duyệt → nhập → áp → chạy lại. Người duyệt được ghi rõ "auto-truth (sách mẫu)" để
không bao giờ nhầm với duyệt thật.
"""

import csv
from pathlib import Path
from typing import Any

from dataminer.devtools.oracle_fix import oracle_outputs
from dataminer.ingest.blocks import Block
from dataminer.ingest.pdf_reader import Line

REVIEWER = "auto-truth (sách mẫu)"


def fill_from_truth(
    queue_csv: Path, out_csv: Path, blocks: list[Block], lines: list[Line], truth: dict[str, Any]
) -> int:
    """Điền quyết định cho mọi dòng của `queue_csv`, ghi `out_csv`. Trả số dòng đã điền."""
    oracle = oracle_outputs(blocks, lines, truth)
    with queue_csv.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    for row in rows:
        item = row["block_id"] + (f"#{row['cell']}" if row["cell"] else "")
        correct_text = oracle[item]
        position = int(row["position"])
        if position < 0:  # cả block
            target = correct_text
        else:
            tokens = correct_text.split()
            target = tokens[position] if position < len(tokens) else ""
        if row["suggestion"] and target == row["suggestion"]:
            row["decision"] = "accept"
        elif target == row["current"]:
            row["decision"] = "keep"
        else:
            row["decision"], row["edited_value"] = "edit", target
        row["reviewer"] = REVIEWER
        row["comment"] = f"theo đáp án: «{target}»"
    with out_csv.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
