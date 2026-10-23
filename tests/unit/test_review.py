"""P1.5 - Hàng đợi duyệt tay. Số (#) khớp mục 5 của docs/phases/P1/P1.5_plan.md.

Block "đã sửa" dựng tất định bằng LLM hoàn hảo (oracle) + guard - giống kết quả DeepSeek thật
ở chỗ quan trọng: đúng 2 mục số liệu (5OO trong gạch đầu dòng, "l" trong ô bảng).
"""

import csv
from pathlib import Path

import pytest

from dataminer.books.book01.rules import build_blocks
from dataminer.core.config import FixCfg
from dataminer.core.prompts import Prompt
from dataminer.devtools.auto_review import REVIEWER, fill_from_truth
from dataminer.devtools.oracle_fix import oracle_outputs
from dataminer.devtools.sample_book import SampleBook
from dataminer.evaluation.truth.p1_eval import eval_ocr
from dataminer.model.block import Block, Fix
from dataminer.model.line import Line
from dataminer.ocrfix.fixer import OCRFixer
from dataminer.ocrfix.guards import GlossaryIndex
from dataminer.ocrfix.review import (
    ReviewError,
    apply_decisions,
    build_queue,
    export_csv,
    import_csv,
    save_decisions,
)
from dataminer.pdf.furniture import strip_furniture
from dataminer.pdf.reader import body_font_size, read_lines
from tests.conftest import SampleBookFor


@pytest.fixture(scope="module")
def book(sample_book_for: SampleBookFor) -> SampleBook:
    return sample_book_for(7)


@pytest.fixture(scope="module")
def fixed(book: SampleBook) -> tuple[list[Block], list[Line]]:
    lines = read_lines(book.pdf_path, pages=(4, 9))
    body = body_font_size(lines)
    fr = strip_furniture(lines, body, pdf_pages=list(range(4, 10)))
    blocks = build_blocks(fr.content, body, printed={p.page: p.printed_page for p in fr.pages})
    prompt = Prompt(id="p", version="v1", text="x")
    fixer = OCRFixer(None, prompt, GlossaryIndex(["mg", "g"]), FixCfg())  # type: ignore[arg-type]
    return fixer.apply(blocks, oracle_outputs(blocks, fr.content, book.truth)), fr.content


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def exported(tmp_path: Path, blocks: list[Block]) -> tuple[list, list[dict[str, str]]]:  # type: ignore[type-arg]
    queue = build_queue(blocks)
    export_csv(queue, tmp_path / "q.csv")
    with (tmp_path / "q.csv").open(encoding="utf-8-sig", newline="") as fh:
        return queue, list(csv.DictReader(fh))


def decide(tmp_path: Path, blocks: list[Block], fill: dict[str, tuple[str, str]]):  # type: ignore[no-untyped-def]
    """fill: {current: (decision, edited_value)} → (quyết định, block sau áp, báo cáo)."""
    queue, rows = exported(tmp_path, blocks)
    for row in rows:
        if row["current"] in fill:
            row["decision"], row["edited_value"] = fill[row["current"]]
    write_rows(tmp_path / "d.csv", rows)
    decisions = import_csv(tmp_path / "d.csv", queue)
    out, report = apply_decisions(blocks, decisions)
    return decisions, out, report


# ---------------------------------------------------------------- hàng đợi


def test_01_queue_has_both_dose_items(fixed: tuple[list[Block], list[Line]]) -> None:
    queue = build_queue(fixed[0])
    assert [(i.priority, i.current, i.suggestion, i.cell) for i in queue] == [
        ("1-SỐ LIỆU", "5OO", "500", None),
        ("1-SỐ LIỆU", "l", "1", "r2c1"),
    ]
    assert "«5OO»" in queue[0].context
    assert queue[0].printed_page == 4


def test_02_csv_utf8_bom_roundtrip(tmp_path: Path, fixed: tuple[list[Block], list[Line]]) -> None:
    queue, rows = exported(tmp_path, fixed[0])
    assert (tmp_path / "q.csv").read_bytes().startswith(b"\xef\xbb\xbf")  # BOM cho Excel
    assert rows[0]["priority"] == "1-SỐ LIỆU"
    assert "Paracetamol" in rows[0]["context"]
    assert rows[0]["decision"] == ""
    assert len(rows) == len(queue)


