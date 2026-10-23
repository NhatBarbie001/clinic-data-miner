"""P2.6 - mutation check: cài từng đột biến vào code → test phải FAIL; xác nhận đột biến áp dụng
được (chuỗi gốc khớp đúng 1 lần), luôn khôi phục file. Chạy từ gốc repo:
uv run python samples/P2.6/scripts/mutation_check.py [Rn]"""

import subprocess
import sys
from pathlib import Path

E = "src/dataminer/evaluation/p2_eval.py"
R = "src/dataminer/structure/report.py"
P = "src/dataminer/pipeline/p2.py"
C = "src/dataminer/cli/p2.py"
TESTS = "tests/unit/test_p2_pipeline.py"
M = [
    (
        "R1 thiếu golden vẫn đạt G7",
        E,
        '            "pass": False,\n',
        '            "pass": True,\n',
    ),
    (
        "R2 eval bỏ G3/G4/G6",
        E,
        "    report.update(eval_tree(nodes, blocks, lines, truth, pages))\n",
        "",
    ),
    ("R3 ma trận luôn ✓", R, '"✓" if t in have[d.id] else "—"', '"✓"'),
    ("R4 báo cáo bỏ cờ của nút", R, "        for f in n.flags:\n", "        for f in []:\n"),
    ("R5 báo cáo bỏ mục quá dài", R, "if w > LONG_FACTOR * median:", "if False:"),
    ("R6 báo cáo không so trang mục lục", R, "if hit.page_start == e.pdf_page", "if True"),
    ("R7 báo cáo dùng ghép cũ của P2.2", R, "if d.toc_match in in_toc and", "if d.toc_match and"),
    (
        "R8 manifest thiếu file ra",
        P,
        '            run.add_output(out / name, records=name.endswith(".jsonl"))\n',
        "            pass\n",
    ),
    (
        "R9 eval chưa đạt vẫn exit 0",
        C,
        "    if not ok:\n        raise typer.Exit(1)\n",
        "    if False:\n        raise typer.Exit(1)\n",
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
