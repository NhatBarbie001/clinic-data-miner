"""Kiểm đột biến I3: phá từng luật IASP mới → `tests/books` phải đỏ ("BẮT ĐƯỢC").

    PYTHONIOENCODING=utf-8 uv run python samples/P2R/scripts/mutate_i3.py
File gốc luôn được trả lại (kể cả khi lỗi).
"""

import subprocess
from pathlib import Path

LINES = "src/dataminer/books/iasp/lines.py"
CODES = "src/dataminer/books/iasp/codes.py"
HEADINGS = "src/dataminer/books/iasp/headings.py"
CHECKS = "src/dataminer/evaluation/checks.py"
MUTATIONS = [
    ("M1 bỏ dừng sau mã", LINES, "if RE_CODE_END.search(prev):", "if False:"),
    ("M2 bỏ nối dòng ngoặc", LINES, "if RE_PAREN_LINE.match(text):", "if False:"),
    ("M3 bỏ nối 'and'", LINES, "if RE_AND_LINE.match(text):", "if False:"),
    ("M4 nhóm 11≠II", CODES, 'return "I" * len(raw)', "return raw"),
    ("M5 chữ 1→l", CODES, 'letter = m.group(4).replace("1", "l")', "letter = m.group(4)"),
    ("M6 cỡ 15 ngoài IN HOA", HEADINGS,
     "    if block.is_upper:\n        if block.font_size >= TITLE_SIZE:",
     "    if block.font_size >= TITLE_SIZE:\n        return 'other', 'high', ['x']\n"
     "    if block.is_upper:\n        if False:"),
    ("M7 bỏ cờ thiếu tên", HEADINGS, 'n.flags.append("missing_syndrome_title")', "pass"),
    ("M8 bỏ kiểm sai nhóm", HEADINGS, 'n.flags.append("code_group_mismatch")', "pass"),
    ("M9 A2 bỏ kiểm trùng", CHECKS, "if code in seen:", "if False:"),
    ("M10 Note là tên mục", LINES, "if RE_NOTE.match(text):", "if False:"),
    ("M11 strip_code chương", HEADINGS, "text = strip_code(text)  #", "text = text  #"),
    ("M12 mã con sai", CHECKS, "and sub in (0, 1)", "and sub >= 0"),
]  # fmt: skip

for name, path, old, new in MUTATIONS:
    file = Path(path)
    original = file.read_text(encoding="utf-8")
    assert original.count(old) == 1, f"{name}: không thấy đúng 1 chỗ cần phá"
    file.write_text(original.replace(old, new), encoding="utf-8")
    try:
        run = subprocess.run(
            ["uv", "run", "pytest", "-q", "-x", "tests/books"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        print(name, "→", "BẮT ĐƯỢC" if run.returncode else "SỐNG SÓT")
    finally:
        file.write_text(original, encoding="utf-8")
