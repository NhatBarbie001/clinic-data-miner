"""P2R I3 - sách IASP: nối tiêu đề nhiều dòng, mã hội chứng / mã IASP, cấp tiêu đề, cây, chỉ tiêu
A2-A4. Xem docs/phases/P2R/I3_plan.md.

Phần lớn dùng block TỰ DỰNG; test cuối chạy trên PDF thật (pilot GROUP XI) nếu máy có file.
"""

import re
from typing import Any

import pytest

from dataminer.books.iasp import codes
from dataminer.books.iasp.headings import code_of, is_syndrome
from dataminer.books.iasp.lines import heading_joins
from dataminer.books.iasp.rules import RULES
from dataminer.core.config import BlocksCfg, HeadingsCfg
from dataminer.evaluation.checks import code_sequence, count_match, section_coverage
from dataminer.model.block import Block
from dataminer.model.tree import Node
from dataminer.pdf.reader import body_font_size, read_lines
from dataminer.structure.heading_levels import classify_headings
from dataminer.structure.tree_builder import build_tree, check_invariants
from dataminer.text import blocks as text_blocks
from dataminer.text.blocks import default_heading_joins, is_upper_text
from tests.books.test_iasp_p1 import PDF, line

BODY = 10.0
_counter = iter(range(100_000))


def blk(text: str, size: float = BODY, kind: str = "heading", page: int = 137) -> Block:
    n = next(_counter)
    return Block(
        id=f"b{n:05d}",
        kind=kind,  # type: ignore[arg-type]
        text=text,
        text_rules=text,
        page_start=page,
        page_end=page,
        line_ids=[f"l{n}"],
        bbox=(65, 100, 300, 113),
        x0=65,
        font_size=size,
        is_upper=kind == "heading" and is_upper_text(text),
        numbering=RULES.numbering(text) if kind == "heading" else None,
    )


# ---------------------------------------------------------------- L8: mã hội chứng


@pytest.mark.parametrize(
    ("title", "code"),
    [
        ("Tumors of the Brachial Plexus (XI-1)", "XI-1"),
        ("Phantom Pain (1-3)", "I-3"),  # nhóm I in bằng chữ số
        ("Hypoglossal Pain from Trauma (11- 13)", "II-13"),  # nhóm II = "11", có dấu cách
        ("Raeder’s Syndrome (111-7)", "III-7"),
        ("Neuralgia of … Nerves (XXV-I)", "XXV-1"),  # chữ I thay số 1
        ("Muscle Tension Pain (1-16.1)", "I-16.1"),  # mã con
        ("Upper Lumbar Spinal Pain (XXVI-9.1)", "XXVI-9.1"),
        ("Complex Regional Pain Syndromes (CRPS)", None),  # ngoặc không phải mã
        ("Erythema Pernio (Chilblains)", None),
        ("Something (12-3)", None),  # "12" không phải cách in La Mã nào
        ("Testicular Pain", None),
    ],
)
def test_syndrome_code(title: str, code: str | None) -> None:
    assert codes.syndrome_code(title) == code


def test_strip_code_and_combined_entry() -> None:
    assert (
        codes.strip_code("Tumors of the Brachial Plexus (XI-1)") == "Tumors of the Brachial Plexus"
    )
    assert codes.strip_code("Complex Regional Pain Syndromes (CRPS)").endswith("(CRPS)")
    combined = "Intermittent Claudication (XV-1) and Rest Pain (XV-2)"
    assert codes.syndrome_codes(combined) == ["XV-1", "XV-2"]
    assert codes.strip_code(combined) == "Intermittent Claudication (XV-1) and Rest Pain"


# ---------------------------------------------------------------- L11: mã IASP 5 trục


@pytest.mark.parametrize(
    ("text", "found"),
    [
        ("102.X4b, 202.X4b", ["102.X4b", "202.X4b"]),
        ("Code X32.X3a", ["X32.X3a"]),  # mã nằm trên dòng tiêu đề mục
        ("203.XlcR", ["203.X1cR"]),  # l thay 1
        ("X34.XOa", ["X34.X0a"]),  # O thay 0
        ("X4X.X l b", ["X4X.X1b"]),  # có dấu cách
        ("023 .X l b", ["023.X1b"]),
        ("Code 002.x2a", ["002.X2a"]),  # x thường
        ("006.X81", ["006.X8l"]),  # số 1 thay chữ l
        ("222.68a 622.68c", ["222.68a", "622.68c"]),  # trục IV là số
        ("2XX.XXz / Upper limb", ["2XX.XXz"]),
        ("13X.X8eS/C 23X.X8eR", ["13X.X8eS", "23X.X8eR"]),
        ("004.X8 or 004.X1 (if subsequent to trauma) 004.X8", ["004.X8", "004.X1"]),  # không lặp
        ("see pages 11-16; dose 12.5 mg; version 1.2", []),  # số thường không phải mã
    ],
)
def test_iasp_codes(text: str, found: list[str]) -> None:
    assert codes.iasp_codes(text) == found


