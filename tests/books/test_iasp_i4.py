"""P2R I4 - sách IASP: loại mục (L13) + mục lục (L12), chỉ tiêu A5-A6.
Xem docs/phases/P2R/I4_plan.md. Test cuối đọc mục lục PDF thật nếu máy có file.
"""

import pytest

from dataminer.books.iasp import toc
from dataminer.books.iasp.rules import RULES
from dataminer.core.config import HeadingsCfg, SectionsCfg, TocCfg
from dataminer.evaluation.checks import section_types, toc_coverage
from dataminer.model.toc import TocEntry
from dataminer.model.tree import HeadingDecision, Node
from dataminer.structure.heading_levels import match_toc, toc_similarity
from dataminer.structure.section_mapper import (
    EXTRA_SECTION_TYPES,
    SECTION_TYPES,
    load_section_map,
    map_sections,
    normalize_section_title,
)
from tests.books.test_iasp_p1 import PDF, line
from tests.books.test_iasp_p2 import blk
from tests.unit.llm_fakes import ROOT

MAP = load_section_map(ROOT / "configs" / "books" / "iasp" / "section_map.yaml")


# ---------------------------------------------------------------- L13: loại mục


@pytest.mark.parametrize(
    ("title", "key"),
    [
        ("Code X32.X3a", "code"),  # mã dính sau tên mục
        ("Code(s)", "code"),
        ("Codes", "code"),
        ("Main Features", "main features"),
        ("1. History of Widespread Pain", "history of widespread pain"),
    ],
)
def test_section_key(title: str, key: str) -> None:
    assert RULES.section_key(title) == key


def test_default_section_key_is_unchanged() -> None:
    """Sách mẫu: khóa vẫn là chuẩn hóa cũ (bỏ số, bỏ dấu)."""
    from dataminer.books.book01.rules import RULES as BOOK01

    assert BOOK01.section_key("3. TRIỆU CHỨNG") == normalize_section_title("3. TRIỆU CHỨNG")
    assert BOOK01.section_key("Code X32.X3a") == "code x32.x3a"


@pytest.mark.parametrize(
    ("title", "kind"),
    [
        ("Definition", "definition"),
        ("Site", "site"),
        ("System(s)", "body_system"),
        ("Main Features", "symptom"),
        ("Aggravating Factors", "symptom"),  # quyết định của người duyệt 2026-10-23
        ("Signs and Laboratory Findings", "paraclinical"),
        ("Pathology", "pathophysiology"),
        ("Schedule of Neoplastic Diseases", "cause"),  # quyết định của người duyệt
        ("Summary of Essential Features and Diagnostic Criteria", "diagnosis"),
        ("Differential Diagnosis", "differential_diagnosis"),
        ("Relief", "treatment"),
        ("Complications", "complication"),
        ("Usual Course", "prognosis"),
        ("Social and Physical Disability", "disability"),
        ("Code X33.X7b", "code"),
        ("Reference", "references"),
        ("Remarks", "other"),  # quyết định của người duyệt
    ],
)
def test_section_map(title: str, kind: str) -> None:
    assert MAP[RULES.section_key(title)] == kind


def test_new_types_are_known_and_extra() -> None:
    assert set(EXTRA_SECTION_TYPES) <= set(SECTION_TYPES)
    assert set(MAP.values()) <= set(SECTION_TYPES)


def _node(title: str, level: str, parent: str | None, i: int) -> Node:
    return Node(id=f"n{i}", level=level, parent_id=parent, order=i, title=title,  # type: ignore[arg-type]
                title_norm=title.lower(), display_title=title, path=[title], page_start=1,
                page_end=1)  # fmt: skip


