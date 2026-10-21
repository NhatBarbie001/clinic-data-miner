"""Đánh giá P2 so với đáp án sách mẫu (`*.truth.json`). Mỗi task P2 thêm phần của mình.

Chỉ tiêu gate xem docs/phases/P2/plan.md mục 7.
"""

import difflib
import re
from typing import Any

from dataminer.core.text_vi import nfc
from dataminer.structure.heading_levels import HeadingDecision
from dataminer.structure.toc import TocResult, match_key


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


def all_pass(report: dict[str, Any]) -> bool:
    return all(item.get("pass") for item in report.values())
