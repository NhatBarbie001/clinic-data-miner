"""Đối chiếu kết quả `dm survey` với đáp án của sách mẫu → precision/recall có chỉ tiêu."""

import unicodedata
from collections import defaultdict
from typing import Any

from dataminer.core.text_vi import has_vietnamese_marks
from dataminer.ingest.survey import RE_MISSING_SPACE, SurveyResult

# Lỗi OCR mà khảo sát (không từ điển) có thể phát hiện, và chỉ tiêu recall.
DETECTABLE_TARGETS = {
    "digit_confusion": 1.0,
    "nfd_line": 1.0,
    "merge_words": 1.0,
    "char_confusion": 0.5,
}
UNDETECTABLE = ("drop_diacritics", "wrong_tone")  # tạo ra từ hợp lệ → cần ngữ cảnh (P1)


def _norm(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).split())


def _pr(found: set[Any], truth: set[Any]) -> dict[str, Any]:
    hit = found & truth
    return {
        "truth": len(truth),
        "found": len(found),
        "recall": round(len(hit) / len(truth), 4) if truth else 1.0,
        "precision": round(len(hit) / len(found), 4) if found else 1.0,
        "missed": sorted(truth - found),
        "extra": sorted(found - truth),
    }


def _detectable(err: dict[str, Any]) -> bool:
    """Lỗi có thể phát hiện không cần từ điển? Dính hai từ KHÔNG dấu ("acidfolic") thì không."""
    if err["kind"] == "merge_words":
        merged = err["corrupted"]
        return has_vietnamese_marks(merged) or bool(RE_MISSING_SPACE.search(merged))
    return True


def _error_detected(err: dict[str, Any], signals: list[dict[str, Any]]) -> bool:
    on_page = [s for s in signals if s["page"] == err["pdf_page"]]
    if err["kind"] == "nfd_line":
        return any(s["kind"] == "nfd_line" and _norm(s["line"]) for s in on_page)
    corrupted = _norm(err["corrupted"])
    return any(
        s["token"] and (_norm(s["token"]) in corrupted or corrupted in _norm(s["token"]))
        for s in on_page
    )


def check_survey(result: SurveyResult, truth: dict[str, Any]) -> dict[str, Any]:
    lines = truth["lines"]
    checks: dict[str, Any] = {}

    hf_truth = {
        (ln["pdf_page"], _norm(ln["ocr"])) for ln in lines if ln["role"] in ("header", "footer")
    }
    hf_found = {(i["page"], _norm(i["text"])) for i in result.header_footer["instances"]}
    checks["header_footer"] = {**_pr(hf_found, hf_truth), "target": "recall=1, precision=1"}
    checks["header_footer"]["pass"] = (
        checks["header_footer"]["recall"] == 1.0 and checks["header_footer"]["precision"] == 1.0
    )

    head_truth = {(h["pdf_page"], _norm(h["ocr"])) for h in truth["headings"]}
    head_found = {(c["page"], _norm(c["text"])) for c in result.headings["candidates"]}
    checks["headings"] = {**_pr(head_found, head_truth), "target": "recall=1"}
    checks["headings"]["pass"] = checks["headings"]["recall"] == 1.0

    est, real = result.stats["body_font_size"], truth["body_size"]
    checks["body_font_size"] = {
        "estimated": est,
        "truth": real,
        "target": "sai số ≤ 0.5pt",
        "pass": abs(est - real) <= 0.5,
    }

    empty_truth = [p["pdf_page"] for p in truth["pages"] if not p["has_text"]]
    checks["pages_without_text"] = {
        "found": result.stats["pages_without_text"],
        "truth": empty_truth,
        "pass": result.stats["pages_without_text"] == empty_truth,
    }

    printed_found = {
        i["page"]: i["printed_page"]
        for i in result.header_footer["instances"]
        if i["kind"] == "page_number"
    }
    printed_truth = {
        p["pdf_page"]: p["printed_page"] for p in truth["pages"] if p["printed_page"] is not None
    }
    checks["printed_page_numbers"] = {
        "found": printed_found,
        "truth": printed_truth,
        "pass": printed_found == printed_truth,
    }

    checks["toc_entries"] = {
        "found": len(result.headings["toc_entries"]),
        "truth": len(truth["toc"]),
        "pass": len(result.headings["toc_entries"]) == len(truth["toc"]),
    }

    # [phát hiện, tổng, phát hiện trong số có-thể-phát-hiện, số có-thể-phát-hiện]
    per_kind: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for err in truth["ocr_errors"]:
        found = int(_error_detected(err, result.signals))
        counts = per_kind[err["kind"]]
        counts[0] += found
        counts[1] += 1
        if _detectable(err):
            counts[2] += found
            counts[3] += 1
    ocr: dict[str, Any] = {}
    for kind, (detected, total, hit_d, total_d) in sorted(per_kind.items()):
        recall = round(hit_d / total_d, 4) if total_d else 1.0
        target = DETECTABLE_TARGETS.get(kind)
        ocr[kind] = {
            "detected": detected,
            "total": total,
            "undetectable": total - total_d,
            "recall": recall,
            "target": target if target is not None else "không áp dụng (cần P1)",
            "pass": True if target is None else recall >= target,
        }
    checks["ocr_errors"] = ocr

    # Tín hiệu không ứng với lỗi nào đã cài = báo động giả.
    def matches_any(sig: dict[str, Any]) -> bool:
        for err in truth["ocr_errors"]:
            if err["pdf_page"] != sig["page"]:
                continue
            if sig["kind"] == "nfd_line" and err["kind"] == "nfd_line":
                return True
            if sig["token"] and (
                _norm(sig["token"]) in _norm(err["corrupted"])
                or _norm(err["corrupted"]) in _norm(sig["token"])
            ):
                return True
        return False

    false_alarms = [s for s in result.signals if not matches_any(s)]
    checks["ocr_signal_precision"] = {
        "signals": len(result.signals),
        "false_alarms": len(false_alarms),
        "precision": round(1 - len(false_alarms) / len(result.signals), 4) if result.signals else 1,
        "examples": [f"tr.{s['page']} {s['kind']} `{s['token']}`" for s in false_alarms[:10]],
        "pass": not false_alarms,
    }

    gated = [checks[k]["pass"] for k in checks if k != "ocr_errors"]
    gated += [v["pass"] for v in ocr.values()]
    checks["all_pass"] = all(gated)
    return checks


