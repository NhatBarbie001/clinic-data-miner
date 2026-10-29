"""P2R I5 - soát tay: chọn mẫu, dữ liệu 1 bệnh, trang HTML, bảng bệnh, phiếu chấm, lệnh CLI.
Số S1-S7 khớp mục 6 của docs/phases/P2R/I5_plan.md. Công cụ dùng chung → thử cả trên sách mẫu.
"""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dataminer.cli import app
from dataminer.core.config import Settings
from dataminer.evaluation import spotcheck as sc
from dataminer.evaluation.spotcheck_page import render_html, type_color
from dataminer.model.block import Block
from dataminer.model.line import Line
from dataminer.model.tree import Node
from dataminer.pipeline.p1 import run_p1
from dataminer.pipeline.p2 import p2_dir, run_p2
from tests.conftest import SampleBookFor
from tests.unit.test_p2_pipeline import project

runner = CliRunner()


# ---------------------------------------------------------------- cây tự dựng


def node(nid: str, level: str, parent: str | None, order: int = 0, **kw: object) -> Node:
    title = str(kw.pop("title", nid))
    return Node(id=nid, level=level, parent_id=parent, order=order, title=title,  # type: ignore[arg-type]
                title_norm=title.lower(), display_title=title, path=[nid], page_start=1,
                page_end=1, **kw)  # type: ignore[arg-type]  # fmt: skip


def forest(sizes: dict[str, int]) -> tuple[list[Node], sc.Tree]:
    """Sách tự dựng: mỗi phần (part) có `sizes[part]` bệnh."""
    nodes = [node("book", "book", None)]
    for p, count in sizes.items():
        nodes.append(node(f"p{p}", "part", "book", numbering=p))
        nodes.append(node(f"c{p}", "chapter", f"p{p}"))
        nodes += [node(f"d{p}{i}", "disease", f"c{p}", i) for i in range(count)]
    return nodes, sc.Tree(nodes)


# ---------------------------------------------------------------- S1 chọn mẫu


def test_allocate_is_proportional_and_covers_every_group() -> None:
    sizes = {"A": 41, "B": 67, "D": 40, "E": 34, "F": 87, "G": 48, "H": 18}  # IASP thật
    assert sc.allocate(sizes, 10) == {"A": 1, "B": 2, "D": 1, "E": 1, "F": 3, "G": 1, "H": 1}
    assert sc.allocate({"A": 100, "B": 1}, 2) == {"A": 1, "B": 1}  # nhóm nhỏ vẫn có 1 lượt
    assert sc.allocate({"A": 2, "B": 1}, 10) == {"A": 2, "B": 1}  # không vượt số bệnh có
    assert sum(sc.allocate({"A": 5, "B": 5, "C": 5}, 2).values()) == 2  # n < số nhóm


def test_choose_sample_is_seeded_spread_and_skips_flagged() -> None:
    nodes, tree = forest({"A": 30, "B": 30, "C": 40})
    units = [n for n in nodes if n.level == "disease"]
    units[0].flags = ["missing_syndrome_title"]
    units[1].flags = ["no_iasp_code"]  # cờ không nói gì về chất lượng tách → vẫn được chọn
    first = sc.choose_sample(units, tree, 10, seed=2026)
    assert [u.id for u in first] == [u.id for u in sc.choose_sample(units, tree, 10, seed=2026)]
    assert [u.id for u in first] != [u.id for u in sc.choose_sample(units, tree, 10, seed=1)]
    assert len({u.id for u in first}) == 10 and units[0] not in first
    assert sorted(tree.stratum(u) for u in first) == ["A"] * 3 + ["B"] * 3 + ["C"] * 4
    order = [units.index(u) for u in first]
    assert order == sorted(order)  # theo thứ tự đọc
    assert sc.eligible(units[1]) and not sc.eligible(units[0])


# ---------------------------------------------------------------- S3 dữ liệu 1 bệnh


def line(lid: str, page: int, bbox: tuple[float, float, float, float]) -> Line:
    return Line(id=lid, page=page, index=0, text=lid, bbox=bbox, size=10.0, font="T", bold=False,
                zone="body", page_width=612.0, page_height=792.0)  # fmt: skip


def block(bid: str, text: str, line_ids: list[str], kind: str = "paragraph") -> Block:
    return Block(id=bid, kind=kind, text=text, text_rules=text, page_start=1, page_end=1,  # type: ignore[arg-type]
                 line_ids=line_ids, bbox=(0, 0, 1, 1), x0=0, font_size=10)  # fmt: skip


