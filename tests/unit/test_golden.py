"""P2.5 - Bộ câu hỏi chuẩn v1 (EV.1). Số (#) khớp mục 5 của docs/phases/P2/P2.5_plan.md.

Hai nguồn cây dùng ở đây:
- cây đã commit `samples/P2.4/nodes.jsonl` (= cây của data/ khi sinh golden v1) - kiểm file golden
  đã commit;
- cây dựng từ sách mẫu với "P1 hoàn hảo" (văn bản block = văn bản sạch của đáp án) - đối chứng
  dương; và với P1 CHỈ quy tắc (còn lỗi OCR) - trích dẫn sạch phải KHÔNG khớp nút còn lỗi.
"""

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dataminer.books.book01.golden import clean_texts, draft_golden
from dataminer.books.book01.rules import build_tree, classify_headings
from dataminer.cli import app
from dataminer.core.io import read_jsonl, write_jsonl
from dataminer.evaluation.golden import GoldenItem, Source, items_of, quote_status, validate_golden
from dataminer.model.block import Block
from dataminer.model.line import Line
from dataminer.model.tree import Node
from dataminer.structure.section_mapper import load_section_map, map_sections
from tests.conftest import SampleBookFor
from tests.unit.llm_fakes import ROOT, make_settings
from tests.unit.test_tree_builder import pipeline

GOLDEN = ROOT / "eval" / "book01" / "golden_qa_v1.jsonl"
REF_NODES = ROOT / "samples" / "P2.4" / "nodes.jsonl"
MAPPING = load_section_map(ROOT / "configs" / "books" / "book01" / "section_map.yaml")
runner = CliRunner()


def oracle_blocks(blocks: list[Block], lines: list[Line], truth: dict) -> list[Block]:
    """ "P1 hoàn hảo": văn bản block = văn bản sạch của đáp án (đối chứng dương)."""
    from dataminer.evaluation.truth.p1_eval import _line_key_map, _norm

    key_of = _line_key_map(lines)
    clean: dict[tuple[int, str, int], str] = {}
    seen: dict[tuple[int, str], int] = {}
    for ln in truth["lines"]:
        k = (ln["pdf_page"], _norm(ln["ocr"]))
        occ = seen.get(k, 0)
        seen[k] = occ + 1
        clean[(k[0], k[1], occ)] = ln["text"]
    tables = {t["pdf_page"]: t["rows"] for t in truth["tables"]}
    out = []
    for b in blocks:
        if b.kind == "table":
            rows = tables[b.page_start]
            text = "\n".join(" | ".join(r) for r in rows)
            out.append(b.model_copy(update={"text": text, "rows": rows}))
            continue
        text = " ".join(clean[key_of[lid]] for lid in b.line_ids)
        if b.kind == "list_item" and text.startswith("- "):
            text = text[2:]
        out.append(b.model_copy(update={"text": text}))
    return out


def built_tree(
    sample_book_for: SampleBookFor, seed: int, *, oracle: bool
) -> tuple[list[Node], list[Block], list[Line], dict]:
    book = sample_book_for(seed)
    blocks, lines, _, toc = pipeline(book.pdf_path)
    if oracle:
        blocks = oracle_blocks(blocks, lines, book.truth)
    decisions = classify_headings(blocks, toc).decisions
    nodes = build_tree(blocks, decisions, book_id="book01", toc=toc).nodes
    map_sections(nodes, MAPPING)
    return nodes, blocks, lines, book.truth


@pytest.fixture(scope="module")
def committed() -> tuple[list[GoldenItem], list[Node]]:
    return list(read_jsonl(GOLDEN, GoldenItem)), list(read_jsonl(REF_NODES, Node))


@pytest.fixture(scope="module")
def oracle(sample_book_for: SampleBookFor) -> tuple[list[Node], list[GoldenItem]]:
    nodes, blocks, lines, truth = built_tree(sample_book_for, 7, oracle=True)
    return nodes, draft_golden(nodes, clean_texts(nodes, blocks, lines, truth))


# ---------------------------------------------------------------- #1-2 bộ v1 đã commit


