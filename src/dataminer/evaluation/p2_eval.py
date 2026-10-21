"""Đánh giá P2 so với đáp án sách mẫu (`*.truth.json`). Mỗi task P2 thêm phần của mình.

Chỉ tiêu gate xem docs/phases/P2/plan.md mục 7.
"""

import difflib
import re
from typing import Any

from dataminer.core.text_vi import nfc
from dataminer.evaluation.p1_eval import _line_key_map, _norm
from dataminer.structure.heading_levels import HeadingDecision
from dataminer.structure.toc import TocResult, match_key
from dataminer.structure.tree_builder import Node, check_invariants


def _ocr_title(ocr_line: str) -> str:
    """Tiêu đề OCR mong đợi của một dòng mục lục trong đáp án: bỏ chấm dẫn + số trang.

    Cố ý KHÔNG dùng `parse_entry_line` (hàm đang được đánh giá) - dòng mục lục của sách mẫu
    luôn có dạng "<tiêu đề> ...... <số>".
    """
    return " ".join(re.sub(r"\s*\.{3,}\s*\d+\s*$", "", nfc(ocr_line)).split())


def eval_toc(result: TocResult, truth: dict[str, Any]) -> dict[str, Any]:
    """G1: mục lục - đủ mục, tiêu đề, cấp, số trang in, trang PDF; trang mục lục đúng.

    Tiêu đề được so ở hai mức:
    - `title_exact`: khớp NGUYÊN VĂN OCR của đáp án (P2.1 không sửa chữ → phải 100%).
    - `title_clean`: khớp tiêu đề SẠCH qua `match_key` (không dấu, bỏ khoảng trắng) - chỉ để
      thông tin: lỗi OCR nhầm ký tự ("Cbương", "Viêrn") còn lại ở đây là việc P2.2 phải chịu.
    """
    toc_lines = [ln for ln in truth["lines"] if ln["role"] == "toc"]
    expected = truth["toc"]
    if len(toc_lines) != len(expected):  # pragma: no cover - đáp án hỏng
        raise ValueError("đáp án: số dòng role=toc khác số mục trong 'toc'")
    truth_pages = sorted({ln["pdf_page"] for ln in toc_lines})

    got = result.entries
    problems: list[str] = []
    clean_mismatch: list[str] = []
    for i, (want, ln) in enumerate(zip(expected, toc_lines, strict=True)):
        if i >= len(got):
            problems.append(f"thiếu mục #{i + 1} '{want['title']}'")
            continue
        e = got[i]
        ocr_title = _ocr_title(ln["ocr"])
        if e.title != ocr_title:
            problems.append(f"#{i + 1} tiêu đề '{e.title}' ≠ OCR '{ocr_title}'")
        for field, value in (
            ("level", want["level"]),
            ("printed_page", want["printed_page"]),
            ("pdf_page", want["pdf_page"]),
        ):
            if getattr(e, field) != value:
                problems.append(f"#{i + 1} '{e.title}': {field}={getattr(e, field)} ≠ {value}")
        if match_key(e.title) != match_key(want["title"]):
            clean_mismatch.append(f"'{e.title}' (sạch: '{want['title']}')")
    extra = [f"thừa mục '{e.title}'" for e in got[len(expected) :]]
    problems.extend(extra)
    if result.toc_pages != truth_pages:
        problems.append(f"trang mục lục {result.toc_pages} ≠ {truth_pages}")

    return {
        "G1_toc": {
            "truth": len(expected),
            "found": len(got),
            "toc_pages": result.toc_pages,
            "title_clean_match": len(expected) - len(clean_mismatch),
            "problems": problems,
            "ocr_damaged_titles": clean_mismatch,
            "pass": not problems and len(expected) > 0,
        }
    }


