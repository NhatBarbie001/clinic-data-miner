"""P2.3 - Dựng cây. Số (#) khớp mục 5 của docs/phases/P2/P2.3_plan.md.

Sách mẫu luôn có chương, không có lời nói đầu trong phạm vi, mục con nào cũng có mục cha - phần
"không dựa trên sách mẫu" (cây tự dựng) là BẮT BUỘC.
"""

import json
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dataminer.books.book01.headings import display_title
from dataminer.books.book01.lines import numbering_of
from dataminer.books.book01.rules import build_blocks, build_tree, classify_headings
from dataminer.books.book01.toc import extract_toc
from dataminer.cli import app
from dataminer.core.config import BlocksCfg
from dataminer.core.io import write_jsonl
from dataminer.devtools.sample_book import SampleBook
from dataminer.evaluation.truth.p2_eval import all_pass, eval_tree
from dataminer.model.block import Block
from dataminer.model.line import Line
from dataminer.model.toc import TocEntry
from dataminer.model.tree import HeadingDecision, Node
from dataminer.pdf.furniture import strip_furniture
from dataminer.pdf.reader import body_font_size, read_lines
from dataminer.structure.toc_match import norm_title
from dataminer.structure.tree_builder import TreeResult, check_invariants, render_tree_md, to_nested
from dataminer.text.blocks import is_upper_text
from tests.conftest import SampleBookFor
from tests.unit.llm_fakes import ROOT, make_settings

PILOT = (4, 9)
runner = CliRunner()


# ---------------------------------------------------------------- dựng từ sách mẫu


def pipeline(pdf: Path) -> tuple[list[Block], list[Line], list[HeadingDecision], list[TocEntry]]:
    """P1 (chỉ quy tắc) → P2.1 → P2.2 cho chương mẫu."""
    lines = read_lines(pdf, pages=PILOT)
    body = body_font_size(lines)
    fr = strip_furniture(lines, body, pdf_pages=list(range(PILOT[0], PILOT[1] + 1)))
    blocks = build_blocks(fr.content, body, BlocksCfg(), {p.page: p.printed_page for p in fr.pages})
    toc = extract_toc(pdf, book_id="book01").entries
    return blocks, fr.content, classify_headings(blocks, toc).decisions, toc


@pytest.fixture(scope="module")
def built(
    sample_book_for: SampleBookFor,
) -> tuple[SampleBook, list[Block], list[Line], TreeResult]:
    book = sample_book_for(7)
    blocks, lines, decisions, toc = pipeline(book.pdf_path)
    return book, blocks, lines, build_tree(blocks, decisions, book_id="book01", toc=toc)


def find(nodes: list[Node], *path: str) -> Node:
    return next(n for n in nodes if n.path[-len(path) :] == list(path))


def child(nodes: list[Node], parent: Node, numbering: str) -> Node:
    """Con của `parent` theo SỐ mục (block chưa sửa OCR: tiêu đề có thể còn lỗi chữ)."""
    return next(n for n in nodes if n.parent_id == parent.id and n.numbering == numbering)


# ---------------------------------------------------------------- dựng tự tay

_counter = iter(range(100_000))


def blk(text: str, kind: str = "paragraph", *, page: int = 4, printed: int | None = 1) -> Block:
    n = next(_counter)
    heading = kind == "heading"
    return Block(
        id=f"b{n:05d}",
        kind=kind,  # type: ignore[arg-type]
        text=text,
        text_rules=text,
        page_start=page,
        page_end=page,
        printed_start=printed,
        printed_end=printed,
        line_ids=[f"l{n}"],
        bbox=(48, 100, 300, 113),
        x0=48,
        font_size=12 if heading else 10.5,
        is_upper=heading and is_upper_text(text),
        numbering=numbering_of(text) if heading else None,
        marker="-" if kind == "list_item" else None,
    )


def make(spec: list[tuple[str, str]], **pages: int) -> tuple[list[Block], list[HeadingDecision]]:
    """spec: (cấp | 'p' | 'li' | 'table', văn bản). Cấp tiêu đề cho thẳng (bỏ qua P2.2)."""
    blocks: list[Block] = []
    decisions: list[HeadingDecision] = []
    page = 4
    for kind, text in spec:
        if kind == "page":
            page = int(text)
            continue
        if kind in ("p", "li", "table"):
            k = {"p": "paragraph", "li": "list_item", "table": "table"}[kind]
            blocks.append(blk(text, k, page=page, printed=page - 3))
            continue
        b = blk(text, "heading", page=page, printed=page - 3)
        blocks.append(b)
        decisions.append(
            HeadingDecision(
                block_id=b.id,
                text=text,
                page=page,
                level=kind,  # type: ignore[arg-type]
                confidence="high",
                reasons=[],
                numbering=b.numbering,
            )
        )
    return blocks, decisions


