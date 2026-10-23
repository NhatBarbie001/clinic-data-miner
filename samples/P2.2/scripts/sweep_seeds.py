"""P2.2 - quét 30 seed sách mẫu: block của P1 (CHỈ quy tắc, chưa sửa OCR → tiêu đề còn lỗi)
+ mục lục P2.1 → cấp tiêu đề → G2. Chạy: uv run python samples/P2.2/scripts/sweep_seeds.py"""

import tempfile
from pathlib import Path

from dataminer.books.book01.rules import build_blocks, classify_headings
from dataminer.books.book01.toc import extract_toc
from dataminer.core.config import BlocksCfg
from dataminer.devtools.sample_book import make_sample_book
from dataminer.evaluation.truth.p2_eval import eval_heading_levels
from dataminer.pdf.furniture import strip_furniture
from dataminer.pdf.reader import body_font_size, read_lines

PILOT = (4, 9)
ok = 0
for seed in range(1, 31):
    book = make_sample_book(Path(tempfile.mkdtemp()), seed=seed)
    lines = read_lines(book.pdf_path, pages=PILOT)
    body = body_font_size(lines)
    fr = strip_furniture(lines, body, pdf_pages=list(range(PILOT[0], PILOT[1] + 1)))
    blocks = build_blocks(fr.content, body, BlocksCfg(), {p.page: p.printed_page for p in fr.pages})
    toc = extract_toc(book.pdf_path, book_id="book01")
    result = classify_headings(blocks, toc.entries)
    g2 = eval_heading_levels(result.decisions, book.truth, PILOT)["G2_heading_levels"]
    ok += g2["pass"]
    fuzzy = [d.text for d in result.decisions if d.source == "toc" and "khớp gần" in d.reasons[-1]]
    print(
        f"{seed:2d} {'✓' if g2['pass'] else '✗'} {g2['correct']}/{g2['truth']} "
        f"nguồn={g2['by_source']} khớp_gần={fuzzy} cảnh_báo={len(result.warnings)} {g2['problems']}"
    )
print(f"ĐẠT {ok}/30")
