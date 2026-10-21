"""P2.4 - Ánh xạ loại mục. Số (#) khớp mục 5 của docs/phases/P2/P2.4_plan.md.

Trên sách mẫu MỌI tên mục tra trúng từ điển (30/30 seed: 22/22 nguồn `map`) - các đường khớp gần,
kế thừa, LLM và vòng duyệt CHỈ được kiểm bằng cây tự dựng ở đây.
"""

import csv
import json
import shutil
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from dataminer.cli import app
from dataminer.core.config import SectionsCfg, Settings
from dataminer.core.io import read_jsonl, write_jsonl
from dataminer.core.llm_client import LLMClient
from dataminer.core.llm_types import LLMJSONError
from dataminer.core.prompts import load_prompt
from dataminer.evaluation.p2_eval import all_pass, eval_sections
from dataminer.structure.section_mapper import (
    CSV_COLUMNS,
    SectionMapError,
    export_proposals,
    import_proposals,
    load_section_map,
    lookup,
    map_sections,
    normalize_section_title,
)
from dataminer.structure.tree_builder import Node, build_tree
from tests.conftest import SampleBookFor
from tests.unit.llm_fakes import ROOT, SleepRecorder, make_settings, ok
from tests.unit.test_tree_builder import PILOT, make, pipeline

MAP_PATH = ROOT / "configs" / "section_map.yaml"
MAPPING = load_section_map(MAP_PATH)
runner = CliRunner()


def tree(spec: list[tuple[str, str]]) -> list[Node]:
    blocks, decisions = make(spec)
    return build_tree(blocks, decisions, book_id="bk").nodes


def sections(nodes: list[Node]) -> list[tuple[str, str | None, str | None]]:
    return [
        (n.title, n.section_type, n.section_source)
        for n in nodes
        if n.level in ("section", "subsection")
    ]


class FakeLLM:
    def __init__(self, answer: str) -> None:
        self.answer = answer
        self.requests: list[dict] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(json.loads(request.content))
        return ok(self.answer)


def llm(settings: Settings, fake: FakeLLM) -> tuple[LLMClient, object]:
    client = LLMClient(settings, transport=httpx.MockTransport(fake), sleep=SleepRecorder())
    return client, load_prompt(ROOT / "prompts", "p2_classify_section")


# ---------------------------------------------------------------- #1-2 trên sách mẫu


@pytest.mark.parametrize("seed", [7, 1, 6])
def test_01_pilot_all_from_dictionary(
    tmp_path: Path, sample_book_for: SampleBookFor, seed: int
) -> None:
    book = sample_book_for(seed)
    blocks, _, decisions, toc = pipeline(book.pdf_path)
    nodes = build_tree(blocks, decisions, book_id="book01", toc=toc).nodes
    fake = FakeLLM('{"section_type": "other", "reason": "x"}')
    client, prompt = llm(make_settings(tmp_path), fake)
    result = map_sections(nodes, MAPPING, client=client, prompt=prompt)  # type: ignore[arg-type]
    assert fake.requests == []  # 0 lời gọi LLM
    assert result.counts == {"map": 22, "map_fuzzy": 0, "inherited": 0, "llm": 0, "none": 0}
    assert result.proposals == [] and result.warnings == []
    report = eval_sections(nodes, book.truth, PILOT)
    assert all_pass(report), report
    g5 = report["G5_section_types"]
    assert (g5["correct"], g5["truth"], g5["other_ratio"]) == (22, 22, 0.0)


@pytest.mark.parametrize(
    ("title", "key", "expected"),
    [
        ("3. TRIỆU CHUNG", "trieu chung", "symptom"),  # lỗi dấu còn sót sau P1
        ("2. NGUYEN NHÂN", "nguyen nhan", "cause"),
        ("1. DAI CƯƠNG", "dai cuong", "definition"),
        ("3.2. Cận lâm sàng:", "can lam sang", "paraclinical"),
        ("  4.   CHẨN   ĐOÁN ", "chan doan", "diagnosis"),
        ("CHẨN ĐOÁN PHÂN BIỆT", "chan doan phan biet", "differential_diagnosis"),
    ],
)
def test_02_ocr_damaged_titles(title: str, key: str, expected: str) -> None:
    assert normalize_section_title(title) == key
    assert lookup(key, MAPPING, 0.9) == (expected, key, 1.0)