def toc_entry(title: str, level: str = "disease", pdf_page: int = 4) -> TocEntry:
    return TocEntry(
        title=title,
        title_norm=norm_title(title),
        level=level,  # type: ignore[arg-type]
        printed_page=pdf_page - 3,
        pdf_page=pdf_page,
        toc_pdf_page=3,
        line_id="x",
        x0=48,
    )


def shape(result: TreeResult) -> list[tuple[str, list[str]]]:
    return [(n.level, n.path) for n in result.nodes]


# ---------------------------------------------------------------- #1-4 trên sách mẫu


@pytest.mark.parametrize("seed", [7, 1, 6])
def test_01_02_pilot_tree_matches_truth(sample_book_for: SampleBookFor, seed: int) -> None:
    book = sample_book_for(seed)
    blocks, lines, decisions, toc = pipeline(book.pdf_path)
    result = build_tree(blocks, decisions, book_id="book01", toc=toc)
    levels = [n.level for n in result.nodes]
    assert [levels.count(lv) for lv in ("chapter", "disease", "section", "subsection")] == [
        2,
        3,
        19,
        3,
    ]
    assert "front" not in levels and result.warnings == []
    report = eval_tree(result.nodes, blocks, lines, book.truth, PILOT)
    assert all_pass(report), report
    assert report["G4_content_in_node"]["ratio"] == 1.0


def test_01b_paths_and_display_titles(built: tuple) -> None:
    _, _, _, result = built
    disease = find(result.nodes, "Viêm khớp dạng thấp")
    assert disease.path == ["Chương 1. Bệnh cơ xương khớp", "Viêm khớp dạng thấp"]
    assert disease.level == "disease" and disease.printed_start == 1 and disease.printed_end == 2
    symptom = find(result.nodes, "Viêm khớp dạng thấp", "Triệu chứng")
    assert (symptom.title, symptom.numbering, symptom.block_ids) == ("3. TRIỆU CHỨNG", "3", [])
    assert "empty" not in symptom.flags  # chỉ có mục con → hợp lệ


def test_03_cross_page_block_in_clinical(built: tuple) -> None:
    _, blocks, _, result = built
    clinical = find(result.nodes, "Triệu chứng", "Lâm sàng")
    by_id = {b.id: b for b in blocks}
    crossing = [bid for bid in clinical.block_ids if by_id[bid].page_start != by_id[bid].page_end]
    assert len(crossing) == 1
    assert (clinical.page_start, clinical.page_end) == (4, 5)
    assert (clinical.printed_start, clinical.printed_end) == (1, 2)
    assert "- Khớp sưng, đau, nóng; về sau có thể biến dạng như bàn tay gió thổi." in clinical.text


def test_04_table_in_treatment_of_disease_3(built: tuple) -> None:
    _, blocks, _, result = built
    kinds = {b.id: b.kind for b in blocks}
    treatment = child(result.nodes, find(result.nodes, "Viêm loét dạ dày tá tràng"), "6")
    assert [kinds[b] for b in treatment.block_ids].count("table") == 1
    assert "\nOmeprazol | 20 mg | 2 | 14 ng" in treatment.text  # bảng dạng hàng `ô | ô`
    assert [n for n in result.nodes if any(kinds[b] == "table" for b in n.block_ids)] == [treatment]


# ---------------------------------------------------------------- #5 bất biến