def test_map_sections_with_iasp_key_and_inheritance() -> None:
    nodes = [
        _node("Fibromyalgia", "disease", None, 0),
        _node("Code X33.X8a", "section", "n0", 1),
        _node(
            "Classification Criteria for Primary and Concomitant Fibromyalgia "
            "(from Wolfe et al. 1990)",
            "section",
            "n0",
            2,
        ),
        _node("1. History of Widespread Pain", "subsection", "n2", 3),
        _node("Strange Heading", "section", "n0", 4),
    ]
    result = map_sections(
        nodes, MAP, SectionsCfg(llm_fallback=False), section_key=RULES.section_key
    )
    assert [(n.section_type, n.section_source) for n in nodes[1:]] == [
        ("code", "map"),
        ("diagnosis", "map"),
        ("diagnosis", "inherited"),  # mục con không tra được → kế thừa mục cha
        ("other", "none"),
    ]
    assert "section_type_unknown" in nodes[4].flags and result.warnings
    check = section_types(nodes)
    assert not check.passed and "không tra được: Strange Heading" in check.details


# ---------------------------------------------------------------- L12: mục lục


def _toc_lines() -> list:  # type: ignore[type-arg]
    rows = [
        ("CONTENTS", 279, 51),
        ("Part I   Topics and Codes", 114, 170), ("1", 491, 171),
        ("E.  Local Syndromes of the Upper Limbs", 126, 366), ("23", 488, 366),  # Part I: bỏ
        ("Part II   Detailed Descriptions of Pain Syndromes", 114, 487), ("37", 488, 487),
        ("A. Relatively Generalized Syndromes", 122, 518), ("39", 488, 518),
        ("I. Relatively Generalized Syndromes", 162, 535), ("39", 488, 535),
        ("V. Primary Headache Syndromes, Vascular Disorders, and", 158, 618), ("77", 488, 618),
        ("Cerebrospinal Fluid Syndromes", 176, 630),  # dòng sau của tên, không số
        ("Headache Crosswalk", 176, 647), ("90", 488, 647),
        ("VIII. Visceral Pain in the Neck", 149, 697), ("98", 488, 697),
        ("v", 304, 759),  # số trang La Mã ở chân trang mục lục
    ]  # fmt: skip
    rows_6 = [
        ("XI. Pain in the Shoulder, Arm, and Hand", 184, 170), ("121", 507, 170),
        ("Part III Pain Terms: A Current List with Definitions", 144, 637), ("207", 507, 644),
        ("Index", 144, 686), ("215", 507, 686),
    ]  # fmt: skip
    return [line(t, x0=x, y=y, page=5, x1=x + 30) for t, x, y in rows] + [
        line(t, x0=x, y=y, page=6, x1=x + 30) for t, x, y in rows_6
    ]


def test_parse_toc() -> None:
    entries, warnings = toc.parse_toc(_toc_lines())
    assert warnings == []
    assert [(e.title, e.level, e.printed_page) for e in entries] == [
        ("A. Relatively Generalized Syndromes", "part", 39),
        ("I. Relatively Generalized Syndromes", "chapter", 39),
        ("V. Primary Headache Syndromes, Vascular Disorders, and Cerebrospinal Fluid Syndromes",
         "chapter", 77),
        ("Headache Crosswalk", "chapter", 90),
        ("VIII. Visceral Pain in the Neck", "chapter", 98),  # không dính "v" của chân trang
        ("XI. Pain in the Shoulder, Arm, and Hand", "chapter", 121),
    ]  # fmt: skip
    assert [toc.toc_key(e.title) for e in entries] == ["A", "I", "V", None, "VIII", "XI"]


def test_parse_toc_without_part_ii_warns() -> None:
    entries, warnings = toc.parse_toc(_toc_lines()[:5])
    assert entries == [] and "Part II" in warnings[0]


def test_toc_title_matches_body_heading() -> None:
    prefix = RULES.chapter_prefix
    body = "GROUP XI: PAIN IN THE SHOULDER, ARM, AND HAND"
    assert toc_similarity(body, "XI. Pain in the Shoulder, Arm, and Hand", prefix) == 1.0
    # sách đảo từ giữa mục lục và thân sách → khớp gần, vẫn ≥ ngưỡng 0.8 của IASP
    reordered = toc_similarity(
        "GROUP IX: CERVICAL OR RADICULAR SPINAL PAIN SYNDROMES",
        "IX. Cervical Spinal or Radicular Pain Syndromes",
        prefix,
    )
    assert 0.8 <= reordered < 0.85


def _entry(title: str, level: str, page: int) -> TocEntry:
    return TocEntry(
        title=title,
        title_norm=title.lower(),
        level=level,  # type: ignore[arg-type]
        printed_page=page - 16,
        pdf_page=page,
        toc_pdf_page=6,
        line_id="x",
        x0=150,
    )