def format_check(checks: dict[str, Any]) -> str:
    def mark(ok: bool) -> str:
        return "✓" if ok else "✗"

    out = ["# Đối chiếu khảo sát với đáp án sách mẫu", ""]
    for key in ("header_footer", "headings"):
        c = checks[key]
        out.append(
            f"{mark(c['pass'])} {key}: recall {c['recall']:.0%} · precision "
            f"{c['precision']:.0%} ({c['found']} tìm thấy / {c['truth']} đáp án) "
            f"- chỉ tiêu {c['target']}"
        )
        for page, text in c["missed"]:
            out.append(f"    BỎ SÓT tr.{page}: {text}")
        for page, text in c["extra"]:
            out.append(f"    THỪA   tr.{page}: {text}")
    b = checks["body_font_size"]
    out.append(
        f"{mark(b['pass'])} cỡ chữ thân bài: ước lượng {b['estimated']} / đáp án "
        f"{b['truth']} - chỉ tiêu {b['target']}"
    )
    for key in ("pages_without_text", "printed_page_numbers", "toc_entries"):
        c = checks[key]
        out.append(f"{mark(c['pass'])} {key}: tìm thấy {c['found']} / đáp án {c['truth']}")
    out.append("")
    out.append("Lỗi OCR đã cài (recall theo loại):")
    out.append("  (recall tính trên các lỗi CÓ THỂ phát hiện không cần từ điển)")
    for kind, c in checks["ocr_errors"].items():
        skipped = f", {c['undetectable']} không thể phát hiện" if c["undetectable"] else ""
        out.append(
            f"  {mark(c['pass'])} {kind:<16} {c['detected']}/{c['total']}{skipped} "
            f"→ recall {c['recall']:.0%} - chỉ tiêu {c['target']}"
        )
    p = checks["ocr_signal_precision"]
    out.append(
        f"{mark(p['pass'])} báo động giả: {p['false_alarms']}/{p['signals']} tín hiệu "
        f"(precision {p['precision']:.0%})"
    )
    out.extend(f"    {e}" for e in p["examples"])
    out.append("")
    out.append(f"KẾT LUẬN: {'ĐẠT mọi chỉ tiêu' if checks['all_pass'] else 'CHƯA ĐẠT'}")
    return "\n".join(out)
