"""P2.5 - quét 30 seed: cây dựng với "P1 hoàn hảo" (văn bản block = văn bản sạch) → sinh bộ câu
hỏi → G7. Kiểm: số câu, phân bổ, mọi nguồn/trích dẫn hợp lệ, nội dung câu hỏi giống nhau giữa các
seed (nội dung sách không đổi theo seed, chỉ lỗi OCR đổi).
Chạy từ gốc repo: uv run python samples/P2.5/scripts/sweep_seeds.py"""

import sys
import tempfile
from pathlib import Path

# script chạy trực tiếp: thêm gốc repo để import được helper trong tests/
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tests.unit.test_golden import oracle_blocks
from tests.unit.test_tree_builder import pipeline

from dataminer.books.book01.golden import clean_texts, draft_golden
from dataminer.books.book01.rules import build_tree, classify_headings
from dataminer.devtools.sample_book import make_sample_book
from dataminer.evaluation.golden import validate_golden
from dataminer.structure.section_mapper import load_section_map, map_sections

MAPPING = load_section_map(Path("configs/books/book01/section_map.yaml"))
ok = 0
reference = None
for seed in range(1, 31):
    book = make_sample_book(Path(tempfile.mkdtemp()), seed=seed)
    blocks, lines, _, toc = pipeline(book.pdf_path)
    blocks = oracle_blocks(blocks, lines, book.truth)
    nodes = build_tree(
        blocks, classify_headings(blocks, toc).decisions, book_id="book01", toc=toc
    ).nodes
    map_sections(nodes, MAPPING)
    items = draft_golden(nodes, clean_texts(nodes, blocks, lines, book.truth))
    report = validate_golden(items, nodes)
    content = [(i.question, i.answer_points) for i in items]
    reference = reference or content
    same = content == reference
    ok += report.ok and same
    print(
        f"{seed:2d} {'✓' if report.ok and same else '✗'} {report.items} câu {report.by_type} "
        f"cảnh báo={len(report.warnings)} giống_seed_1={same} {report.errors[:2]}"
    )
print(f"ĐẠT {ok}/30")
