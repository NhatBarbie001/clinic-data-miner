"""P2.1 - mutation check: cài từng đột biến vào code → test phải FAIL; xác nhận đột biến áp dụng
được (chuỗi gốc khớp đúng 1 lần), luôn khôi phục file. Chạy từ gốc repo:
uv run python samples/P2.1/scripts/mutation_check.py [Mn]"""

import subprocess
import sys
from pathlib import Path

T = "src/dataminer/books/book01/toc.py"
E = "src/dataminer/evaluation/p2_eval.py"
M = [
    (
        "M1 bỏ thụt lề khi mẫu chữ trượt",
        T,
        "        elif by_indent is not None:\n            level = by_indent",
        "        elif False:\n            level = by_indent",
    ),
    ("M2 không nối tiêu đề ngắt dòng", T, "if gap <= 1.0 * max", "if gap <= -1.0 * max"),
    (
        "M3 coi 'MỤC LỤC' là dòng thường",
        T,
        'return norm_title(text).rstrip(" .:") in TOC_TITLES',
        "return False",
    ),
    ("M4 gộp trang mục lục không liên tiếp", T, "pages = [hits[0]]", "pages = list(hits)"),
    (
        "M5 bỏ cảnh báo số trang giảm",
        T,
        "if cur.printed_page < prev.printed_page:",
        "if cur.printed_page > prev.printed_page + 999:",
    ),
    (
        "M6 ánh xạ trang lệch 1",
        T,
        "printed_to_pdf.get(e.printed_page)",
        "printed_to_pdf.get(e.printed_page + 1)",
    ),
    (
        "M7 không cho dòng không chấm dẫn",
        T,
        "parse_entry_line(ln.text, allow_plain=True)",
        "parse_entry_line(ln.text, allow_plain=False)",
    ),
    ("M8 bỏ cờ level_conflict", T, 'flags.append("level_conflict")', "pass"),
    ("M9 eval bỏ so tiêu đề", E, "if e.title != ocr_title:", "if False:"),
    (
        "M10 eval bỏ đếm mục thừa",
        E,
        "for e in got[len(expected) :]]\n    problems.extend(extra)",
        "for e in got[len(expected) :]]\n    pass",
    ),
    ("M11 eval bỏ so trang mục lục", E, "if result.toc_pages != truth_pages:", "if False:"),
    ("M12 eval bỏ so cấp", E, '("level", want["level"]),', ""),
]
only = sys.argv[1] if len(sys.argv) > 1 else None
for name, f, old, new in M:
    if only and not name.startswith(only + " "):
        continue
    p = Path(f)
    src = p.read_text(encoding="utf-8")
    n = src.count(old)
    if n != 1:
        print(f"{name}: KHÔNG ÁP DỤNG ĐƯỢC (khớp {n} lần)")
        continue
    p.write_text(src.replace(old, new), encoding="utf-8")
    try:
        r = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/unit/test_toc.py",
                "-q",
                "-x",
                "-p",
                "no:cacheprovider",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        last = r.stdout.strip().splitlines()[-1]
        failed = [
            ln.split("::")[1].split(" ")[0]
            for ln in r.stdout.splitlines()
            if ln.startswith("FAILED")
        ]
        print(f"{name}: {'BỊ BẮT ✓' if r.returncode else 'SỐNG SÓT ✗'} · {last} · {failed}")
    finally:
        p.write_text(src, encoding="utf-8")