def small_unit() -> tuple[sc.Tree, dict[str, Block], dict[str, Line]]:
    nodes = [
        node("book", "book", None),
        node("d", "disease", "book", title="Tumors <b>&", heading_block_id="bh",
             block_ids=["b0"], numbering="XI-1", attrs={"iasp_codes": ["102.X4b"]}),
        node("s1", "section", "d", 0, title="Definition", heading_block_id="h1",
             block_ids=["b1", "b2"], section_type="definition"),
        node("s2", "section", "d", 1, title="Criteria", heading_block_id="h2", block_ids=[],
             section_type="diagnosis"),
        node("s21", "subsection", "s2", 0, title="1. History", heading_block_id="h3",
             block_ids=["b3"], section_type="diagnosis"),
    ]  # fmt: skip
    lines = {
        "l0": line("l0", 137, (306.0, 79.2, 612.0, 158.4)),
        "l1": line("l1", 137, (65, 100, 300, 110)),
        "l2": line("l2", 137, (65, 112, 300, 122)),
        "l3": line("l3", 138, (65, 50, 300, 60)),
    }
    blocks = {
        "bh": block("bh", "Tumors <b>&", ["l0"], "heading"),
        "b0": block("b0", "Intro </script>", ["l1"]),
        "h1": block("h1", "Definition", ["l1"], "heading"),
        "b1": block("b1", "Progressive aching.", ["l2"]),
        "b2": block("b2", "Second paragraph.", ["l2"]),
        "h2": block("h2", "Criteria", ["l2"], "heading"),
        "h3": block("h3", "1. History", ["l3"], "heading"),
        "b3": block("b3", "Widespread pain.", ["l3"], "list_item"),
    }
    blocks["b3"].marker = "1."  # mục danh sách: ký hiệu lưu riêng, trang soát phải hiện lại
    return sc.Tree(nodes), blocks, lines


def test_build_view_parts_boxes_pages() -> None:
    tree, blocks, lines = small_unit()
    view = sc.build_view(tree.by_id["d"], tree, blocks, lines)
    assert [(p.node_id, p.depth, p.section_type) for p in view.parts] == [
        ("d", 0, None), ("s1", 1, "definition"), ("s2", 1, "diagnosis"), ("s21", 2, "diagnosis"),
    ]  # fmt: skip
    assert [p.texts for p in view.parts] == [
        ["Intro </script>"],
        ["Progressive aching.", "Second paragraph."],
        [],
        ["1. Widespread pain."],
    ]
    assert view.pages == [137, 138] and view.n_blocks == 8  # mọi block của nhánh, mỗi cái 1 lần
    title_box = next(b for b in view.boxes if b.node_id == "d")
    assert (title_box.left, title_box.top, title_box.width, title_box.height) == (50, 10, 50, 10)
    assert all(b.left >= 0 and b.left + b.width <= 100.001 for b in view.boxes)  # S2: trong khổ
    assert view.code == "XI-1" and view.attrs == {"iasp_codes": ["102.X4b"]}


# ---------------------------------------------------------------- S4 HTML


def test_html_escapes_book_text_and_counts_checkboxes() -> None:
    tree, blocks, lines = small_unit()
    view = sc.build_view(tree.by_id["d"], tree, blocks, lines)
    meta: dict[str, object] = {"book_id": "iasp", "nodes_sha256": "abc", "seed": 1, "n": 1}
    page = render_html([view], [view], book_title="t<x>", unit_label="hội chứng", meta=meta)
    assert "Tumors &lt;b&gt;&amp;" in page and "<b>&</b>" not in page
    assert "Intro &lt;/script&gt;" in page and "t&lt;x&gt;" in page
    assert page.count('type="checkbox"') == 4  # chỉ mẫu có ô chấm; phần xem thêm thì không
    assert page.count("<script") == 2  # meta + mã trang; chữ sách không mở thêm thẻ nào
    embedded = page.split('<script id="meta" type="application/json">')[1].split("</script>")[0]
    assert json.loads(embedded)["criteria"] == list(sc.CRITERIA)
    assert 'src="pages/p0137.jpg"' in page and 'src="pages/p0138.jpg"' in page
    assert type_color("definition") != type_color("diagnosis") != type_color(None)
    hostile = render_html([view], [], book_title="t", unit_label="x",
                          meta={**meta, "book_id": "a</script><script>alert(1)"})  # fmt: skip
    assert hostile.count("</script>") == 2  # dữ liệu nhúng không đóng được thẻ <script> sớm


# ---------------------------------------------------------------- bảng bệnh


def test_units_table() -> None:
    tree, _, _ = small_unit()
    unit = tree.by_id["d"]
    columns, rows = sc.units_table([unit], tree, ["definition", "diagnosis", "code"])
    assert columns[:2] == ["code", "title"] and "has_code" in columns and "iasp_codes" in columns
    assert (
        rows[0]["code"] == "XI-1" and rows[0]["has_code"] == "" and rows[0]["has_definition"] == "✓"
    )
    assert rows[0]["n_sections"] == "3" and rows[0]["iasp_codes"] == "102.X4b"


# ---------------------------------------------------------------- S5 phiếu chấm


def write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8-sig")
    return path


