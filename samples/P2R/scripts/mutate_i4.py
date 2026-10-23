"""Kiểm đột biến I4: phá từng luật mới (loại mục, mục lục, A5, A6) → test phải đỏ ("BẮT ĐƯỢC").

    PYTHONIOENCODING=utf-8 uv run python samples/P2R/scripts/mutate_i4.py
File gốc luôn được trả lại (kể cả khi lỗi).
"""

import subprocess
from pathlib import Path

HEADINGS = "src/dataminer/books/iasp/headings.py"
TOC = "src/dataminer/books/iasp/toc.py"
LEVELS = "src/dataminer/structure/heading_levels.py"
CHECKS = "src/dataminer/evaluation/checks.py"
REPORT = "src/dataminer/structure/report.py"
MAP = "configs/books/iasp/section_map.yaml"
TESTS = ["tests/books", "tests/unit/test_p2_pipeline.py", "tests/unit/test_section_mapper.py"]
MUTATIONS = [
    ("M1 bỏ luật 'Code <mã>'", HEADINGS, "if RE_CODE_TITLE.match(_norm(title)):", "if False:"),
    ("M2 không bỏ chân trang 'v'", TOC, "and not RE_FOOTER.match(_norm(ln.text))", ""),
    ("M3 không tìm 'Part II'", TOC, "inside = True", "inside = inside"),
    ("M4 không nối dòng sau của tên", TOC, 'last.title = f"{last.title} {text}"',
     "last.title = last.title"),
    ("M5 chữ cái không thành part", TOC,
     'return "part" if RE_TOC_LETTER.match(title) else "chapter"', 'return "chapter"'),
    ("M6 bỏ toc_lists_diseases", LEVELS, " and cfg.toc_lists_diseases", ""),
    ("M7 mục lục bỏ qua cấp part", LEVELS, '("part", "chapter", "disease", "other")',
     '("chapter", "disease", "other")'),
    ("M8 A5 bỏ kiểm tên không tra được", CHECKS, "passed=share < max_other and not unknown",
     "passed=share < max_other"),
    ("M9 A6 bỏ kiểm trang", CHECKS, "elif hits[0].page_start != page:", "elif False:"),
    ("M10 báo cáo liệt kê loại mới", REPORT, "and t not in EXTRA_SECTION_TYPES", ""),
    ("M11 từ điển đổi quyết định", MAP, "aggravating factors: symptom",
     "aggravating factors: risk_factor"),
    ("M12 không dừng ở 'Part III'", TOC, "if RE_PART_END.match(text):", "if False:"),
]  # fmt: skip

for name, path, old, new in MUTATIONS:
    file = Path(path)
    original = file.read_text(encoding="utf-8")
    assert original.count(old) == 1, f"{name}: không thấy đúng 1 chỗ cần phá"
    file.write_text(original.replace(old, new), encoding="utf-8")
    try:
        run = subprocess.run(
            ["uv", "run", "pytest", "-q", "-x", *TESTS],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        print(name, "→", "BẮT ĐƯỢC" if run.returncode else "SỐNG SÓT")
    finally:
        file.write_text(original, encoding="utf-8")