def test_01_committed_v1_distribution(committed: tuple[list[GoldenItem], list[Node]]) -> None:
    items, _ = committed
    assert len(items) == 30
    assert [sum(i.qtype == t for i in items) for t in ("specific", "list", "refusal")] == [20, 5, 5]
    assert len({i.id for i in items}) == 30
    numeric = [i for i in items if i.check.get("rule") == "numbers_in_node"]
    assert len(numeric) >= 2  # câu số liệu / liều
    assert any("BẢNG" in (i.notes or "") for i in numeric)  # câu cần đọc bảng
    diseases = {i.disease for i in items if i.qtype == "specific"}
    assert diseases == {"Viêm khớp dạng thấp", "Thoái hóa khớp gối", "Viêm loét dạ dày tá tràng"}
    assert {i.section_type for i in items if i.qtype == "specific"} >= {
        "definition", "cause", "symptom", "diagnosis", "treatment", "prevention",
    }  # fmt: skip
    assert all(i.created_by == "auto (sách mẫu)" and i.reviewed_by for i in items)


def test_02_committed_v1_valid_against_committed_tree(
    committed: tuple[list[GoldenItem], list[Node]],
) -> None:
    items, nodes = committed
    report = validate_golden(items, nodes)
    assert report.ok, report.errors
    assert report.warnings == []  # mọi trích dẫn khớp NGUYÊN VĂN (bỏ qua khoảng trắng)


def test_02b_oracle_tree_draft_is_valid_and_matches_committed(
    oracle: tuple[list[Node], list[GoldenItem]], committed: tuple[list[GoldenItem], list[Node]]
) -> None:
    nodes, items = oracle
    report = validate_golden(items, nodes)
    assert report.ok and report.warnings == [], report.errors
    # cùng câu hỏi, đáp án, ý - chỉ node_id có thể khác (cây pilot có tiêu đề "TRIỆU CHUNG")
    strip = [(i.question, i.answer, i.answer_points) for i in items]
    assert strip == [(i.question, i.answer, i.answer_points) for i in committed[0]]


def test_02c_unfixed_ocr_tree_is_rejected(sample_book_for: SampleBookFor) -> None:
    """P1 chỉ quy tắc (còn 'viêrn', 'tbuốc'…): trích dẫn SẠCH không khớp nút → G7 báo lỗi."""
    nodes, blocks, lines, truth = built_tree(sample_book_for, 7, oracle=False)
    items = draft_golden(nodes, clean_texts(nodes, blocks, lines, truth))
    report = validate_golden(items, nodes)
    assert not report.ok
    assert any("trích dẫn không có trong nút" in e for e in report.errors)


# ---------------------------------------------------------------- #3-4 từ chối, liệt kê


def test_03_refusal_items(committed: tuple[list[GoldenItem], list[Node]]) -> None:
    items, nodes = committed
    refusals = [i for i in items if i.qtype == "refusal"]
    assert all(not i.sources and not i.answer_points and i.check["keywords"] for i in refusals)
    leaky = refusals[0].model_copy(
        update={"check": {"rule": "absent", "keywords": ["loét dạ dày"]}}
    )
    report = validate_golden([*items[:-5], leaky, *refusals[1:]], nodes)
    assert any("CÓ trong sách - không phải câu từ chối" in e for e in report.errors)
    sourced = refusals[0].model_copy(update={"sources": items[0].sources})
    report = validate_golden([*items[:-5], sourced, *refusals[1:]], nodes)
    assert any("câu từ chối không được có nguồn" in e for e in report.errors)
    no_keywords = refusals[0].model_copy(update={"check": {"rule": "absent", "keywords": []}})
    report = validate_golden([*items[:-5], no_keywords, *refusals[1:]], nodes)
    assert any("thiếu từ khóa để tự kiểm" in e for e in report.errors)


def test_04_list_answers_recomputed_from_tree(
    committed: tuple[list[GoldenItem], list[Node]],
) -> None:
    items, nodes = committed
    nsaid = next(i for i in items if "chống viêm không steroid" in i.question)
    assert nsaid.answer_points == ["Viêm khớp dạng thấp", "Thoái hóa khớp gối"]
    assert "Viêm loét dạ dày tá tràng (cause)" in (nsaid.notes or "")  # bẫy ngữ nghĩa
    smoking = next(i for i in items if "thuốc lá" in i.question)
    assert smoking.answer_points == ["Viêm khớp dạng thấp", "Viêm loét dạ dày tá tràng"]

    wrong = nsaid.model_copy(
        update={"answer_points": [*nsaid.answer_points, "Viêm loét dạ dày tá tràng"]}
    )
    errors = validate_golden([wrong if i is nsaid else i for i in items], nodes).errors
    assert any("≠ tính lại từ cây" in e for e in errors)
    complications = next(i for i in items if "biến chứng" in i.question)
    short = complications.model_copy(update={"answer_points": complications.answer_points[:2]})
    errors = validate_golden([short if i is complications else i for i in items], nodes).errors
    assert any("ý bắt buộc khác nội dung nút (2 ý ↔ nút có 3 ý)" in e for e in errors)


