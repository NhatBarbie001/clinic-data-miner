"""P2.5 - mutation check: cài từng đột biến vào code → test phải FAIL; xác nhận đột biến áp dụng
được (chuỗi gốc khớp đúng 1 lần), luôn khôi phục file. Chạy từ gốc repo:
uv run python samples/P2.5/scripts/mutation_check.py [Gn]"""

import subprocess
import sys
from pathlib import Path

G = "src/dataminer/structure/golden.py"
C = "src/dataminer/cli/p2.py"
TESTS = "tests/unit/test_golden.py"
M = [
    (
        "G1 so trích dẫn phân biệt khoảng trắng",
        G,
        "if squash(quote) in squash(node_text):",
        "if quote in node_text:",
    ),
    ("G2 so số liệu kiểu chuỗi con", G, "if n not in have]", "if n not in node_text]"),
    ("G3 bỏ so theo tập từ (ý ghép từ bảng)", G, "<= words", "<= set()"),
    (
        "G4 tách ý gồm cả hàng bảng/chú thích",
        G,
        'if not ln or "|" in ln or RE_CAPTION_LINE.match(ln):',
        "if not ln:",
    ),
    (
        "G5 văn bản 'sạch' lấy từ OCR",
        "src/dataminer/books/book01/golden.py",
        "    if truth is None:\n",
        "    if True:\n",
    ),
    (
        "G6 liệt kê không lọc loại mục",
        G,
        "            if n.section_type not in section_types:\n",
        "            if False:\n",
    ),
    ("G7 bỏ kiểm hạn ngạch", G, "if by_type[t] != want:", "if False:"),
    ("G8 câu từ chối được có nguồn", G, "if item.sources or item.answer_points:", "if False:"),
    (
        "G9 bỏ kiểm từ khóa câu từ chối",
        G,
        'found = [k for k in item.check.get("keywords", []) if loose(k) in book]',
        "found = []",
    ),
    ("G10 câu từ chối không cần từ khóa", G, 'if not item.check.get("keywords"):', "if False:"),
    (
        "G11 bỏ lỗi nút nguồn không tồn tại",
        G,
        'errors.append(f"{tag}: nút nguồn {s.node_id} không tồn tại (cây đã đổi?)")',
        "pass",
    ),
    ("G12 bỏ kiểm path", G, "if node.path != s.path:", "if False:"),
    ("G13 bỏ kiểm câu gần trùng", G, ".ratio() >= 0.9:", ".ratio() >= 1.01:"),
    ("G14 bỏ kiểm ý ↔ nội dung nút", G, "        if got != want:\n", "        if False:\n"),
    (
        "G15 bỏ tính lại tập bệnh",
        G,
        "        if item.answer_points != want:\n",
        "        if False:\n",
    ),
    (
        "G16 CLI ghi đè v1 đã khóa",
        C,
        "if [i.model_dump() for i in old] == [i.model_dump() for i in items]:",
        "if True:",
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