def eval_heading_levels(
    decisions: list[HeadingDecision], truth: dict[str, Any], pages: tuple[int, int]
) -> dict[str, Any]:
    """G2: cấp của mọi tiêu đề trong `pages` (trang PDF đã xử lý) đúng như đáp án.

    Ghép theo THỨ TỰ đọc; mỗi cặp phải cùng văn bản (khóa không dấu giống ≥ 0.8, chịu lỗi OCR
    còn sót) - lệch nghĩa là P1 sót/thừa tiêu đề và mọi cặp sau đó vô nghĩa → không đạt.
    """
    lo, hi = pages
    expected = [
        h for h in truth["headings"] if lo <= h["pdf_page"] <= hi and h["level"] != "toc_title"
    ]
    problems: list[str] = []
    correct = 0
    for i, want in enumerate(expected):
        if i >= len(decisions):
            problems.append(f"thiếu tiêu đề #{i + 1} '{want['text']}'")
            continue
        d = decisions[i]
        similar = difflib.SequenceMatcher(None, match_key(d.text), match_key(want["text"]))
        if similar.ratio() < 0.8:
            problems.append(f"#{i + 1} lệch thứ tự: '{d.text}' ↔ đáp án '{want['text']}'")
            break
        if d.level != want["level"]:
            problems.append(f"#{i + 1} '{d.text}': {d.level} ≠ {want['level']}")
        else:
            correct += 1
    problems.extend(f"thừa tiêu đề '{d.text}'" for d in decisions[len(expected) :])
    return {
        "G2_heading_levels": {
            "truth": len(expected),
            "found": len(decisions),
            "correct": correct,
            "by_source": {
                src: sum(d.source == src for d in decisions) for src in ("rules", "toc", "llm")
            },
            "problems": problems,
            "pass": not problems and len(expected) > 0,
        }
    }


def eval_tree(
    nodes: list[Node],
    blocks: list[Any],
    lines: list[Any],
    truth: dict[str, Any],
    pages: tuple[int, int],
) -> dict[str, Any]:
    """G3 (bệnh trong cây ↔ mục lục đáp án), G4 (mỗi dòng nội dung đúng nút), G6 (bất biến).

    G4 không so chữ tiêu đề (có thể còn lỗi OCR): "nút đúng" của một dòng nội dung = nút có
    tiêu đề là dòng tiêu đề GẦN NHẤT phía trên nó trong đáp án. Dòng đáp án ↔ dòng đọc được
    ghép bằng khóa (trang, văn bản OCR, lần xuất hiện) như P1.
    """
    lo, hi = pages
    # ---- G3
    diseases = [n for n in nodes if n.level == "disease"]
    want = [e for e in truth["toc"] if e["level"] == "disease" and lo <= e["pdf_page"] <= hi]
    g3_problems: list[str] = []
    used: set[str] = set()
    for e in want:
        scored = [
            (difflib.SequenceMatcher(None, match_key(n.title), match_key(e["title"])).ratio(), n)
            for n in diseases
            if n.id not in used
        ]
        score, node = max(scored, key=lambda x: x[0], default=(0.0, None))
        if node is None or score < 0.85:
            g3_problems.append(f"thiếu nút bệnh '{e['title']}'")
            continue
        used.add(node.id)
        if node.page_start != e["pdf_page"]:
            g3_problems.append(
                f"'{e['title']}': nút bắt đầu trang {node.page_start} ≠ {e['pdf_page']}"
            )
    g3_problems.extend(f"thừa nút bệnh '{n.title}'" for n in diseases if n.id not in used)

    # ---- G4
    key_of = _line_key_map(lines)
    line_of = {key: lid for lid, key in key_of.items()}
    block_of_line = {lid: b.id for b in blocks for lid in b.line_ids}
    node_of_block: dict[str, str] = {}
    heading_node: dict[str, str] = {}
    for n in nodes:
        for bid in n.block_ids:
            node_of_block[bid] = n.id
        if n.heading_block_id:
            heading_node[n.heading_block_id] = n.id
            node_of_block[n.heading_block_id] = n.id
    title_of = {n.id: " › ".join(n.path) for n in nodes}
    seen: dict[tuple[int, str], int] = {}
    current: str | None = None  # nút của tiêu đề đáp án gần nhất
    total = correct = 0
    g4_problems: list[str] = []
    for ln in truth["lines"]:
        if not lo <= ln["pdf_page"] <= hi or ln["role"] in ("header", "footer"):
            continue
        text = _norm(ln["ocr"])
        occ = seen.get((ln["pdf_page"], text), 0)
        seen[(ln["pdf_page"], text)] = occ + 1
        lid = line_of.get((ln["pdf_page"], text, occ))
        line_block = block_of_line.get(lid) if lid else None
        if ln["role"] == "heading":
            current = heading_node.get(line_block) if line_block else None
            if current is None:
                g4_problems.append(f"tiêu đề đáp án '{ln['text']}' không là tiêu đề nút nào")
            continue
        total += 1
        got = node_of_block.get(line_block) if line_block else None
        if got is not None and got == current:
            correct += 1
        elif len(g4_problems) < 20:
            where = title_of.get(got or "", "không nút nào")
            expected = title_of.get(current or "", "?")
            g4_problems.append(
                f"'{text[:50]}' (tr.PDF {ln['pdf_page']}): ở '{where}' ≠ '{expected}'"
            )
    ratio = correct / total if total else 0.0

    # ---- G6
    violations = check_invariants(nodes, blocks)
    return {
        "G3_diseases_vs_toc": {
            "truth": len(want),
            "found": len(diseases),
            "problems": g3_problems,
            "pass": not g3_problems and len(want) > 0,
        },
        "G4_content_in_node": {
            "lines": total,
            "correct": correct,
            "ratio": round(ratio, 4),
            "problems": g4_problems,
            "pass": total > 0 and ratio >= 0.99 and not any("tiêu đề" in p for p in g4_problems),
        },
        "G6_invariants": {
            "nodes": len(nodes),
            "violations": violations,
            "pass": not violations and len(nodes) > 1,
        },
    }


