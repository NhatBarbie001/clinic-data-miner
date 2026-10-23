"""P2.3 - mutation check: cài từng đột biến vào code → test phải FAIL; xác nhận đột biến áp dụng
được (chuỗi gốc khớp đúng 1 lần), luôn khôi phục file. Chạy từ gốc repo:
uv run python samples/P2.3/scripts/mutation_check.py [Tn|En]"""

import subprocess
import sys
from pathlib import Path

T = "src/dataminer/structure/tree_builder.py"
E = "src/dataminer/evaluation/truth/p2_eval.py"
TESTS = "tests/unit/test_tree_builder.py"
M = [
    (
        "T1 tiêu đề cùng cấp không đóng nút",
        T,
        "while RANK[stack[-1].level] >= rank:",
        "while RANK[stack[-1].level] > rank:",
    ),
    ("T2 không tạo nút phần đầu", T, "if top is root:", "if False:"),
    ("T3 bỏ cờ orphan_subsection", T, 'node.flags.append("orphan_subsection")', "pass"),
    ("T4 bỏ cờ orphan_section", T, 'node.flags.append("orphan_section")', "pass"),
    ("T5 phạm vi trang không gồm con", T, "        if spans:\n", "        if False:\n"),
    (
        "T6 trang in không gồm con",
        T,
        "node.printed_start = min(printed_all, default=None)",
        "node.printed_start = min(printed, default=None)",
    ),
    ("T7 bỏ cờ empty", T, 'node.flags.append("empty")', "pass"),
    ("T8 không xử lý path trùng", T, "while node_id in used:", "while False:"),
    (
        "T9 ID phụ thuộc nội dung",
        T,
        'node_id = stable_id(book_id, *path, prefix="nd")',
        'node_id = stable_id(book_id, *path, *(b.text for b in draft.content), prefix="nd")',
    ),
    ("T10 bỏ ký hiệu gạch đầu dòng", T, 'return f"{marker} {block.text}"', "return block.text"),
    (
        "T11 bỏ số thứ tự khỏi tên mục: không",
        T,
        'text = RE_SECTION_PREFIX.sub("", nfc(text).strip())',
        "text = nfc(text).strip()",
    ),
    (
        "T12 không viết hoa sau 'Chương n.'",
        "src/dataminer/books/book01/headings.py",
        "title = title[: m.end()] + rest[:1].upper() + rest[1:]",
        "title = title",
    ),
    ("T13 bỏ cảnh báo mục lục thiếu nút", T, "if len(hits) != 1:", "if False:"),
    (
        "T14 bỏ cảnh báo lệch trang mục lục",
        T,
        "elif hits[0].page_start != e.pdf_page:",
        "elif False:",
    ),
    ("T15 bất biến bỏ kiểm thứ tự", T, "if order != [b.id for b in blocks]:", "if False:"),
    (
        "T16 bất biến bỏ kiểm phạm vi cha",
        T,
        "if not parent.page_start <= n.page_start <= n.page_end <= parent.page_end:",
        "if False:",
    ),
    (
        "T17 bất biến bỏ kiểm block thuộc 1 nút",
        T,
        "        if len(holders) != 1:\n",
        "        if len(holders) > 99:\n",
    ),
    ("E1 G4 không so nút", E, "if got is not None and got == current:", "if got is not None:"),
    ("E2 G3 bỏ so trang", E, 'if node.page_start != e["pdf_page"]:', "if False:"),
    (
        "E3 G3 bỏ đếm bệnh thừa",
        E,
        "g3_problems.extend(f\"thừa nút bệnh '{n.title}'\"",
        "(f\"thừa nút bệnh '{n.title}'\"",
    ),
    (
        "E4 G6 không dùng bất biến",
        E,
        '"pass": not violations and len(nodes) > 1,',
        '"pass": len(nodes) > 1,',
    ),
    ("E5 G4 hạ ngưỡng 90%", E, "ratio >= 0.99", "ratio >= 0.9"),
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