def test_05_invariants_detect_corruption(built: tuple) -> None:
    _, blocks, _, result = built
    nodes = result.nodes
    assert check_invariants(nodes, blocks) == []

    def broken(**change: object) -> list[Node]:
        index = change.pop("index")
        copy = [n.model_copy(deep=True) for n in nodes]
        for key, value in change.items():
            setattr(copy[index], key, value)  # type: ignore[index]
        return copy

    leaf = next(i for i, n in enumerate(nodes) if len(n.block_ids) >= 2)
    other = next(i for i, n in enumerate(nodes) if n.block_ids and i != leaf)
    stolen = nodes[leaf].block_ids[0]
    # mỗi đột biến phải ra ĐÚNG thông báo của nó (không chỉ "có vi phạm": block trùng/mồ côi
    # cũng làm lệch thứ tự - nếu chỉ đòi "có lỗi" thì bỏ hẳn kiểm tra sở hữu vẫn lọt)
    cases = {
        f"block {stolen} thuộc 2 nút": broken(
            index=other, block_ids=[*nodes[other].block_ids, stolen]
        ),
        f"block {stolen} thuộc 0 nút": broken(index=leaf, block_ids=nodes[leaf].block_ids[1:]),
        "nằm ngoài cha": broken(index=leaf, page_end=99),
        "ID nút trùng": broken(index=leaf, id=nodes[0].id),
        "có cha không tồn tại": broken(index=leaf, parent_id="nd_khong_co"),
        "thứ tự block trong cây khác thứ tự đọc": broken(
            index=leaf, block_ids=list(reversed(nodes[leaf].block_ids))
        ),
    }
    for message, corrupted in cases.items():
        problems = check_invariants(corrupted, blocks)
        assert any(message in p for p in problems), (message, problems)
    reordered = check_invariants(cases["thứ tự block trong cây khác thứ tự đọc"], blocks)
    assert reordered == ["thứ tự block trong cây khác thứ tự đọc"]
    empty = broken(index=leaf, block_ids=[])
    problems = check_invariants(empty, blocks)
    assert any("không có cờ 'empty'" in p for p in problems)


# ---------------------------------------------------------------- #6 ID ổn định


def test_06_ids_stable_when_content_changes(built: tuple) -> None:
    book, blocks, _, result = built
    _, _, decisions, toc = pipeline(book.pdf_path)
    again = build_tree(blocks, decisions, book_id="book01", toc=toc)
    assert [n.id for n in again.nodes] == [n.id for n in result.nodes]

    edited = [
        b.model_copy(update={"text": b.text + " (sửa)"}) if b.kind == "paragraph" else b
        for b in blocks
    ]
    changed = build_tree(edited, decisions, book_id="book01", toc=toc)
    assert [n.id for n in changed.nodes] == [n.id for n in result.nodes]
    assert [n.text for n in changed.nodes] != [n.text for n in result.nodes]
    other_book = build_tree(blocks, decisions, book_id="book02", toc=toc)
    assert not {n.id for n in other_book.nodes} & {n.id for n in result.nodes}


# ---------------------------------------------------------------- #7-10 không dựa sách mẫu


def test_07_book_without_chapters() -> None:
    blocks, decisions = make(
        [
            ("disease", "HEN PHẾ QUẢN"),
            ("section", "1. ĐẠI CƯƠNG"),
            ("p", "a"),
            ("disease", "VIÊM PHỔI"),
            ("section", "1. ĐẠI CƯƠNG"),
            ("p", "b"),
        ]
    )
    result = build_tree(blocks, decisions, book_id="bk")
    assert shape(result) == [
        ("book", []),
        ("disease", ["Hen phế quản"]),
        ("section", ["Hen phế quản", "Đại cương"]),
        ("disease", ["Viêm phổi"]),
        ("section", ["Viêm phổi", "Đại cương"]),
    ]
    assert result.nodes[1].parent_id == result.nodes[0].id


def test_08_front_matter_and_disease_intro() -> None:
    blocks, decisions = make(
        [
            ("p", "Sách này dành cho sinh viên."),
            ("p", "Lời cảm ơn."),
            ("chapter", "CHƯƠNG 1. HÔ HẤP"),
            ("p", "Giới thiệu chương."),
            ("disease", "HEN PHẾ QUẢN"),
            ("p", "Đoạn mở đầu của bệnh, trước mục 1."),
            ("section", "1. ĐẠI CƯƠNG"),
            ("p", "x"),
        ]
    )
    result = build_tree(blocks, decisions, book_id="bk", book_title="Sách thử")
    front, chapter, disease = result.nodes[1], result.nodes[2], result.nodes[3]
    assert (front.level, front.path, len(front.block_ids)) == ("front", ["Phần đầu"], 2)
    assert front.text == "Sách này dành cho sinh viên.\nLời cảm ơn."
    assert chapter.text == "Giới thiệu chương."
    assert disease.text == "Đoạn mở đầu của bệnh, trước mục 1."
    assert result.nodes[0].title == "Sách thử"