HEADER = "unit_id,code,title,pdf_pages,ok_title,ok_boundary,ok_sections,ok_columns,note\n"


def rows_for(results: list[str]) -> str:
    return HEADER + "".join(f"u{i},C-{i},T{i},1,{r}\n" for i, r in enumerate(results))


def test_score_pass_fail_unscored(tmp_path: Path) -> None:
    ids = [f"u{i}" for i in range(10)]
    ok = "1,1,1,1,"
    nine = sc.read_review(write(tmp_path / "a.csv", rows_for([ok] * 9 + ["1,0,1,1,lẫn 2 dòng"])))
    result = sc.score(nine, ids, 0.9)
    assert result.check.passed and result.check.value == "9/10 đạt"
    assert result.failed == ["C-9 T9: sai Đúng ranh giới - lẫn 2 dòng"]
    eight = sc.read_review(write(tmp_path / "b.csv", rows_for([ok] * 8 + ["0,1,1,1,"] * 2)))
    assert not sc.score(eight, ids, 0.9).check.passed
    open_ = sc.read_review(write(tmp_path / "c.csv", rows_for([ok] * 9 + [",,,,"])))
    res = sc.score(open_, ids, 0.9)
    assert not res.check.passed and res.unscored == ["C-9 T9"]


def test_score_reads_excel_semicolons_and_rejects_bad_files(tmp_path: Path) -> None:
    semi = (HEADER + "u0,C-0,T0,1,1,1,1,1,\n").replace(",", ";")
    assert sc.score(sc.read_review(write(tmp_path / "s.csv", semi)), ["u0"], 0.9).check.passed
    with pytest.raises(sc.SpotcheckError, match="chỉ nhận 0 hoặc 1"):
        sc.score(sc.read_review(write(tmp_path / "x.csv", rows_for(["1,1,x,1,"]))), ["u0"], 0.9)
    with pytest.raises(sc.SpotcheckError, match="không thuộc mẫu"):
        sc.score(sc.read_review(write(tmp_path / "o.csv", rows_for(["1,1,1,1,"]))), ["zz"], 0.9)
    with pytest.raises(sc.SpotcheckError, match="thiếu cột"):
        sc.read_review(write(tmp_path / "m.csv", "unit_id,note\nu0,\n"))
    with pytest.raises(sc.SpotcheckError, match="Không có phiếu"):
        sc.read_review(tmp_path / "none.csv")


# ---------------------------------------------------------------- S6-S7 lệnh CLI trên sách mẫu


@pytest.fixture
def built(tmp_path: Path, sample_book_for: SampleBookFor) -> Settings:
    settings = project(tmp_path, sample_book_for)
    run_p1(settings, use_llm=False)
    run_p2(settings, use_llm=False)
    return settings


def test_cli_spotcheck_and_score_on_sample_book(built: Settings) -> None:
    root = ["--root", str(built.root)]
    nodes = p2_dir(built) / "nodes.jsonl"
    before = nodes.read_bytes()
    out = runner.invoke(app, ["p2", "spotcheck", *root, "--n", "2", "--dpi", "50"])
    assert out.exit_code == 0, out.output
    folder = p2_dir(built) / "spotcheck"
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    assert len(meta["sample"]) == 2 and (folder / "index.html").is_file()
    assert sorted(p.name for p in (folder / "pages").iterdir())  # có ảnh trang
    assert (p2_dir(built) / "diseases.csv").is_file()  # tên mặc định (sách mẫu)
    assert nodes.read_bytes() == before  # S7: chỉ đọc, không đổi cây

    review = folder / "review.csv"
    assert runner.invoke(app, ["p2", "spotcheck", "score", *root]).exit_code == 1  # chưa chấm
    text = review.read_text(encoding="utf-8-sig").replace(",,,,,", ",1,1,1,1,")
    review.write_text(text, encoding="utf-8-sig")
    scored = runner.invoke(app, ["p2", "spotcheck", "score", *root])
    assert scored.exit_code == 0 and "2/2 đạt" in scored.output
    assert "2/2 đạt" in (folder / "score.md").read_text(encoding="utf-8")

    again = runner.invoke(app, ["p2", "spotcheck", *root, "--n", "2", "--dpi", "50"])
    assert "giữ nguyên" in again.output and review.read_text(encoding="utf-8-sig") == text

    nodes.write_bytes(before + b"\n")  # cây chạy lại sau khi soát → phiếu cũ
    stale = runner.invoke(app, ["p2", "spotcheck", "score", *root])
    assert stale.exit_code == 1 and "bản cây cũ" in stale.output


def test_cli_spotcheck_rejects_unknown_code(built: Settings) -> None:
    out = runner.invoke(app, ["p2", "spotcheck", "--root", str(built.root), "--codes", "ZZ-9"])
    assert out.exit_code == 1 and "ZZ-9" in out.output