# ---------------------------------------------------------------- P1: nối tiêu đề nhiều dòng


@pytest.mark.parametrize(
    ("prev", "text", "joins"),
    [
        ("Upper Lumbar Spinal Pain of Unknown or Uncertain Origin", "(XXVI-9.1)", True),
        ("Complex Regional Pain Syndromes", "(CRPS)", True),
        ("Trigeminal Neuralgia", "(Tic Douloureux) (II-1)", True),
        ("E.", "LOCAL SYNDROMES OF THE UPPER LIMBS AND RELATIVELY", True),
        ("GROUP XXIV: DISEASES OF THE BLADDER, UTERUS, OVARIES,", "AND ADNEXA", True),
        ("Lumbar Spinal or Radicular Pain", "Attributable to a Fracture (XXVI-1)", True),
        ("Intermittent Claudication (XV-1)", "and Rest Pain (XV-2)", True),  # mục gộp
        ("Neuralgia of … Nerves (XXV-I)", "Testicular Pain", False),  # tên đã kết thúc bằng mã
        ("E. LOCAL SYNDROMES OF THE UPPER LIMBS", "GROUP XI: PAIN IN THE SHOULDER", False),
        ("GROUP XVII: VISCERAL AND OTHER CHEST PAIN", "Acute Herpes Zoster (XVII-1)", False),
        ("C.", "Definition", False),
    ],
)
def test_heading_joins(prev: str, text: str, joins: bool) -> None:
    assert heading_joins(prev, text) is joins


def test_default_heading_joins_is_the_old_rule() -> None:
    """Sách mẫu: luật cũ giữ nguyên (cùng kiểu IN HOA, dòng sau không đánh số)."""

    def numbering(text: str) -> str | None:
        return "1" if text.startswith("1.") else None

    assert default_heading_joins("VIÊM KHỚP", "DẠNG THẤP", numbering)
    assert not default_heading_joins("VIÊM KHỚP", "Dạng thấp", numbering)
    assert not default_heading_joins("VIÊM KHỚP", "1. ĐỊNH NGHĨA", numbering)


def test_p1_joins_code_line_and_letter_group() -> None:
    rows = [
        line("E.", y=73, x0=65, x1=80, size=14.0, bold=True),
        line("LOCAL SYNDROMES OF THE UPPER LIMBS", y=73, x0=101, x1=500, size=14.0, bold=True),
        line("Upper Lumbar Spinal Pain of Unknown", y=200, size=14.0, bold=True),
        line("(XXVI-9.1)", y=216, size=14.0, bold=True),
        line("Definition", y=240, bold=True),
        line("As for XXVI-9 but upper.", y=252),
    ]
    out = text_blocks.build_blocks(
        rows,
        BODY,
        BlocksCfg(detect_tables=False),
        classify=RULES.classify_line,
        numbering=RULES.numbering,
        heading_joins=RULES.heading_joins,
    )
    assert [(b.kind, b.text, b.numbering) for b in out[:3]] == [
        ("heading", "E. LOCAL SYNDROMES OF THE UPPER LIMBS", "E"),
        ("heading", "Upper Lumbar Spinal Pain of Unknown (XXVI-9.1)", "XXVI-9.1"),
        ("heading", "Definition", None),
    ]


def test_bold_note_is_content_not_a_section() -> None:
    cfg = BlocksCfg()
    note = line("Note: “b” coding used to allow the “a” coding to be em-", bold=True)
    assert RULES.classify_line(note, BODY, cfg) == "body"
    assert RULES.classify_line(
        line("Note: Specific Myofascial", bold=True, size=14.0), BODY, cfg
    ) == ("heading")


# ---------------------------------------------------------------- P2: cấp tiêu đề


