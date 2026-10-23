"""P2.3 - quét 30 seed sách mẫu: block P1 (CHỈ quy tắc, chưa sửa OCR) → mục lục → cấp tiêu đề
→ cây → G3, G4, G6. Chạy: uv run python samples/P2.3/scripts/sweep_seeds.py"""

import tempfile
from pathlib import Path

from dataminer.books.book01.rules import build_blocks, build_tree, classify_headings
from dataminer.books.book01.toc import extract_toc
from dataminer.core.config import BlocksCfg
from dataminer.devtools.sample_book import make_sample_book
from dataminer.evaluation.truth.p2_eval import all_pass, eval_tree
from dataminer.pdf.furniture import strip_furniture
from dataminer.pdf.reader import body_font_size, read_lines

PILOT = (4, 9)
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
    report = eval_tree(tree.nodes, blocks, fr.content, book.truth, PILOT)
    ok += all_pass(report)
    g4 = report["G4_content_in_node"]
    levels = [n.level for n in tree.nodes]
    print(
        f"{seed:2d} {'✓' if all_pass(report) else '✗'} "
        f"G3={'✓' if report['G3_diseases_vs_toc']['pass'] else '✗'} "
        f"G4={g4['correct']}/{g4['lines']} "
        f"G6={'✓' if report['G6_invariants']['pass'] else '✗'} "
        f"nút: {levels.count('chapter')} chương, {levels.count('disease')} bệnh, "
        f"{levels.count('section')} mục, {levels.count('subsection')} mục con · "
        f"cảnh báo {len(tree.warnings)} {report['G3_diseases_vs_toc']['problems']} {g4['problems']}"
    )
print(f"ĐẠT {ok}/30")
