"""P2.2 - mutation check: cài từng đột biến vào code → test phải FAIL; xác nhận đột biến áp dụng
được (chuỗi gốc khớp đúng 1 lần), luôn khôi phục file. Chạy từ gốc repo:
uv run python samples/P2.2/scripts/mutation_check.py [Hn]"""

import subprocess
import sys
from pathlib import Path

H = "src/dataminer/structure/heading_levels.py"
E = "src/dataminer/evaluation/truth/p2_eval.py"
TESTS = "tests/unit/test_heading_levels.py"
M = [
    ("H1 bỏ khớp gần mục lục", H, "if score < cfg.toc_match_min:", "if score < 1.0:"),
    (
        "H2 bỏ mẫu chương không dấu",
        "src/dataminer/books/book01/headings.py",
        "if chapter := RE_CHAPTER_NORM.match(norm_title(block.text)):",
        "if chapter := RE_CHAPTER_NORM.match('x'):",
    ),
    ("H3 bỏ cờ missing_from_toc", H, 'd.flags.append("missing_from_toc")', "pass"),
    (
        "H4 mục lục không đổi cấp",
        H,
        'd.level, d.confidence, d.source = entry.level, "high", "toc"',
        'd.confidence, d.source = "high", "toc"',
    ),
    (
        "H5 gọi LLM cho mọi tiêu đề",
        H,
        'low = [d for d in decisions if d.confidence == "low"]',
        "low = list(decisions)",
    ),
    ("H6 không xét mục con thuộc mục", H, "if n != section or m != sub + 1:", "if m != sub + 1:"),
    (
        "H7 không đếm lại số mục mỗi bệnh",
        H,
        "            section, sub = 0, 0\n            continue",
        "            continue",
    ),
    ("H8 cảnh báo mục lục thiếu cả ngoài phạm vi", H, "lo <= e.pdf_page <= hi", "True"),
    (
        "H9 bỏ ngưỡng cỡ chữ của bệnh",
        "src/dataminer/books/book01/headings.py",
        "if block.is_upper and block.font_size >= threshold:",
        "if block.is_upper:",
    ),
    (
        "H10 mục chữ thường không xét cỡ",
        "src/dataminer/books/book01/headings.py",
        "if block.font_size >= body_size + SECTION_SIZE_DELTA:",
        "if True:",
    ),
    (
        "H11 eval bỏ kiểm tra gióng thứ tự",
        E,
        'match_key(d.text), match_key(want["text"]))\n        if similar.ratio() < 0.8:',
        'match_key(d.text), match_key(want["text"]))\n        if False:',
    ),
    (
        "H12 eval bỏ đếm tiêu đề thừa",
        E,
        "    problems.extend(f\"thừa tiêu đề '{d.text}'\"",
        "    (f\"thừa tiêu đề '{d.text}'\"",
    ),
    ("H13 eval bỏ so cấp", E, 'if d.level != want["level"]:', "if False:"),
    (
        "H14 bỏ cờ lệch trang mục lục",
        H,
        "if entry.pdf_page is not None and entry.pdf_page != page:",
        "if False:",
    ),
    ("H15 một mục lục ghép nhiều lần", H, "used.add(idx)", "pass"),
    (
        "H16 eval đạt khi đáp án rỗng",
        E,
        '"problems": problems,\n            "pass": not problems and len(expected) > 0,',
        '"problems": problems,\n            "pass": not problems,',
    ),
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
            [sys.executable, "-m", "pytest", TESTS, "-q", "-p", "no:cacheprovider"],
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