# ---------------------------------------------------------------- #3-4 không dựa sách mẫu


def test_03_fuzzy_match_threshold() -> None:
    hit = lookup("nguyen nhau", MAPPING, 0.9)  # OCR nhầm n → u: giống 0.909
    assert hit is not None and hit[:2] == ("cause", "nguyen nhan")
    assert lookup("dieu khien", MAPPING, 0.9) is None  # 0.667: không được khớp nhầm "dieu tri"
    assert lookup("trieu chimg", MAPPING, 0.9) is None  # nhầm 2 ký tự: 0.818 < 0.9

    nodes = tree([("disease", "GOUT"), ("section", "2. NGUYÊN NHÂU"), ("p", "a")])
    result = map_sections(nodes, MAPPING)
    node = nodes[2]
    assert (node.section_type, node.section_source) == ("cause", "map_fuzzy")
    assert node.flags == ["section_type_fuzzy"]
    [proposal] = result.proposals
    assert (proposal.source, proposal.key, proposal.proposal) == (
        "map_fuzzy",
        "nguyen nhau",
        "cause",
    )
    assert proposal.diseases == ["Gout"] and proposal.reason == "khớp gần 'nguyen nhan' (0.91)"


def test_04_subsection_inherits_parent_only() -> None:
    nodes = tree(
        [
            ("disease", "GOUT"),
            ("section", "3. TRIỆU CHỨNG"),
            ("subsection", "3.3. Đặc điểm"),  # không có trong từ điển → kế thừa
            ("p", "a"),
            ("section", "4. ĐẶC ĐIỂM"),  # MỤC (không phải mục con) → không được kế thừa
            ("p", "b"),
        ]
    )
    result = map_sections(nodes, MAPPING)
    assert sections(nodes) == [
        ("3. TRIỆU CHỨNG", "symptom", "map"),
        ("3.3. Đặc điểm", "symptom", "inherited"),
        ("4. ĐẶC ĐIỂM", "other", "none"),
    ]
    assert nodes[-1].flags == ["section_type_unknown"]
    assert "'4. ĐẶC ĐIỂM'" in result.warnings[0]


# ---------------------------------------------------------------- #5 LLM giả lập


FOLLOW_UP = [
    ("disease", "ĐÁI THÁO ĐƯỜNG"),
    ("section", "7. THEO DÕI SAU ĐIỀU TRỊ"),
    ("p", "Tái khám mỗi 3 tháng, theo dõi biến chứng."),
    ("disease", "TĂNG HUYẾT ÁP"),
    ("section", "6. THEO DÕI SAU ĐIỀU TRỊ"),
    ("p", "Đo huyết áp tại nhà."),
]