def test_09_item_ids_stable(fixed: tuple[list[Block], list[Line]]) -> None:
    assert [i.item_id for i in build_queue(fixed[0])] == [i.item_id for i in build_queue(fixed[0])]


# ---------------------------------------------------------------- quyết định


def test_03_accept(tmp_path: Path, fixed: tuple[list[Block], list[Line]]) -> None:
    _, out, report = decide(tmp_path, fixed[0], {"5OO": ("accept", "")})
    assert report.applied == 1
    block = next(b for b in out if "Paracetamol" in b.text)
    assert "Paracetamol 500 mg" in block.text
    assert "dose_suspect" not in block.flags
    assert "reviewed" in block.flags
    assert block.fixes[-1] == Fix(
        position=1, before="5OO", after="500", accepted=True, rule="review"
    )
    assert block.reviews[0].decision == "accept"
    assert len(build_queue(out)) == 1  # còn mục "l g"


def test_04_keep(tmp_path: Path, fixed: tuple[list[Block], list[Line]]) -> None:
    _, out, _ = decide(tmp_path, fixed[0], {"l": ("keep", "")})
    table = next(b for b in out if b.kind == "table")
    assert table.rows is not None
    assert table.rows[2][1] == "l g"  # giữ nguyên theo quyết định
    assert "dose_suspect" not in table.flags
    assert table.reviews[0].decision == "keep"
    assert not any(f.rule == "review" for f in table.fixes)  # không đổi gì → không có Fix


def test_05_edit_number_in_table_cell(
    tmp_path: Path, fixed: tuple[list[Block], list[Line]]
) -> None:
    _, out, _ = decide(tmp_path, fixed[0], {"l": ("edit", "1")})
    table = next(b for b in out if b.kind == "table")
    assert table.rows is not None
    assert table.rows[2][1] == "1 g"
    assert "Amoxicilin | 1 g" in table.text


def test_05b_number_item_rejects_non_number(
    tmp_path: Path, fixed: tuple[list[Block], list[Line]]
) -> None:
    with pytest.raises(ReviewError) as info:
        decide(tmp_path, fixed[0], {"5OO": ("edit", "5O0")})
    assert "dòng 2: mục SỐ LIỆU phải là số" in str(info.value)


def test_06_invalid_rows_reported_with_line_numbers(
    tmp_path: Path, fixed: tuple[list[Block], list[Line]]
) -> None:
    with pytest.raises(ReviewError) as info:
        decide(tmp_path, fixed[0], {"5OO": ("ok", ""), "l": ("edit", "")})
    msg = str(info.value)
    assert "2 dòng không hợp lệ" in msg
    assert "dòng 2: decision 'ok' không hợp lệ" in msg
    assert "dòng 3: 'edit' nhưng edited_value trống" in msg


def test_06b_blank_decision_means_pending(
    tmp_path: Path, fixed: tuple[list[Block], list[Line]]
) -> None:
    decisions, out, _ = decide(tmp_path, fixed[0], {})
    assert decisions == []
    assert len(build_queue(out)) == 2


def test_06c_unknown_item_id(tmp_path: Path, fixed: tuple[list[Block], list[Line]]) -> None:
    queue, rows = exported(tmp_path, fixed[0])
    rows[0]["item_id"], rows[0]["decision"] = "rv_khong_co", "keep"
    write_rows(tmp_path / "d.csv", rows)
    with pytest.raises(ReviewError, match="không có trong hàng đợi"):
        import_csv(tmp_path / "d.csv", queue)


# ---------------------------------------------------------------- bền, stale


def test_07_decisions_persist_across_reruns(
    tmp_path: Path, fixed: tuple[list[Block], list[Line]]
) -> None:
    decisions, out1, _ = decide(tmp_path, fixed[0], {"5OO": ("accept", ""), "l": ("edit", "1")})
    store = tmp_path / "decisions.jsonl"
    save_decisions(store, decisions)
    # "chạy lại P1.4" → block đã sửa mới tinh (không có reviews) → áp lại từ file
    rerun = [b.model_copy(deep=True) for b in fixed[0]]
    out2, report = apply_decisions(rerun, save_decisions(store, []))
    assert report.applied == 2
    assert [b.text for b in out2] == [b.text for b in out1]
    assert build_queue(out2) == []


