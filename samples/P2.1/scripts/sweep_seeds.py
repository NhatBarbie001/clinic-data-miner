import tempfile
from pathlib import Path

from dataminer.devtools.sample_book import make_sample_book
from dataminer.evaluation.p2_eval import eval_toc
from dataminer.structure.toc import extract_toc

ok = 0
for s in range(1, 31):
    b = make_sample_book(Path(tempfile.mkdtemp()), seed=s)
    truth = b.truth
    r = extract_toc(b.pdf_path, book_id="book01")
    g = eval_toc(r, truth)["G1_toc"]
    ok += g["pass"]
    flags = [(e.title, e.flags) for e in r.entries if e.flags]
    print(
        s,
        "✓" if g["pass"] else "✗",
        f"sạch {g['title_clean_match']}/5",
        g["problems"],
        g["ocr_damaged_titles"],
        flags,
    )
print(f"ĐẠT {ok}/30")
