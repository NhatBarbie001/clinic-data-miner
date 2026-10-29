"""Kiểm đột biến I5: phá từng luật của công cụ soát tay → test phải đỏ ("BẮT ĐƯỢC").

    PYTHONIOENCODING=utf-8 uv run python samples/P2R/scripts/mutate_i5.py
File gốc luôn được trả lại (kể cả khi lỗi).
"""

import subprocess
from pathlib import Path

SC = "src/dataminer/evaluation/spotcheck.py"
PAGE = "src/dataminer/evaluation/spotcheck_page.py"
CLI = "src/dataminer/cli/p2.py"
TESTS = ["tests/unit/test_spotcheck.py", "tests/books/test_iasp_i5.py"]
MUTATIONS = [
    ("M1 nhóm nhỏ có thể 0 lượt", SC, "if n >= len(sizes):", "if False:"),
    ("M2 chọn cả bệnh có cờ", SC, "return not (set(unit.flags) - BENIGN_FLAGS)", "return True"),
    ("M3 bỏ qua seed", SC, "rng = random.Random(seed)", "rng = random.Random(0)"),
    ("M4 không escape chữ sách", PAGE, "return html.escape(text, quote=True)", "return text"),
    ("M5 không chặn </script> trong dữ liệu", PAGE, 'data = data.replace("</", "<\\\\/")',
     "data = data"),
    ("M6 tọa độ chia nhầm chiều", SC, "left=round(100 * x0 / w, 3)",
     "left=round(100 * x0 / h, 3)"),
    ("M7 ngưỡng A9 lỏng", SC, "passed >= need", "passed >= need - 1"),
    ("M8 ô trống tính là đạt", SC, 'if row is None or any(v == "" for v in values.values()):',
     "if row is None:"),
    ("M9 ghi đè phiếu đã chấm", CLI, "kept = any(", "kept = False and any("),
    ("M10 bỏ cảnh báo bản cây cũ", CLI, 'sha256_file(nodes_path) != meta["nodes_sha256"]',
     'sha256_file(nodes_path) == ""'),
    ("M11 không đọc ';' của Excel", SC, 'delimiter = ";" if', 'delimiter = "," if'),
    ("M12 cột loại mục trùng cột mã", SC, '**{f"has_{t}": "✓"', '**{t: "✓"'),
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