# ---------------------------------------------------------------- #5-7 kiểm tra phát hiện lỗi


def test_05_near_duplicate_questions(committed: tuple[list[GoldenItem], list[Node]]) -> None:
    items, nodes = committed
    dup = items[0].model_copy(update={"question": items[0].question.replace("?", " ?"), "id": "x"})
    errors = validate_golden([*items, dup], nodes).errors
    assert any("câu gần trùng" in e for e in errors)
    assert any("số câu 'specific' = 21, cần 20" in e for e in errors)


def test_06_validate_detects_broken_sources(
    committed: tuple[list[GoldenItem], list[Node]],
) -> None:
    items, nodes = committed
    first = items[0]
    src = first.sources[0]
    cases = {
        "không tồn tại (cây đã đổi?)": Source(
            node_id="nd_khong_co", path=src.path, quote=src.quote
        ),
        "path": Source(node_id=src.node_id, path=["Sai"], quote=src.quote),
        "trích dẫn không có trong nút": Source(
            node_id=src.node_id, path=src.path, quote="Câu này không có trong sách."
        ),
    }
    for message, broken in cases.items():
        item = first.model_copy(update={"sources": [broken]})
        errors = validate_golden([item, *items[1:]], nodes).errors
        assert any(message in e for e in errors), (message, errors)
    empty = first.model_copy(update={"sources": [], "answer_points": []})
    assert any("thiếu nguồn" in e for e in validate_golden([empty, *items[1:]], nodes).errors)
    blank = first.model_copy(update={"answer": " "})
    assert any("thiếu câu hỏi hoặc đáp án" in e for e in validate_golden([blank], nodes).errors)
    odd = first.model_copy(update={"check": {"rule": "doan_mo"}})
    assert any("không hợp lệ" in e for e in validate_golden([odd, *items[1:]], nodes).errors)


def test_07_numbers_must_be_reviewed_values() -> None:
    node_text = (
        "- Paracetamol 500 mg mỗi lần, không quá 3 g mỗi ngày.\nAmoxicilin | 1 g | 2 | 14 ngày"
    )
    assert quote_status("Paracetamol 500 mg mỗi lần", node_text) == "exact"
    assert quote_status("Paracetamol 5OO mg mỗi lần", node_text) == "missing"  # OCR chưa duyệt
    assert quote_status("Amoxicilin | l g |", node_text) == "missing"
    assert quote_status("Paracetamol  500 mg\nmỗi lần", node_text) == "exact"  # khoảng trắng
    # nút còn lỗi DẤU (P1 sửa nhầm "kinh điển" → "kinh diễn"): chấp nhận nhưng cảnh báo
    assert quote_status("DMARD kinh điển", "khi đáp ứng kém với DMARD kinh diễn.") == "loose"
    # bỏ dấu khớp nhưng SỐ khác → vẫn là thiếu
    assert quote_status("liều 7,5 mg", "lieu 75 mg") == "missing"


def test_07b_numbers_in_node_rule(committed: tuple[list[GoldenItem], list[Node]]) -> None:
    items, nodes = committed
    dose = next(i for i in items if "paracetamol" in i.question)
    assert dose.answer_points == ["500 mg mỗi lần", "không quá 3 g mỗi ngày"]
    table = next(i for i in items if "Helicobacter" in i.question)
    assert table.answer_points[:3] == ["Omeprazol 20 mg", "Amoxicilin 1 g", "Clarithromycin 500 mg"]
    wrong = dose.model_copy(update={"answer_points": ["5OO mg mỗi lần", "không quá 3 g mỗi ngày"]})
    errors = validate_golden([wrong if i is dose else i for i in items], nodes).errors
    assert any("số liệu ['5'] không có trong nút" in e for e in errors)


def test_items_of_splits_bullets_sentences_skips_tables() -> None:
    text = (
        "- Ngừng thuốc gây loét.\n- Omeprazol 20 mg.\nBảng 2.1. Phác đồ 3 thuốc\n"
        "Thuốc | Liều\nOmeprazol | 20 mg"
    )
    assert items_of(text) == ["Ngừng thuốc gây loét.", "Omeprazol 20 mg."]
    assert items_of("Bệnh hay gặp. Tuổi 30 đến 50; nữ nhiều hơn.") == [
        "Bệnh hay gặp.",
        "Tuổi 30 đến 50; nữ nhiều hơn.",
    ]
    assert items_of("Tiêu chuẩn ACR/EULAR 2010. Đạt 6/10 điểm.") == [
        "Tiêu chuẩn ACR/EULAR 2010.",
        "Đạt 6/10 điểm.",
    ]