def test_07b_later_decision_wins(tmp_path: Path, fixed: tuple[list[Block], list[Line]]) -> None:
    store = tmp_path / "decisions.jsonl"
    first, _, _ = decide(tmp_path, fixed[0], {"5OO": ("keep", "")})
    save_decisions(store, first)
    second, _, _ = decide(tmp_path, fixed[0], {"5OO": ("accept", "")})
    merged = save_decisions(store, second)
    assert [d.decision for d in merged] == ["accept"]


def test_08_stale_decision(tmp_path: Path, fixed: tuple[list[Block], list[Line]]) -> None:
    decisions, _, _ = decide(tmp_path, fixed[0], {"5OO": ("accept", "")})
    changed = [b.model_copy(deep=True) for b in fixed[0]]
    for b in changed:
        b.text = b.text.replace("5OO", "550")  # văn bản đã đổi: token cần duyệt không còn
    out, report = apply_decisions(changed, decisions)
    assert report.stale == [decisions[0].id]
    assert report.applied == 0
    assert not any(b.reviews for b in out)


# ---------------------------------------------------------------- mục loại 2, 3


def _block(text: str, **kw) -> Block:  # type: ignore[no-untyped-def]
    return Block(
        id="b1",
        kind="paragraph",
        text=text,
        text_rules=text,
        page_start=5,
        page_end=5,
        line_ids=["l1"],
        bbox=(0, 0, 1, 1),
        x0=48,
        font_size=10.5,
        **kw,
    )


def test_rejected_fix_and_ocr_suspect_items() -> None:
    block = _block(
        "bệnh nhân đau đầu, viêrn khớp",
        fixes=[Fix(position=2, before="đau", after="nhức", accepted=False, rule="G-sim")],
        flags=["ocr_suspect", "fix_partially_rejected"],
    )
    queue = build_queue([block])
    assert [(i.priority, i.current, i.suggestion) for i in queue] == [
        ("2-BỊ TỪ CHỐI", "đau", "nhức"),
        ("3-NGHI LỖI", "viêrn", None),
    ]
    assert "G-sim" in queue[0].reason


def test_fix_failed_whole_block_edit(tmp_path: Path) -> None:
    block = _block("benh nhan bi sot", flags=["fix_failed"])
    _, out, report = decide(tmp_path, [block], {"benh nhan bi sot": ("edit", "bệnh nhân bị sốt")})
    assert report.applied == 1
    assert out[0].text == "bệnh nhân bị sốt"
    assert "fix_failed" not in out[0].flags


# ---------------------------------------------------------------- #10 auto-truth + G8


def test_10_auto_truth_review_resolves_all_numbers(
    tmp_path: Path, book: SampleBook, fixed: tuple[list[Block], list[Line]]
) -> None:
    blocks, lines = fixed
    queue = build_queue(blocks)
    export_csv(queue, tmp_path / "q.csv")
    assert fill_from_truth(tmp_path / "q.csv", tmp_path / "d.csv", blocks, lines, book.truth) == 2
    decisions = import_csv(tmp_path / "d.csv", queue)
    assert {(d.decision, d.value, d.reviewer) for d in decisions} == {
        ("accept", "500", REVIEWER),
        ("accept", "1", REVIEWER),
    }
    out, _ = apply_decisions(blocks, decisions)
    g8 = eval_ocr(out, lines, book.truth)["G8_numbers"]
    assert g8["pass"], g8
    assert all(d["fixed_by_review"] for d in g8["dose_errors"])
    assert eval_ocr(out, lines, book.truth)["G5_wer"]["after"] < 0.005


def test_g8_fails_when_reviewer_enters_wrong_number(
    tmp_path: Path, book: SampleBook, fixed: tuple[list[Block], list[Line]]
) -> None:
    """Người duyệt gõ sai số (50 thay vì 500) → G8 phải KHÔNG ĐẠT."""
    blocks, lines = fixed
    _, out, _ = decide(tmp_path, blocks, {"5OO": ("edit", "50"), "l": ("accept", "")})
    assert not eval_ocr(out, lines, book.truth)["G8_numbers"]["pass"]


def test_accept_without_suggestion_rejected(tmp_path: Path) -> None:
    """Mục 'nghi lỗi' không có gợi ý → 'accept' vô nghĩa, phải báo lỗi (không được ghi None)."""
    block = _block("viêrn khớp dạng thấp", flags=["ocr_suspect"])
    with pytest.raises(ReviewError, match="không có gợi ý"):
        decide(tmp_path, [block], {"viêrn": ("accept", "")})