def test_toc_without_diseases_does_not_flag_syndromes() -> None:
    blocks = [blk("GROUP XI: PAIN IN THE SHOULDER, ARM, AND HAND", 13.5),
              blk("Tumors of the Brachial Plexus (XI-1)", 13.5)]  # fmt: skip
    entries = [_entry("XI. Pain in the Shoulder, Arm, and Hand", "chapter", 137)]

    def decisions() -> list[HeadingDecision]:
        return [HeadingDecision(block_id=b.id, text=b.text, page=137, level=lv, confidence="high",
                                reasons=[]) for b, lv in zip(blocks, ("chapter", "disease"),
                                                              strict=True)]  # fmt: skip

    by_id = {b.id: b for b in blocks}
    iasp = decisions()
    match_toc(iasp, by_id, entries, HeadingsCfg(toc_lists_diseases=False), RULES.chapter_prefix)
    assert iasp[0].source == "toc" and iasp[1].flags == [] and iasp[1].confidence == "high"
    default = decisions()  # sách mẫu: bệnh vắng mục lục → đáng ngờ (giữ hành vi cũ)
    match_toc(default, by_id, entries, HeadingsCfg(), RULES.chapter_prefix)
    assert default[1].flags == ["missing_from_toc"] and default[1].confidence == "low"


def test_toc_coverage() -> None:
    nodes = [_node("E. Local", "part", None, 0), _node("GROUP XI", "chapter", "n0", 1)]
    nodes[0].numbering, nodes[1].numbering = "E", "XI"
    nodes[0].page_start = nodes[1].page_start = 137
    ok = toc_coverage([("E", "part", 137), ("XI", "chapter", 137)], nodes, lambda n: n.numbering)
    assert ok.passed and ok.value == "2/2"
    bad = toc_coverage([("XI", "chapter", 138), ("XII", "chapter", 144)], nodes,
                       lambda n: n.numbering)  # fmt: skip
    assert bad.details == [
        "chapter XI: cây PDF 137 ≠ mục lục PDF 138",
        "chapter XII: 0 nút (cần 1)",
    ]


@pytest.mark.skipif(not PDF.is_file(), reason="không có file sách IASP trên máy này")
def test_real_pdf_toc() -> None:
    result = toc.extract_toc(PDF, book_id="iasp", cfg=TocCfg(pages=(5, 6)), content_pages=(53, 222))
    assert len(result.entries) == 43 and result.page_offset == 16
    by_key = {toc.toc_key(e.title): e for e in result.entries}
    assert len([k for k in by_key if k]) == 41  # 8 nhóm chữ cái + 33 GROUP
    assert by_key["XI"].pdf_page == 137 and by_key["H"].pdf_page == 213
    assert result.entries[0].title.startswith("List of Items Usually Provided")


def test_a5_fails_on_unmapped_title_even_when_share_is_low() -> None:
    nodes = [_node("Syndrome", "disease", None, 0)]
    nodes += [_node("Definition", "section", "n0", i) for i in range(1, 40)]
    nodes.append(_node("Strange Heading", "section", "n0", 40))
    map_sections(nodes, MAP, SectionsCfg(llm_fallback=False), section_key=RULES.section_key)
    check = section_types(nodes)
    assert check.value.startswith("2.5%")  # dưới ngưỡng 5% …
    assert not check.passed  # … nhưng vẫn trượt vì có tên mục từ điển chưa có


def test_toc_matches_letter_group_heading() -> None:
    block = blk("E. LOCAL SYNDROMES OF THE UPPER LIMBS AND RELATIVELY GENERALIZED", 13.5)
    decision = HeadingDecision(block_id=block.id, text=block.text, page=137, level="part",
                               confidence="high", reasons=[])  # fmt: skip
    entry = _entry("E. Local Syndromes of the Upper Limbs and Relatively Generalized", "part", 137)
    missing, _ = match_toc(
        [decision], {block.id: block}, [entry], HeadingsCfg(), RULES.chapter_prefix
    )
    assert missing == [] and decision.source == "toc" and decision.level == "part"
