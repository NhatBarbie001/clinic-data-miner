"""P2R I2 - kiểm P1 của sách IASP bằng ĐẾM ĐỘC LẬP trên PDF gốc (code riêng, không qua bộ luật).
Chạy sau `dm --book iasp p1 run --scope all`: uv run python samples/P2R/scripts/check_p1_iasp.py"""

import re
from collections import Counter
from pathlib import Path

import pymupdf

from dataminer.books.iasp.layout import column_of
from dataminer.core.io import read_jsonl
from dataminer.model.block import Block
from dataminer.model.line import Line

PDF = Path("data/books/iasp/raw/classification_of_chronic_pain.pdf")
OUT = Path("data/books/iasp/p1_clean")
FIRST, LAST = 53, 222
RE_PAGE = re.compile(r"^(page\s+)?\d{1,4}$", re.IGNORECASE)
RE_JUNK = re.compile(r"^Page\s+\d+\s+is\s+BLANK$", re.IGNORECASE)


def alnum(text: str) -> int:
    return sum(c.isalnum() for c in text)


# ---------------------------------------------------------------- đếm thẳng trên PDF
doc = pymupdf.open(PDF)
pdf_chars = 0
big_bold = 0
field_titles: Counter[str] = Counter()
for i in range(FIRST - 1, LAST):
    for b in doc[i].get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            spans = [s for s in ln["spans"] if s["text"].strip()]
            if not spans:
                continue
            text = " ".join("".join(s["text"] for s in ln["spans"]).split())
            if RE_PAGE.match(text) or RE_JUNK.match(text):
                continue  # số trang (L2), dòng rác (L3)
            pdf_chars += alnum(text)
            bold = any(s["flags"] & 16 for s in spans)
            if bold and spans[0]["size"] >= 12.4:
                big_bold += 1
            if bold and spans[0]["size"] < 11:
                field_titles[text] += 1

# ---------------------------------------------------------------- kết quả P1
lines = {ln.id: ln for ln in read_jsonl(OUT / "lines.jsonl", Line)}
blocks = list(read_jsonl(OUT / "blocks.jsonl", Block))
block_chars = sum(alnum(b.text) for b in blocks)
marker_chars = sum(alnum(b.marker or "") for b in blocks)  # "1." của danh sách số
mixed = []
TABLE_PAGES = range(106, 109)  # bảng đối chiếu (L14): trang 1 cột, đọc theo hàng
for b in blocks:
    if b.page_start in TABLE_PAGES:
        continue
    cols = {column_of({"bbox": lines[i].bbox}) for i in b.line_ids} - {"full"}
    if len(cols) > 1 and not ({"joined_across_columns", "joined_across_pages"} & set(b.flags)):
        mixed.append((b.page_start, b.text[:60]))
heading_lines = sum(len(b.line_ids) for b in blocks if b.kind == "heading" and b.font_size >= 12.4)
definition_blocks = sum(b.kind == "heading" and b.text == "Definition" for b in blocks)

kinds = dict(Counter(b.kind for b in blocks))
print(f"Part II = PDF {FIRST}-{LAST} · {len(lines)} dòng · {len(blocks)} block · {kinds}")
print(f"A1 không trộn cột  : {len(mixed)} block trộn cột không có cờ nối {mixed[:3]}")
print(f"   bảng giả        : {sum(b.kind == 'table' for b in blocks)}")
total = block_chars + marker_chars
print(
    f"A7 không mất chữ   : PDF {pdf_chars} ký tự chữ/số · block {block_chars} + ký hiệu "
    f"{marker_chars} = {total} → lệch {pdf_chars - total}"
)
print(f"Tiêu đề lớn (đậm ≥12.4): PDF {big_bold} dòng · block tiêu đề lớn gồm {heading_lines} dòng")
print(f"'Definition': PDF {field_titles['Definition']} dòng · block {definition_blocks}")
print("Tên mục (đậm cỡ thường) phổ biến:", field_titles.most_common(8))