# ---------------------------------------------------------------- #8 xác định


def test_08_deterministic(
    oracle: tuple[list[Node], list[GoldenItem]], sample_book_for: SampleBookFor
) -> None:
    _, items = oracle
    again_nodes, blocks, lines, truth = built_tree(sample_book_for, 7, oracle=True)
    again = draft_golden(again_nodes, clean_texts(again_nodes, blocks, lines, truth))
    assert [i.model_dump() for i in again] == [i.model_dump() for i in items]


# ---------------------------------------------------------------- CLI


def test_cli_golden(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    book = sample_book_for(7)
    make_settings(tmp_path)
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    shutil.copytree(ROOT / "prompts", tmp_path / "prompts")
    raw = tmp_path / "data" / "books" / "book01" / "raw"
    raw.mkdir(parents=True)
    shutil.copy(book.pdf_path, raw / "book01.pdf")
    shutil.copy(book.truth_path, raw / "book01.truth.json")
    blocks, lines, _, _ = pipeline(book.pdf_path)
    write_jsonl(
        tmp_path / "data" / "books" / "book01" / "p1_clean" / "blocks.jsonl",
        oracle_blocks(blocks, lines, book.truth),
    )
    write_jsonl(tmp_path / "data" / "books" / "book01" / "p1_clean" / "content_lines.jsonl", lines)
    root = ["--root", str(tmp_path)]

    assert "dm p2 tree" in runner.invoke(app, ["p2", "golden", *root]).output
    for cmd in (["headings", "--no-llm"], ["tree"]):
        assert runner.invoke(app, ["p2", *cmd, *root]).exit_code == 0
    no_types = runner.invoke(app, ["p2", "golden", *root])
    assert no_types.exit_code == 1 and "sections map" in no_types.output
    assert runner.invoke(app, ["p2", "sections", "map", *root, "--no-llm"]).exit_code == 0
    assert runner.invoke(app, ["p2", "golden", *root, "--check"]).exit_code == 1  # chưa có file

    first = runner.invoke(app, ["p2", "golden", *root])
    assert first.exit_code == 0, first.output
    assert "30 câu · cụ thể 20 · liệt kê 5 · từ chối 5" in first.output
    golden = tmp_path / "eval" / "book01" / "golden_qa_v1.jsonl"

    # cùng nội dung với bản đã commit; chỉ nguồn của "Triệu chứng" (THKG) khác: cây commit có
    # tiêu đề còn lỗi OCR "TRIỆU CHUNG" (path/ID khác) - xem giới hạn "ID phụ thuộc tiêu đề" (P2.3)
    def content(path: Path) -> list[tuple]:
        return [(i.question, i.answer, i.answer_points) for i in read_jsonl(path, GoldenItem)]

    assert content(golden) == content(GOLDEN)
    paths = [s.path for i in read_jsonl(golden, GoldenItem) for s in i.sources]
    committed_paths = [s.path for i in read_jsonl(GOLDEN, GoldenItem) for s in i.sources]
    assert [(a, b) for a, b in zip(paths, committed_paths, strict=True) if a != b] == [
        (
            ["Chương 1. Bệnh cơ xương khớp", "Thoái hóa khớp gối", "Triệu chứng"],
            ["Chương 1. Bệnh cơ xương khớp", "Thoái hóa khớp gối", "Triệu chung"],
        )
    ]
    assert "không đổi" in runner.invoke(app, ["p2", "golden", *root]).output
    assert runner.invoke(app, ["p2", "golden", *root, "--check"]).exit_code == 0

    # sửa tay 1 câu trong v1 → sinh lại bị TỪ CHỐI (v1 đã khóa); --check bắt trích dẫn sai
    items = list(read_jsonl(golden, GoldenItem))
    items[0].sources[0].quote = "Trích dẫn bịa."
    write_jsonl(golden, items)
    locked = runner.invoke(app, ["p2", "golden", *root])
    assert locked.exit_code == 1 and "golden_qa_v2.jsonl" in locked.output
    checked = runner.invoke(app, ["p2", "golden", *root, "--check"])
    assert checked.exit_code == 1 and "trích dẫn không có trong nút" in checked.output

    (raw / "book01.truth.json").unlink()
    golden.unlink()
    no_truth = runner.invoke(app, ["p2", "golden", *root])
    assert no_truth.exit_code == 1 and "người chuyên môn" in no_truth.output