def eval_sections(
    nodes: list[Node], truth: dict[str, Any], pages: tuple[int, int]
) -> dict[str, Any]:
    """G5: `section_type` của mọi nút mục/mục con đúng như đáp án (≥ 95%), `other` < 5%.

    Ghép nút (thứ tự duyệt trước = thứ tự đọc) với tiêu đề mục của đáp án theo thứ tự, kiểm văn
    bản trùng (khóa không dấu giống ≥ 0.8) - lệch thì không đạt, không ghép mò.
    """
    lo, hi = pages
    expected = [
        h
        for h in truth["headings"]
        if lo <= h["pdf_page"] <= hi and h["level"] in ("section", "subsection")
    ]
    got = [n for n in nodes if n.level in ("section", "subsection")]
    problems: list[str] = []
    correct = 0
    misaligned = False
    for i, want in enumerate(expected):
        if i >= len(got):
            problems.append(f"thiếu mục #{i + 1} '{want['text']}'")
            misaligned = True
            continue
        n = got[i]
        similar = difflib.SequenceMatcher(None, match_key(n.title), match_key(want["text"]))
        if similar.ratio() < 0.8:
            problems.append(f"#{i + 1} lệch thứ tự: '{n.title}' ↔ đáp án '{want['text']}'")
            misaligned = True
            break
        if n.section_type == want["section_type"]:
            correct += 1
        else:
            problems.append(f"#{i + 1} '{n.title}': {n.section_type} ≠ {want['section_type']}")
    extra = [f"thừa mục '{n.title}'" for n in got[len(expected) :]]
    problems.extend(extra)
    accuracy = correct / len(expected) if expected else 0.0
    other = sum(n.section_type in (None, "other") for n in got) / len(got) if got else 1.0
    sources = [n.section_source or "chưa gán" for n in got]
    return {
        "G5_section_types": {
            "truth": len(expected),
            "found": len(got),
            "correct": correct,
            "accuracy": round(accuracy, 4),
            "other_ratio": round(other, 4),
            "by_source": {s: sources.count(s) for s in dict.fromkeys(sources)},
            "problems": problems,
            "pass": bool(expected)
            and accuracy >= 0.95
            and other < 0.05
            and not misaligned
            and not extra,
        }
    }


def all_pass(report: dict[str, Any]) -> bool:
    return all(item.get("pass") for item in report.values())