def test_05_llm_once_per_unknown_title(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    fake = FakeLLM('{"section_type": "prevention", "reason": "tái khám, theo dõi biến chứng"}')
    client, prompt = llm(settings, fake)
    nodes = tree(FOLLOW_UP)
    result = map_sections(nodes, MAPPING, client=client, prompt=prompt)  # type: ignore[arg-type]
    assert len(fake.requests) == 1  # 2 bệnh cùng tên mục lạ → hỏi 1 lần
    sent = json.loads(fake.requests[0]["messages"][1]["content"])
    assert sent == {
        "disease": "Đái tháo đường",
        "section_title": "7. THEO DÕI SAU ĐIỀU TRỊ",
        "parent_section": None,
        "content_start": "Tái khám mỗi 3 tháng, theo dõi biến chứng.",
    }
    assert fake.requests[0]["model"] == settings.model_for("classify").model
    assert [s[1:] for s in sections(nodes)] == [("prevention", "llm"), ("prevention", "llm")]
    assert all(n.flags == ["section_type_from_llm"] for n in nodes if n.level == "section")
    [proposal] = result.proposals
    assert proposal.diseases == ["Đái tháo đường", "Tăng huyết áp"] and len(proposal.node_ids) == 2
    assert (result.llm_calls, result.prompt) == (1, "p2_classify_section@v1")

    again = map_sections(nodes, MAPPING, client=client, prompt=prompt)  # type: ignore[arg-type]
    assert again.llm_calls == 0 and len(fake.requests) == 1  # cache
    assert all(n.flags == ["section_type_from_llm"] for n in nodes if n.level == "section")


def test_05b_llm_label_outside_set(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    fake = FakeLLM('{"section_type": "follow_up", "reason": "?"}')
    client, prompt = llm(settings, fake)
    with pytest.raises(LLMJSONError, match="sai schema"):
        map_sections(tree(FOLLOW_UP), MAPPING, client=client, prompt=prompt)  # type: ignore[arg-type]
    assert len(fake.requests) == settings.llm.json_retries + 1


def test_05c_llm_disabled(tmp_path: Path) -> None:
    fake = FakeLLM('{"section_type": "treatment", "reason": "x"}')
    client, prompt = llm(make_settings(tmp_path), fake)
    nodes = tree(FOLLOW_UP)
    result = map_sections(
        nodes,
        MAPPING,
        SectionsCfg(llm_fallback=False),
        client=client,
        prompt=prompt,  # type: ignore[arg-type]
    )
    assert fake.requests == [] and result.counts["none"] == 2


# ---------------------------------------------------------------- #6 vòng duyệt


def _fill(path: Path, decisions: dict[str, tuple[str, str]]) -> None:
    """Điền CSV như người duyệt mở bằng Excel: {normalized: (decision, edited_value)}."""
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        row["decision"], row["edited_value"] = decisions.get(row["normalized"], ("", ""))
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def test_06_review_loop_adds_to_dictionary(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    map_path = tmp_path / "section_map.yaml"
    shutil.copy(MAP_PATH, map_path)
    fake = FakeLLM('{"section_type": "prevention", "reason": "theo dõi"}')
    client, prompt = llm(settings, fake)
    nodes = tree([*FOLLOW_UP, ("section", "7. NGUYÊN NHÂU"), ("p", "c")])
    result = map_sections(nodes, load_section_map(map_path), client=client, prompt=prompt)  # type: ignore[arg-type]
    assert [p.source for p in result.proposals] == ["map_fuzzy", "llm"]

    csv_path = tmp_path / "review.csv"
    export_proposals(result.proposals, csv_path)
    assert csv_path.read_bytes().startswith(b"\xef\xbb\xbf")  # BOM: Excel đọc đúng tiếng Việt
    _fill(
        csv_path,
        {"theo doi sau dieu tri": ("edit", "treatment"), "nguyen nhau": ("accept", "")},
    )
    added = import_proposals(csv_path, result.proposals, map_path, reviewer="BS. A")
    assert added == [("nguyen nhau", "cause"), ("theo doi sau dieu tri", "treatment")]
    tail = map_path.read_text(encoding="utf-8").splitlines()[-1]
    assert tail.startswith("theo doi sau dieu tri: treatment   # thêm ")
    assert "duyệt bởi BS. A (nguồn: llm)" in tail

    rerun = map_sections(nodes, load_section_map(map_path), client=client, prompt=prompt)  # type: ignore[arg-type]
    assert rerun.counts["map"] == 3 and rerun.proposals == [] and len(fake.requests) == 1
    assert sections(nodes)[0][1:] == ("treatment", "map")  # quyết định của người duyệt thắng LLM
    assert import_proposals(csv_path, result.proposals, map_path, reviewer="x") == []  # đã có


def test_06b_import_errors_all_reported_nothing_written(tmp_path: Path) -> None:
    map_path = tmp_path / "section_map.yaml"
    shutil.copy(MAP_PATH, map_path)
    before = map_path.read_text(encoding="utf-8")
    nodes = tree([("disease", "GOUT"), ("section", "2. NGUYÊN NHÂU"), ("p", "a")])
    proposals = map_sections(nodes, MAPPING).proposals
    csv_path = tmp_path / "review.csv"
    export_proposals(proposals, csv_path)
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8-sig", newline="")))
    rows[0].update(decision="edit", edited_value="follow_up")
    rows.append({**rows[0], "decision": "maybe"})
    rows.append({**rows[0], "item_id": "sp_khong_co", "decision": "accept"})
    with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(SectionMapError) as err:
        import_proposals(csv_path, proposals, map_path, reviewer="x")
    message = str(err.value)
    assert "3 lỗi" in message
    assert "dòng 2: edited_value 'follow_up'" in message
    assert "dòng 3: decision 'maybe'" in message
    assert "dòng 4: item_id 'sp_khong_co'" in message
    assert map_path.read_text(encoding="utf-8") == before

    # khóa đã có trong từ điển với loại KHÁC → lỗi, không ghi đè
    map_path.write_text(before + "nguyen nhau: other\n", encoding="utf-8")
    _fill(csv_path, {"nguyen nhau": ("accept", "")})
    with pytest.raises(SectionMapError, match="đã có trong từ điển với loại 'other'"):
        import_proposals(csv_path, proposals, map_path, reviewer="x")


# ---------------------------------------------------------------- #7 từ điển sai định dạng


def test_07_dictionary_validation(tmp_path: Path) -> None:
    path = tmp_path / "map.yaml"
    path.write_text(
        "# chú thích\n"
        "dieu tri: treatment\n"
        "chẩn đoán: diagnosis\n"
        "3. bien chung: complication\n"
        "theo doi: follow_up\n"
        "dong sai dinh dang\n"
        "dieu tri: prevention\n",
        encoding="utf-8",
    )
    with pytest.raises(SectionMapError) as err:
        load_section_map(path)
    message = str(err.value)
    assert "5 lỗi" in message
    assert "dòng 3: khóa 'chẩn đoán' phải không dấu" in message and "viết 'chan doan'" in message
    assert "dòng 4: khóa '3. bien chung'" in message
    assert "dòng 5: loại 'follow_up' không hợp lệ" in message
    assert "dòng 6: không đúng dạng" in message
    assert "dòng 7: khóa 'dieu tri' đã có loại 'treatment'" in message
    with pytest.raises(SectionMapError, match="Không có từ điển"):
        load_section_map(tmp_path / "khong_co.yaml")


def test_07b_shipped_dictionary_is_valid() -> None:
    assert len(MAPPING) >= 20 and set(MAPPING.values()) <= {
        "definition", "cause", "risk_factor", "pathophysiology", "symptom", "paraclinical",
        "diagnosis", "differential_diagnosis", "treatment", "complication", "prognosis",
        "prevention", "other",
    }  # fmt: skip


# ---------------------------------------------------------------- #8 đối chứng âm


@pytest.fixture(scope="module")
def pilot_nodes(sample_book_for: SampleBookFor) -> tuple[list[Node], dict]:
    book = sample_book_for(7)
    blocks, _, decisions, toc = pipeline(book.pdf_path)
    nodes = build_tree(blocks, decisions, book_id="book01", toc=toc).nodes
    map_sections(nodes, MAPPING)
    return nodes, book.truth


def test_08_eval_fails_on_wrong_truth(pilot_nodes: tuple[list[Node], dict]) -> None:
    """Ngưỡng plan: ≥ 95%. Với 22 mục, 1 mục sai (95.45%) vẫn ĐẠT nhưng phải hiện trong
    `problems`; 2 mục sai (90.9%) → không đạt."""
    nodes, truth = pilot_nodes
    assert all_pass(eval_sections(nodes, truth, PILOT))
    wrong = json.loads(json.dumps(truth))
    next(h for h in wrong["headings"] if h["text"] == "4. BIẾN CHỨNG")["section_type"] = "symptom"
    one = eval_sections(nodes, wrong, PILOT)["G5_section_types"]
    assert (one["correct"], one["accuracy"], one["pass"]) == (21, round(21 / 22, 4), True)
    [problem] = one["problems"]  # tiêu đề có thể còn lỗi OCR ("BIEN CHỨNG")
    assert problem.endswith(": complication ≠ symptom")
    next(h for h in wrong["headings"] if h["text"] == "2.1. Yếu tố nguy cơ")["section_type"] = (
        "cause"
    )
    two = eval_sections(nodes, wrong, PILOT)["G5_section_types"]
    assert (two["correct"], two["pass"]) == (20, False)


def test_08b_eval_other_ratio_and_alignment(pilot_nodes: tuple[list[Node], dict]) -> None:
    nodes, truth = pilot_nodes

    def with_other(*titles: str) -> list[Node]:
        copy = [n.model_copy(deep=True) for n in nodes]
        for n in copy:
            if n.title in titles:
                n.section_type = "other"
        return copy

    one = eval_sections(with_other("2.1. Yếu tố nguy cơ"), truth, PILOT)["G5_section_types"]
    assert (one["other_ratio"], one["pass"]) == (round(1 / 22, 4), True)  # 4.5% < 5%
    two = with_other("2.1. Yếu tố nguy cơ", "3.2. Cận lâm sàng")
    assert not all_pass(eval_sections(two, truth, PILOT))
    # cô lập ngưỡng `other`: đáp án CŨNG ghi other → đúng 22/22 nhưng other = 9% ≥ 5% → không đạt
    lenient = json.loads(json.dumps(truth))
    for h in lenient["headings"]:
        if h["text"] in ("2.1. Yếu tố nguy cơ", "3.2. Cận lâm sàng"):
            h["section_type"] = "other"
    isolated = eval_sections(two, lenient, PILOT)["G5_section_types"]
    assert (isolated["correct"], isolated["other_ratio"]) == (22, round(2 / 22, 4))
    assert not isolated["pass"]
    secs = [n for n in nodes if n.level in ("section", "subsection")]
    others = [n for n in nodes if n.level not in ("section", "subsection")]
    assert "lệch thứ tự" in str(eval_sections(others + secs[1:], truth, PILOT))
    assert not all_pass(eval_sections([*nodes, secs[0]], truth, PILOT))  # thừa mục
    assert not all_pass(eval_sections([], truth, PILOT))
    assert not all_pass(eval_sections(nodes, truth, (1, 2)))  # phạm vi không có mục


# ---------------------------------------------------------------- CLI


def test_cli_sections_map_export_import(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    book = sample_book_for(7)
    make_settings(tmp_path)
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    shutil.copytree(ROOT / "prompts", tmp_path / "prompts")
    shutil.copy(MAP_PATH, tmp_path / "configs" / "section_map.yaml")
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    shutil.copy(book.pdf_path, raw / "book01.pdf")
    shutil.copy(book.truth_path, raw / "book01.truth.json")
    blocks, lines, _, _ = pipeline(book.pdf_path)
    write_jsonl(tmp_path / "data" / "p1_clean" / "blocks.jsonl", blocks)
    write_jsonl(tmp_path / "data" / "p1_clean" / "content_lines.jsonl", lines)
    root = ["--root", str(tmp_path)]

    assert runner.invoke(app, ["p2", "sections", "map", *root]).exit_code == 1  # chưa có cây
    assert runner.invoke(app, ["p2", "headings", *root, "--no-llm"]).exit_code == 0
    assert runner.invoke(app, ["p2", "tree", *root]).exit_code == 0
    good = runner.invoke(app, ["p2", "sections", "map", *root, "--eval", "--no-llm"])
    assert good.exit_code == 0, good.output
    assert "từ điển 22 · khớp gần 0 · kế thừa 0 · LLM 0 · chưa rõ 0" in good.output
    assert "✓ G5_section_types" in good.output
    out = tmp_path / "data" / "p2_tree"
    assert "[symptom]" in (out / "tree.md").read_text(encoding="utf-8")

    # Giả lập 1 tên mục còn lỗi OCR nhầm ký tự → khớp gần → duyệt → vào từ điển
    nodes = list(read_jsonl(out / "nodes.jsonl", Node))
    next(n for n in nodes if n.title == "2. NGUYÊN NHÂN").title = "2. NGUYÊN NHÂU"
    write_jsonl(out / "nodes.jsonl", nodes)
    fuzzy = runner.invoke(app, ["p2", "sections", "map", *root, "--no-llm"])
    assert "khớp gần 1" in fuzzy.output and "chờ duyệt [map_fuzzy]" in fuzzy.output
    exported = runner.invoke(app, ["p2", "sections", "export", *root])
    assert exported.exit_code == 0 and "1 đề xuất" in exported.output
    csv_path = out / "section_proposals.csv"
    _fill(csv_path, {"nguyen nhau": ("accept", "")})
    imported = runner.invoke(app, ["p2", "sections", "import", str(csv_path), *root])
    assert imported.exit_code == 0, imported.output
    assert "+ nguyen nhau: cause" in imported.output
    again = runner.invoke(app, ["p2", "sections", "map", *root, "--no-llm"])
    assert "từ điển 22 · khớp gần 0" in again.output
