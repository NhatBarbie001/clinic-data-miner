"""P2.1 - quét 30 seed sách mẫu: mục lục → G1.

Chạy: uv run python samples/P2.1/scripts/sweep_seeds.py

Cột: seed · G1 · tiêu đề sạch khớp (match_key) · lỗi G1 · tiêu đề còn lỗi nhầm ký tự · cờ.
"""

import tempfile
from pathlib import Path

from dataminer.books.book01.toc import extract_toc
from dataminer.devtools.sample_book import make_sample_book
from dataminer.evaluation.truth.p2_eval import eval_toc

ok = 0
for seed in range(1, 31):
    book = make_sample_book(Path(tempfile.mkdtemp()), seed=seed)
    result = extract_toc(book.pdf_path, book_id="book01")
    g1 = eval_toc(result, book.truth)["G1_toc"]
    ok += g1["pass"]
    flags = [(e.title, e.flags) for e in result.entries if e.flags]
    print(
        seed,
        "✓" if g1["pass"] else "✗",
        f"sạch {g1['title_clean_match']}/5",
        g1["problems"],
        g1["ocr_damaged_titles"],
        flags,
    )
print(f"ĐẠT {ok}/30")
