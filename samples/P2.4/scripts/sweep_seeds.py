"""P2.4 - quét 30 seed: block P1 (CHỈ quy tắc, chưa sửa OCR) → mục lục → cấp tiêu đề → cây
→ loại mục → G5. Chạy: uv run python samples/P2.4/scripts/sweep_seeds.py"""

import tempfile
from pathlib import Path

from dataminer.books.book01.rules import build_blocks, build_tree, classify_headings
from dataminer.books.book01.toc import extract_toc
from dataminer.core.config import BlocksCfg
from dataminer.devtools.sample_book import make_sample_book
from dataminer.evaluation.p2_eval import eval_sections
from dataminer.pdf.furniture import strip_furniture
from dataminer.pdf.reader import body_font_size, read_lines
from dataminer.structure.section_mapper import load_section_map, map_sections

PILOT = (4, 9)
MAPPING = load_section_map(Path("configs/books/book01/section_map.yaml"))
ok = 0
for seed in range(1, 31):
    book = make_sample_book(Path(tempfile.mkdtemp()), seed=seed)
    lines = read_lines(book.pdf_path, pages=PILOT)
    body = body_font_size(lines)
    fr = strip_furniture(lines, body, pdf_pages=list(range(PILOT[0], PILOT[1] + 1)))
    printed = {p.page: p.printed_page for p in fr.pages}
    blocks = build_blocks(fr.content, body, BlocksCfg(), printed)
    toc = extract_toc(book.pdf_path, book_id="book01").entries
    decisions = classify_headings(blocks, toc).decisions
    tree = build_tree(blocks, decisions, book_id="book01", toc=toc)
    result = map_sections(tree.nodes, MAPPING)
    g5 = eval_sections(tree.nodes, book.truth, PILOT)["G5_section_types"]
    ok += g5["pass"]
    print(
        f"{seed:2d} {'✓' if g5['pass'] else '✗'} {g5['correct']}/{g5['truth']} "
        f"other={g5['other_ratio']} nguồn={result.counts} đề_xuất={len(result.proposals)} "
        f"{g5['problems']}"
    )
print(f"ĐẠT {ok}/30")