@pytest.mark.parametrize(
    ("text", "size", "level", "confidence"),
    [
        ("E. LOCAL SYNDROMES OF THE UPPER LIMBS", 13.5, "part", "high"),
        ("GROUP XI: PAIN IN THE SHOULDER, ARM, AND HAND", 13.5, "chapter", "high"),
        ("PART II", 15.5, "other", "high"),  # tên phần sách → nút "Phần đầu"
        ("HEADACHE CROSSWALK", 13.5, "chapter", "medium"),  # IN HOA không GROUP
        ("OF PAIN SYNDROMES", 13.5, "other", "medium"),  # dòng sau của tiêu đề căn giữa
        ("Tumors of the Brachial Plexus (XI-1)", 13.5, "disease", "high"),
        ("Gout (1-13)", 15.0, "disease", "high"),  # cỡ 15 nhưng chữ thường: vẫn là hội chứng
        ("Testicular Pain", 13.0, "disease", "medium"),  # L9: không mã
        ("Definition", BODY, "section", "high"),
        ("1. History of Widespread Pain", BODY, "subsection", "high"),
    ],
)
def test_rule_level(text: str, size: float, level: str, confidence: str) -> None:
    got_level, got_conf, reasons = RULES.rule_level(blk(text, size), BODY, HeadingsCfg())
    assert (got_level, got_conf) == (level, confidence)
    assert reasons


@pytest.mark.parametrize(
    ("text", "level", "shown"),
    [
        ("E. LOCAL SYNDROMES OF THE UPPER LIMBS", "part", "E. Local syndromes of the upper limbs"),
        (
            "GROUP XI: PAIN IN THE SHOULDER, ARM, AND HAND",
            "chapter",
            "GROUP XI: Pain in the shoulder, arm, and hand",
        ),
        (
            "GROUP XVI: PAIN OF PSYCHOLOGICAL ORIGIN IN THE LOWER LIMBS (XVI-1)",
            "chapter",
            "GROUP XVI: Pain of psychological origin in the lower limbs",
        ),
        ("HEADACHE CROSSWALK", "chapter", "Headache crosswalk"),
        ("Tumors of the Brachial Plexus (XI-1)", "disease", "Tumors of the Brachial Plexus"),
        ("Definition", "section", "Definition"),
    ],
)
def test_display_title(text: str, level: str, shown: str) -> None:
    assert RULES.display_title(text, level) == shown


# ---------------------------------------------------------------- cây + thuộc tính


def _tree(spec: list[tuple[str, float, str]]) -> list[Node]:
    blocks = [blk(text, size, kind) for text, size, kind in spec]
    levels = classify_headings(
        blocks, [], HeadingsCfg(llm_fallback=False), rule_level=RULES.rule_level
    )
    nodes = build_tree(
        blocks, levels.decisions, book_id="iasp", display_title=RULES.display_title
    ).nodes
    RULES.annotate_tree(nodes)
    assert check_invariants(nodes, blocks) == []
    return nodes


H, P = "heading", "paragraph"
SPEC: list[tuple[str, float, str]] = [
    ("PART II", 15.5, H),
    ("E. LOCAL SYNDROMES OF THE UPPER LIMBS", 13.5, H),
    ("GROUP XI: PAIN IN THE SHOULDER, ARM, AND HAND", 13.5, H),
    ("Tumors of the Brachial Plexus (XI-1)", 13.5, H),
    ("Definition", BODY, H),
    ("Progressive aching, burning pain.", BODY, P),
    ("Code", BODY, H),
    ("102.X4b", BODY, P),
    ("202.X4b", BODY, P),
    ("References", BODY, H),
    ("Smith, J. (1990).", BODY, P),
    ("Definition", BODY, H),  # sách thiếu tên hội chứng tiếp theo (như PDF 185)
    ("Pain in the retroverted uterus.", BODY, P),
    ("Chemical Irritation of the Brachial Plexus (XII-2)", 13.5, H),  # mã sai nhóm
    ("Code X33.X7b", BODY, H),  # mã trên dòng tiêu đề mục
    ("Testicular Pain", 13.0, H),  # không mã, không mục Code
]


def test_tree_levels_codes_and_flags() -> None:
    nodes = _tree(SPEC)
    by_title = {n.display_title: n for n in nodes}
    assert [n.level for n in nodes[:5]] == ["book", "front", "part", "chapter", "disease"]
    tumors = by_title["Tumors of the Brachial Plexus"]
    assert tumors.numbering == "XI-1"
    assert tumors.path == [
        "E. Local syndromes of the upper limbs",
        "GROUP XI: Pain in the shoulder, arm, and hand",
        "Tumors of the Brachial Plexus",
    ]
    assert tumors.attrs == {"iasp_codes": ["102.X4b", "202.X4b"]}
    assert "missing_syndrome_title" in tumors.flags
    chem = by_title["Chemical Irritation of the Brachial Plexus"]
    assert chem.attrs["iasp_codes"] == ["X33.X7b"]
    assert "code_group_mismatch" in chem.flags
    testicular = by_title["Testicular Pain"]
    assert {"no_code", "no_iasp_code"} <= set(testicular.flags)
    assert [code_of(n) for n in nodes if is_syndrome(n)] == ["XI-1", "XII-2", None]