def test_09_orphans_flagged_and_warned() -> None:
    blocks, decisions = make(
        [
            ("disease", "GOUT"),
            ("section", "1. ĐẠI CƯƠNG"),
            ("p", "a"),
            ("disease", "SỎI THẬN"),
            ("subsection", "2.1. Thể lâm sàng"),
            ("p", "b"),
            ("chapter", "CHƯƠNG 2. TIM"),
            ("section", "1. GHI CHÚ"),
            ("p", "c"),
        ]
    )
    result = build_tree(blocks, decisions, book_id="bk")
    sub = find(result.nodes, "Sỏi thận", "Thể lâm sàng")
    assert sub.flags == ["orphan_subsection"] and sub.parent_id == find(result.nodes, "Sỏi thận").id
    sec = find(result.nodes, "Chương 2. Tim", "Ghi chú")
    assert sec.flags == ["orphan_section"]
    assert len(result.warnings) == 2 and "gắn tạm vào 'Sỏi thận'" in result.warnings[0]


def test_10_toc_reconcile_both_directions() -> None:
    blocks, decisions = make(
        [("disease", "GOUT"), ("p", "a"), ("page", "6"), ("disease", "HEN"), ("p", "b")]
    )
    decisions[0].toc_match = "gout"  # P2.2 đã ghép với mục lục
    decisions[1].flags.append("missing_from_toc")  # P2.2: không có trong mục lục
    toc = [
        toc_entry("Gout", pdf_page=5),  # nút bắt đầu trang 4 ≠ 5
        toc_entry("Sỏi thận", pdf_page=6),  # trong phạm vi, không có nút
        toc_entry("Lao phổi", pdf_page=40),  # ngoài phạm vi → bỏ qua
    ]
    result = build_tree(blocks, decisions, book_id="bk", toc=toc)
    assert find(result.nodes, "Hen").flags == ["missing_from_toc"]
    assert result.warnings == [
        "Mục lục 'Gout': nút bắt đầu ở trang PDF 4, mục lục ghi 5.",
        "Mục lục 'Sỏi thận': 0 nút khớp trong cây (cần đúng 1).",
    ]


def test_other_heading_empty_and_duplicate_path() -> None:
    blocks, decisions = make(
        [
            ("disease", "GOUT"),
            ("section", "1. ĐIỀU TRỊ"),
            ("p", "a"),
            ("other", "LƯU Ý"),
            ("p", "Không tự ý dùng thuốc."),
            ("section", "2. PHÒNG BỆNH"),
            ("section", "3. ĐIỀU TRỊ"),
            ("li", "b"),
        ]
    )
    result = build_tree(blocks, decisions, book_id="bk")
    treat = result.nodes[2]
    assert treat.text == "a\nLƯU Ý\nKhông tự ý dùng thuốc." and treat.flags == ["other_heading"]
    assert find(result.nodes, "Phòng bệnh").flags == ["empty"]
    dup = result.nodes[-1]
    assert dup.path == ["Gout", "Điều trị"] and dup.flags == ["duplicate_path"]
    assert dup.id != treat.id and dup.text == "- b"


@pytest.mark.parametrize(
    ("text", "level", "expected"),
    [
        ("3. TRIỆU CHỨNG", "section", "Triệu chứng"),
        ("3.1. Lâm sàng", "subsection", "Lâm sàng"),
        ("CHƯƠNG 1. BỆNH CƠ XƯƠNG KHỚP", "chapter", "Chương 1. Bệnh cơ xương khớp"),
        ("VIÊM KHỚP DẠNG THẤP", "disease", "Viêm khớp dạng thấp"),
        ("Nhiễm Helicobacter pylori", "disease", "Nhiễm Helicobacter pylori"),
        ("  VIÊM   GAN B ", "disease", "Viêm gan b"),
    ],
)
def test_display_title(text: str, level: str, expected: str) -> None:
    assert display_title(text, level) == expected


# ---------------------------------------------------------------- #11 tree.md, tree.json


def test_11_tree_md_and_nested(built: tuple) -> None:
    _, blocks, _, result = built
    md = render_tree_md(result.nodes, blocks).splitlines()
    assert md[0] == "book01 · tr.in 1–6"
    assert md[1] == "├─ Chương 1. Bệnh cơ xương khớp · tr.in 1–4"
    assert "│  │  ├─ 3. Triệu chứng · (chỉ có mục con) · tr.in 1–2" in md
    assert "│  │  │  ├─ 3.1. Lâm sàng · 4 gạch đầu dòng · tr.in 1–2" in md
    assert md[-2].startswith("      ├─ 6. Điều tr")  # chữ có thể còn lỗi OCR (chưa sửa)
    assert md[-2].endswith(" · 3 gạch đầu dòng, 1 chú thích, 1 bảng · tr.in 6")
    nested = to_nested(result.nodes)
    assert [c["display_title"] for c in nested["children"]] == [
        "Chương 1. Bệnh cơ xương khớp",
        "Chương 2. Bệnh tiêu hóa",
    ]
    assert nested["children"][0]["children"][0]["children"][0]["n_blocks"] == 1


