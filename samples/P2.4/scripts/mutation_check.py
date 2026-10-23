"""P2.4 - mutation check: cài từng đột biến vào code → test phải FAIL; xác nhận đột biến áp dụng
được (chuỗi gốc khớp đúng 1 lần), luôn khôi phục file. Chạy từ gốc repo:
uv run python samples/P2.4/scripts/mutation_check.py [Sn|En]"""

import subprocess
import sys
from pathlib import Path

S = "src/dataminer/structure/section_mapper.py"
E = "src/dataminer/evaluation/truth/p2_eval.py"
TESTS = "tests/unit/test_section_mapper.py"
M = [
    ("S1 bỏ khớp gần", S, "if best[0] >= fuzzy_min:", "if False:"),
    (
        "S2 bỏ kế thừa mục cha",
        S,
        'if n.level == "subsection" and parent is not None and parent.section_type:',
        "if False:",
    ),
    (
        "S3 hỏi LLM mỗi nút (không gộp tên trùng)",
        S,
        "unknown.setdefault(key, []).append(n)",
        'unknown.setdefault(f"{key}#{n.id}", []).append(n)',
    ),
    (
        "S4 không xóa kết quả cũ khi chạy lại",
        S,
        "n.flags = [f for f in n.flags if f not in SECTION_FLAGS]",
        "pass",
    ),
    (
        "S5 chuẩn hóa giữ dấu",
        S,
        'text = " ".join(strip_diacritics(text).casefold().split())',
        'text = " ".join(text.casefold().split())',
    ),
    (
        "S6 chuẩn hóa giữ số thứ tự",
        S,
        'text = RE_SECTION_PREFIX.sub("", nfc(title).strip())',
        "text = nfc(title).strip()",
    ),
    (
        "S7 từ điển: bỏ kiểm khóa chuẩn hóa",
        S,
        "if key != normalize_section_title(key):",
        "if False:",
    ),
    (
        "S8 từ điển: bỏ kiểm loại",
        S,
        "        if value not in SECTION_TYPES:\n            errors.append(\n"
        '                f"dòng {lineno}: loại',
        '        if False:\n            errors.append(\n                f"dòng {lineno}: loại',
    ),
    (
        "S9 từ điển: bỏ kiểm khóa trùng",
        S,
        "if key in mapping and mapping[key] != value:",
        "if False:",
    ),
    (
        "S10 nhập CSV: có lỗi vẫn ghi",
        S,
        "    if errors:\n        raise SectionMapError(\n",
        "    if False:\n        raise SectionMapError(\n",
    ),
    (
        "S11 nhập CSV: bỏ kiểm edited_value",
        S,
        "                if value not in SECTION_TYPES:",
        "                if False:",
    ),
    ("S12 nhập CSV: ghi đè khóa đã có", S, "if current.get(p.key, value) != value:", "if False:"),
    (
        "S13 nhập CSV: edit dùng đề xuất LLM",
        S,
        'value = (row.get("edited_value") or "").strip()',
        "value = p.proposal",
    ),
    (
        "S14 CSV không có BOM",
        S,
        'path.open("w", encoding="utf-8-sig", newline="")',
        'path.open("w", encoding="utf-8", newline="")',
    ),
    ("S15 bỏ cờ section_type_unknown", S, 'n.flags.append("section_type_unknown")', "pass"),
    ("S16 bỏ cờ section_type_from_llm", S, 'n.flags.append("section_type_from_llm")', "pass"),
    ("E1 G5 không so loại", E, 'if n.section_type == want["section_type"]:', "if True:"),
    ("E2 G5 nới ngưỡng other", E, "and other < 0.05", "and other < 0.5"),
    (
        "E3 G5 bỏ kiểm gióng thứ tự",
        E,
        "        if similar.ratio() < 0.8:\n"
        "            problems.append(f\"#{i + 1} lệch thứ tự: '{n.title}'",
        "        if False:\n            problems.append(f\"#{i + 1} lệch thứ tự: '{n.title}'",
    ),
    ("E4 G5 bỏ đếm mục thừa", E, "            and not extra,\n", "            and True,\n"),
    ("E5 G5 hạ ngưỡng 90%", E, "and accuracy >= 0.95", "and accuracy >= 0.9"),
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
