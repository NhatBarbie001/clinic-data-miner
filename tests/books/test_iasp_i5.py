"""P2R I5 - sách IASP: đơn vị soát tay = hội chứng (gồm GROUP chỉ có 1 hội chứng), tên bảng."""

from dataminer.books.book01.rules import RULES as BOOK01
from dataminer.books.iasp.rules import RULES
from dataminer.evaluation.spotcheck import Tree, code_of, units_table
from tests.books.test_iasp_p2 import BODY, H, P, _tree
from tests.unit.llm_fakes import ROOT


def test_review_units_include_group_syndrome() -> None:
    nodes = _tree(
        [
            ("GROUP XV: ARTERIAL INSUFFICIENCY IN THE LIMBS", 13.5, H),
            ("Intermittent Claudication (XV-1) and Rest Pain (XV-2)", 13.5, H),
            ("Code", BODY, H),
            ("1XX.X8", BODY, P),
            ("GROUP XVI: PAIN OF PSYCHOLOGICAL ORIGIN IN THE LOWER LIMBS (XVI-1)", 13.5, H),
            ("Code", BODY, H),
            ("6XX.X8", BODY, P),
        ]
    )
    units = RULES.review_units(nodes)
    assert [code_of(u) for u in units] == ["XV-1, XV-2", "XVI-1"]  # mục gộp; GROUP-hội chứng
    assert [u.level for u in units] == ["disease", "chapter"]
    assert [u.level for u in BOOK01.review_units(nodes)] == ["disease"]  # mặc định: chỉ disease
    _, rows = units_table(units, Tree(nodes), ["code"])  # cây chưa gán loại mục (I3)
    assert [(r["code"], r["n_sections"], r["iasp_codes"]) for r in rows] == [
        ("XV-1, XV-2", "1", "1XX.X8"),
        ("XVI-1", "1", "6XX.X8"),
    ]


def test_iasp_profile_names_the_table_syndromes() -> None:
    text = (ROOT / "configs" / "books" / "iasp" / "book.yaml").read_text(encoding="utf-8")
    assert "unit_name: syndromes" in text