def test_chapter_that_is_a_syndrome() -> None:
    nodes = _tree(
        [
            ("GROUP XVI: PAIN OF PSYCHOLOGICAL ORIGIN IN THE LOWER LIMBS (XVI-1)", 13.5, H),
            ("Code", BODY, H),
            ("6XX.X8", BODY, P),
        ]
    )
    chapter = next(n for n in nodes if n.level == "chapter")
    assert is_syndrome(chapter) and code_of(chapter) == "XVI-1"
    assert "chapter_is_syndrome" in chapter.flags
    assert chapter.attrs == {"codes": ["XVI-1"], "iasp_codes": ["6XX.X8"]}


def test_book01_nodes_have_no_attrs_by_default() -> None:
    node = Node(id="n", level="book", parent_id=None, order=0, title="t", title_norm="t",
                display_title="t", path=[], page_start=1, page_end=1)  # fmt: skip
    assert node.attrs == {}


# ---------------------------------------------------------------- chỉ tiêu A2-A4


def test_code_sequence() -> None:
    ok = ["XI-1", "XI-2", "IX-1", "IX-2", "IX-2.1", "IX-2.2", "IX-3", "I-1", "I-2.1", "I-2.2"]
    assert code_sequence(ok).passed  # mã con sau mã chính, hoặc mở đầu số mới bằng .1
    result = code_sequence(["XI-1", "XI-3", "XI-3", "XXIV-6", "XXIV-8", "bad"], ["XXIV-6→XXIV-8"])
    assert not result.passed
    assert result.details == [
        "XI-1→XI-3",
        "mã trùng: XI-3",
        "(đầu nhóm)→XXIV-6",
        "mã không đúng dạng: bad",
    ]
    assert not code_sequence(["IX-1", "IX-1.2"]).passed  # thiếu IX-1.1
    assert not code_sequence(["IX-1", "IX-3.1"]).passed  # thiếu IX-2
    assert not code_sequence(["IX-1", "IX-2.2"]).passed  # số mới phải mở bằng .1 (thiếu IX-2.1)


def test_count_match_and_coverage() -> None:
    assert count_match(331, 331).passed
    assert count_match(328, 331).passed  # lệch 0.9%
    assert not count_match(320, 331).passed
    nodes = _tree(SPEC)
    kids = {n.id: [m for m in nodes if m.parent_id == n.id] for n in nodes}
    result = section_coverage(
        [n for n in nodes if is_syndrome(n)],
        lambda s: kids[s.id],
        re.compile(r"^(Definition|Codes?\b)"),
    )
    assert result.value.startswith("66.7%") and not result.passed
    assert result.details == ["'Testicular Pain' (PDF 137)"]


# ---------------------------------------------------------------- trên PDF thật (nếu có)


@pytest.mark.skipif(not PDF.is_file(), reason="không có file sách IASP trên máy này")
def test_real_pdf_pilot_group_xi() -> None:
    page = read_lines(PDF, book_id="iasp", pages=(137, 143), order=RULES.order_lines)
    content = [ln for ln in page if RULES.page_number(ln.text) is None]
    cfg = BlocksCfg(dehyphenate=True, detect_tables=False, bullet_markers=["-", "—"])
    built = text_blocks.build_blocks(
        content,
        body_font_size(page),
        cfg,
        classify=RULES.classify_line,
        numbering=RULES.numbering,
        heading_joins=RULES.heading_joins,
    )
    nodes = _nodes_from(built)
    chapter = next(n for n in nodes if n.level == "chapter")
    assert chapter.display_title == "GROUP XI: Pain in the shoulder, arm, and hand"
    syndromes = [n for n in nodes if n.level == "disease"]
    assert syndromes[0].display_title == "Tumors of the Brachial Plexus"
    assert syndromes[0].attrs["iasp_codes"] == ["102.X4b", "202.X4b"]
    seq = [code_of(n) or "" for n in syndromes]
    assert seq == [f"XI-{i}" for i in range(1, len(seq) + 1)]
    assert code_sequence(seq).passed and len(seq) >= 15


def _nodes_from(blocks: list[Block]) -> list[Node]:
    levels: Any = classify_headings(
        blocks, [], HeadingsCfg(llm_fallback=False), rule_level=RULES.rule_level
    )
    nodes = build_tree(
        blocks, levels.decisions, book_id="iasp", display_title=RULES.display_title
    ).nodes
    RULES.annotate_tree(nodes)
    assert check_invariants(nodes, blocks) == []
    return nodes
