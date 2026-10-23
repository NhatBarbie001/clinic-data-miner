"""P1.6 - Báo cáo `report.md` của phase P1: tổng quan, chỉ tiêu, trước/sau theo trang, chờ duyệt."""

import difflib
from pathlib import Path
from typing import Any

from dataminer.core.io import read_json, read_jsonl
from dataminer.ingest.review import build_queue
from dataminer.model.block import Block

GATE_NAMES = {
    "G1_furniture": "G1 header/footer bỏ đủ, không bỏ nhầm",
    "G2_printed_pages": "G2 số trang in",
    "G3_blocks": "G3 block đúng tập dòng (≥ 97%), không gộp nhầm",
    "G4_tables": "G4 bảng hàng × cột",
    "G5_wer": "G5 tỉ lệ từ sai ≤ 1%",
    "G6_errors_fixed": "G6 lỗi đã cài được sửa ≥ 80%",
    "G7_introduced": "G7 từ đúng bị sửa sai ≤ 0.3%",
    "G8_numbers": "G8 số liệu không đổi nếu chưa qua duyệt",
    "G9_nfc": "G9 Unicode NFC",
}


def _highlight(before: str, after: str) -> str:
    """Văn bản `after`, các token khác `before` được in đậm."""
    a, b = before.split(), after.split()
    out: list[str] = []
    for tag, _, _, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        chunk = b[j1:j2]
        out.extend(chunk if tag == "equal" else [f"**{t}**" for t in chunk])
    return " ".join(out)


def _gate_detail(item: dict[str, Any]) -> str:
    keys = ("recall", "after", "rate", "removed", "pages", "found_tables", "tokens")
    return ", ".join(f"{k}={item[k]}" for k in keys if k in item)


def render_report(out_dir: Path) -> str:
    manifest = read_json(out_dir / "manifest.json")
    blocks = list(read_jsonl(out_dir / "blocks.jsonl", Block))
    counts = manifest.get("counts", {})
    llm = manifest["llm"]
    prompts = (
        ", ".join(f"{k}@{v}" for k, v in manifest.get("prompts", {}).items()) or "không dùng LLM"
    )
    lines = [
        "# Báo cáo P1: trích xuất và làm sạch text",
        "",
        "## 1. Tổng quan",
        "",
        f"- Lần chạy: `{manifest['run_id']}` · trạng thái **{manifest['status']}** · "
        f"{manifest.get('duration_s')}s · git `{(manifest.get('git_commit') or '')[:7]}`",
        f"- Prompt: {prompts} · chi phí LLM: ${llm['cost_usd']:.6f} ({llm['calls']} lời gọi)",
        *[f"- {note}" for note in manifest.get("notes", [])],
        "",
        "| chỉ số | giá trị |",
        "|---|---|",
        *[f"| {k} | {v} |" for k, v in counts.items()],
        "",
        "## 2. Chỉ tiêu (so với đáp án)",
        "",
    ]
    eval_path = out_dir / "eval.json"
    if eval_path.is_file():
        report = read_json(eval_path)
        lines += ["| chỉ tiêu | kết quả | chi tiết |", "|---|---|---|"]
        for key, name in GATE_NAMES.items():
            if key in report:
                mark = "✅" if report[key].get("pass") else "❌"
                lines.append(f"| {name} | {mark} | {_gate_detail(report[key])} |")
    else:
        lines.append("_Chưa có `eval.json` - chạy `dm p1 eval` (chỉ khi có đáp án, vd. sách mẫu)._")

    lines += [
        "",
        "## 3. Trước / sau theo trang",
        "",
        "Chỉ liệt kê block có thay đổi; **in đậm** = token đã đổi (LLM hoặc người duyệt).",
    ]
    page = None
    changed = [b for b in blocks if b.text != b.text_rules]
    for block in changed:
        if block.page_start != page:
            page = block.page_start
            lines += ["", f"### Trang PDF {page} (trang in {block.printed_start})", ""]
        if block.kind == "table":
            rows_b, rows_a = block.text_rules.split("\n"), block.text.split("\n")
            for rb, ra in zip(rows_b, rows_a, strict=False):
                if rb != ra:
                    lines.append(f"- *bảng*: {_highlight(rb, ra)}")
        else:
            lines.append(f"- *{block.kind}*: {_highlight(block.text_rules, block.text)}")
    lines.append("")
    lines.append(f"Tổng: {len(changed)}/{len(blocks)} block có thay đổi.")

    pending = build_queue(blocks)
    lines += ["", f"## 4. Mục chờ duyệt ({len(pending)})", ""]
    if pending:
        lines += [
            "| ưu tiên | trang in | ngữ cảnh | hiện tại | gợi ý | lý do |",
            "|---|---|---|---|---|---|",
        ]
        lines += [
            f"| {i.priority} | {i.printed_page} | {i.context} | `{i.current}` "
            f"| `{i.suggestion}` | {i.reason} |"
            for i in pending
        ]
    else:
        reviewed = sum(len(b.reviews) for b in blocks)
        lines.append(f"Không còn mục chờ duyệt ({reviewed} quyết định đã áp).")
    return "\n".join(lines) + "\n"