# ---------------------------------------------------------------- #12 đối chứng âm


def _move_truth_lines(truth: dict, texts: list[str], after_heading: str) -> dict:
    wrong = json.loads(json.dumps(truth))
    moved = [ln for ln in wrong["lines"] if ln["text"].startswith(tuple(texts))]
    assert len(moved) == len(texts)
    rest = [ln for ln in wrong["lines"] if ln not in moved]
    at = next(i for i, ln in enumerate(rest) if ln["text"] == after_heading) + 1
    wrong["lines"] = rest[:at] + moved + rest[at:]
    return wrong


def test_12_eval_fails_on_wrong_truth(built: tuple) -> None:
    book, blocks, lines, result = built
    nodes = result.nodes
    one = _move_truth_lines(book.truth, ["- Cứng khớp buổi sáng kéo dài"], "4. BIẾN CHỨNG")
    report = eval_tree(nodes, blocks, lines, one, PILOT)["G4_content_in_node"]
    assert report["correct"] == 109 and len(report["problems"]) == 1  # 1/110: vẫn ≥ 99%
    two = _move_truth_lines(
        book.truth,
        ["- Cứng khớp buổi sáng kéo dài", "- Giới tính nữ"],
        "4. BIẾN CHỨNG",
    )
    assert not eval_tree(nodes, blocks, lines, two, PILOT)["G4_content_in_node"]["pass"]

    renamed = json.loads(json.dumps(book.truth))
    renamed["toc"][2]["title"] = "Gout"
    g3 = eval_tree(nodes, blocks, lines, renamed, PILOT)["G3_diseases_vs_toc"]
    assert not g3["pass"] and "thiếu nút bệnh 'Gout'" in g3["problems"]
    moved = json.loads(json.dumps(book.truth))
    moved["toc"][1]["pdf_page"] = 5
    assert not eval_tree(nodes, blocks, lines, moved, PILOT)["G3_diseases_vs_toc"]["pass"]


def test_12b_eval_fails_on_broken_tree(built: tuple) -> None:
    book, blocks, lines, result = built
    nodes = [n.model_copy(deep=True) for n in result.nodes]
    leaf = next(n for n in nodes if len(n.block_ids) > 1)
    leaf.block_ids = leaf.block_ids[1:]  # 1 block mồ côi
    report = eval_tree(nodes, blocks, lines, book.truth, PILOT)
    assert not report["G6_invariants"]["pass"]
    extra = [*result.nodes, result.nodes[2].model_copy(update={"id": "nd_x", "title": "GOUT"})]
    assert "thừa nút bệnh 'GOUT'" in str(eval_tree(extra, blocks, lines, book.truth, PILOT))
    empty = eval_tree([], [], [], book.truth, PILOT)
    assert not all_pass(empty)  # không được "đạt" im lặng


# ---------------------------------------------------------------- CLI


def test_cli_tree(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    book = sample_book_for(7)
    make_settings(tmp_path)
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    shutil.copytree(ROOT / "prompts", tmp_path / "prompts")
    raw = tmp_path / "data" / "books" / "book01" / "raw"
    raw.mkdir(parents=True)
    shutil.copy(book.pdf_path, raw / "book01.pdf")
    shutil.copy(book.truth_path, raw / "book01.truth.json")
    blocks, lines, _, _ = pipeline(book.pdf_path)
    p1 = tmp_path / "data" / "books" / "book01" / "p1_clean"
    write_jsonl(p1 / "blocks.jsonl", blocks)
    write_jsonl(p1 / "content_lines.jsonl", lines)
    root = ["--root", str(tmp_path)]

    missing = runner.invoke(app, ["p2", "tree", *root])
    assert missing.exit_code == 1 and "dm p2 headings" in missing.output

    assert runner.invoke(app, ["p2", "headings", *root, "--no-llm"]).exit_code == 0
    good = runner.invoke(app, ["p2", "tree", *root, "--eval"])
    assert good.exit_code == 0, good.output
    assert "2 chương · 3 bệnh · 19 mục · 3 mục con" in good.output
    assert "✓ G4_content_in_node" in good.output
    out = tmp_path / "data" / "books" / "book01" / "p2_tree"
    assert len((out / "nodes.jsonl").read_text(encoding="utf-8").splitlines()) == 28
    assert json.loads((out / "tree.json").read_text(encoding="utf-8"))["level"] == "book"
    assert "3.1. Lâm sàng" in (out / "tree.md").read_text(encoding="utf-8")
