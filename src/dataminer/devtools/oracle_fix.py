""" "LLM hoàn hảo" cho sách mẫu: trả về đúng văn bản SẠCH của đáp án cho từng mục sửa lỗi.

Dùng làm ĐỐI CHỨNG DƯƠNG cho guard + đánh giá P1.4: với output hoàn hảo, mọi chỉ tiêu phải đạt,
và guard phải chặn đúng (chỉ) các thay đổi số liệu. Nếu không → lỗi nằm ở guard/đánh giá,
không phải ở LLM. (Đối chứng này đã tìm ra 3 lỗi - xem P1.4_report.)
"""

from typing import Any

from dataminer.evaluation.p1_eval import _line_key_map, _norm, _truth_keys
from dataminer.ingest.blocks import Block, join_text
from dataminer.ingest.ocr_fixer import block_items
from dataminer.ingest.pdf_reader import Line


def oracle_outputs(blocks: list[Block], lines: list[Line], truth: dict[str, Any]) -> dict[str, str]:
    pages = {ln.page for ln in lines}
    raw = {
        (t["pdf_page"], _norm(t["ocr"])): t["text"]
        for t in truth["lines"]
        if t["pdf_page"] in pages
    }
    clean_of = {t["key"]: raw[(t["key"][0], t["key"][1])] for t in _truth_keys(truth, pages)}
    key_of = _line_key_map(lines)
    grids = {t["pdf_page"]: t["rows"] for t in truth.get("tables", [])}
    outputs: dict[str, str] = {}
    for block in blocks:
        for item_id, _ in block_items(block):
            if block.kind == "table":
                r, c = (int(x) for x in item_id.split("#r")[1].split("c"))
                outputs[item_id] = grids[block.page_start][r][c]
                continue
            parts = [clean_of[key_of[lid]] for lid in block.line_ids]
            text = parts[0]
            for part in parts[1:]:
                text = join_text(text, part)
            if block.marker and text.startswith(block.marker):
                text = text[len(block.marker) :].strip()
            outputs[item_id] = text
    return outputs
