"""P2.6 - `dm p2 run / eval / report`, tái lập, đầu-cuối. Số (#) khớp mục 6 của
docs/phases/P2/P2.6_plan.md."""

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from dataminer.cli import app
from dataminer.core.config import Settings
from dataminer.core.io import read_json, read_jsonl, write_jsonl
from dataminer.core.llm_client import LLMClient
from dataminer.evaluation.truth.p2_eval import GATE_NAMES
from dataminer.model.tree import Node
from dataminer.pipeline.p1 import p1_dir, run_p1
from dataminer.pipeline.p2 import OUTPUTS, p2_dir, run_p2
from tests.conftest import SampleBookFor
from tests.unit.llm_fakes import ROOT, SleepRecorder, copy_configs, make_settings, ok
from tests.unit.test_p1_pipeline import client as p1_client
from tests.unit.test_p1_pipeline import oracle_for, truth_of

runner = CliRunner()


def project(tmp: Path, book_for: SampleBookFor) -> Settings:
    """Dự án tạm: cấu hình + prompt + từ điển thật, sách mẫu seed 7."""
    copy_configs(tmp)
    if not (tmp / "prompts").exists():
        shutil.copytree(ROOT / "prompts", tmp / "prompts")
    (tmp / "pyproject.toml").write_text("", encoding="utf-8")
    raw = tmp / "data" / "books" / "book01" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    book = book_for(7)
    shutil.copy(book.pdf_path, raw / "book01.pdf")
    shutil.copy(book.truth_path, raw / "book01.truth.json")
    return make_settings(tmp)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CountingLLM:
    """LLM giả lập chỉ để ĐẾM lời gọi (sách mẫu: P2 không được gọi lần nào)."""

    def __init__(self) -> None:
        self.requests = 0

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests += 1
        return ok('{"level": "other", "reason": "x"}')


@pytest.fixture
def p1_rules(tmp_path: Path, sample_book_for: SampleBookFor) -> Settings:
    """P1 chạy --no-llm (chỉ quy tắc) - đủ để P2 chạy."""
    settings = project(tmp_path, sample_book_for)
    run_p1(settings, use_llm=False)
    return settings


# ---------------------------------------------------------------- #1-2 chạy, tái lập


def test_01_run_writes_outputs_and_manifest(p1_rules: Settings) -> None:
    fake = CountingLLM()
    client = LLMClient(p1_rules, transport=httpx.MockTransport(fake), sleep=SleepRecorder())
    result = run_p2(p1_rules, client=client)
    out = p2_dir(p1_rules)
    assert all((out / name).is_file() for name in OUTPUTS)
    assert fake.requests == 0  # có bật LLM nhưng sách mẫu không có gì mơ hồ
    c = result.counts
    assert (c["nodes_chapter"], c["nodes_disease"], c["nodes_section"], c["nodes_subsection"]) == (
        2,
        3,
        19,
        3,
    )
    assert (c["headings_rules"], c["headings_toc"], c["headings_llm"]) == (22, 5, 0)
    assert (c["sections_map"], c["section_proposals"]) == (22, 0)
    manifest = read_json(out / "manifest.json")
    assert manifest["status"] == "success" and manifest["phase"] == "p2_tree"
    assert manifest["prompts"] == {}  # không lời gọi nào → không ghi prompt
    inputs = [Path(f["path"]).name for f in manifest["inputs"]]
    assert inputs == ["blocks.jsonl", "book01.pdf", "section_map.yaml"]
    outputs = {Path(f["path"]).name: f for f in manifest["outputs"]}
    assert list(outputs) == list(OUTPUTS)
    assert outputs["nodes.jsonl"]["sha256"] == result.nodes_sha256 == sha(out / "nodes.jsonl")
    assert outputs["nodes.jsonl"]["records"] == 28
    assert manifest["llm"]["calls"] == 0 and result.llm_cost_usd == 0


def test_02_rerun_is_byte_identical(p1_rules: Settings) -> None:
    out = p2_dir(p1_rules)
    first = run_p2(p1_rules, use_llm=False)
    before = {name: sha(out / name) for name in OUTPUTS}
    second = run_p2(p1_rules, use_llm=False)
    assert {name: sha(out / name) for name in OUTPUTS} == before  # G8
    assert second.nodes_sha256 == first.nodes_sha256 and second.run_id != first.run_id
    assert len(list((out / "runs").glob("*.json"))) == 2  # mỗi lần chạy một manifest


# ---------------------------------------------------------------- #3 eval


def test_03_eval_exit_codes(p1_rules: Settings) -> None:
    root = ["--root", str(p1_rules.root)]
    not_run = runner.invoke(app, ["p2", "eval", *root])
    assert not_run.exit_code == 1 and "dm p2 run" in not_run.output

    assert runner.invoke(app, ["p2", "run", *root, "--no-llm"]).exit_code == 0
    no_golden = runner.invoke(app, ["p2", "eval", *root])
    assert no_golden.exit_code == 1  # G7 không được bỏ qua im lặng
    assert "✗ G7_golden" in no_golden.output and "dm p2 golden" in no_golden.output
    report = read_json(p2_dir(p1_rules) / "eval.json")
    assert list(report) == list(GATE_NAMES)  # đủ G1-G7, không chỉ tiêu nào bị bỏ sót
    assert all(report[g]["pass"] for g in ("G1_toc", "G2_heading_levels", "G6_invariants"))

    wrong = truth_of(p1_rules)
    wrong["toc"][1]["printed_page"] = 2
    bad_truth = p1_rules.root / "wrong.truth.json"
    bad_truth.write_text(json.dumps(wrong, ensure_ascii=False), encoding="utf-8")
    bad = runner.invoke(app, ["p2", "eval", *root, "--truth", str(bad_truth)])
    assert bad.exit_code == 1 and "✗ G1_toc" in bad.output and "CHƯA ĐẠT" in bad.output


# ---------------------------------------------------------------- #4 báo cáo


def test_04_report_sections_and_matrix(p1_rules: Settings) -> None:
    root = ["--root", str(p1_rules.root)]
    assert "dm p2 run" in runner.invoke(app, ["p2", "report", *root]).output
    assert runner.invoke(app, ["p2", "run", *root, "--no-llm"]).exit_code == 0
    assert runner.invoke(app, ["p2", "report", *root]).exit_code == 0
    text = (p2_dir(p1_rules) / "tree_report.md").read_text(encoding="utf-8")
    for heading in (
        "## 1. Tổng quan",
        "## 2. Đối chiếu mục lục",
        "## 3. Ma trận bệnh × loại mục",
        "## 4. Cảnh báo cần người xem",
        "## 5. Cây",
    ):
        assert heading in text
    assert "**2 chương · 3 bệnh · 19 mục · 3 mục con**" in text
    assert "| Viêm khớp dạng thấp | 4–5 | 1–2 | 9 |" in text
    rows = {
        ln.split(" | ")[0][2:]: ln
        for ln in text.splitlines()
        if ln.startswith("| Viêm") or ln.startswith("| Thoái")
    }
    header = next(ln for ln in text.splitlines() if ln.startswith("| Bệnh | definition"))
    col = header.split(" | ").index("complication")
    assert [
        rows[d].split(" | ")[col] for d in rows if "| ✓ |" in rows[d] or "| — |" in rows[d]
    ] == [
        "—",
        "—",
        "✓",
    ]  # complication chỉ ở bệnh 3
    assert "chỉ có ở một số bệnh** (P4 phải chấp nhận trường trống): `risk_factor`" in text
    assert "| Chương 2. Bệnh tiêu hỏa | chapter | 5 | ✓ Chương 2. Bệnh tiêu hóa | ✓ PDF 8 |" in text
    assert "✅ Không có cảnh báo" in text


def test_04b_report_lists_warnings(p1_rules: Settings) -> None:
    """Cài cờ + một mục rất dài vào nodes.jsonl → phần 4 phải liệt kê."""
    run_p2(p1_rules, use_llm=False)
    out = p2_dir(p1_rules)
    nodes = list(read_jsonl(out / "nodes.jsonl", Node))
    target = next(n for n in nodes if n.level == "section" and n.text)
    target.flags.append("section_type_fuzzy")
    long_one = next(n for n in nodes if n.level == "section" and n.text and n is not target)
    long_one.text = "từ " * 2000
    write_jsonl(out / "nodes.jsonl", nodes)
    from dataminer.structure.report import render_tree_report

    toc = read_json(out / "toc.json")
    toc["entries"][1]["pdf_page"] = 5  # mục lục ghi sai trang của VKDT
    del toc["entries"][2]  # mục lục "thiếu" Thoái hóa khớp gối
    (out / "toc.json").write_text(json.dumps(toc, ensure_ascii=False), encoding="utf-8")

    text = render_tree_report(out)
    assert "`section_type_fuzzy`: loại mục từ khớp gần" in text
    assert "dài 2000 từ" in text and "Không có cảnh báo" not in text
    assert "| Viêm khớp dạng thấp | disease | 1 | ✓ Viêm khớp dạng thấp | ✗ cây PDF 4 ≠ 5 |" in text
    assert "**không có trong mục lục**: `Thoái hóa khớp gối`" in text


# ---------------------------------------------------------------- #5 thiếu đầu vào


def test_05_missing_p1_output(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    project(tmp_path, sample_book_for)
    result = runner.invoke(app, ["p2", "run", "--root", str(tmp_path), "--no-llm"])
    assert result.exit_code == 1 and "dm p1 run" in result.output
    assert not (tmp_path / "data" / "books" / "book01" / "p2_tree" / "nodes.jsonl").exists()


# ---------------------------------------------------------------- #6 đầu-cuối


def test_06_end_to_end_p1_oracle_to_p2_gate(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    """P1 với LLM 'hoàn hảo' (giả lập) → P2 → golden → eval: đạt G1-G7."""
    settings = project(tmp_path, sample_book_for)
    fake = oracle_for(settings, truth_of(settings))
    run_p1(settings, client=p1_client(settings, fake))
    root = ["--root", str(tmp_path)]

    # Chưa duyệt số liệu (P1 chặn "5OO"→"500") → nút còn "5OO mg" → golden PHẢI bị từ chối
    assert runner.invoke(app, ["p2", "run", *root, "--no-llm"]).exit_code == 0
    refused = runner.invoke(app, ["p2", "golden", *root])
    assert refused.exit_code == 1 and "số liệu ['500'] không có trong nút" in refused.output

    # P1.5: xuất hàng đợi → "người duyệt" điền từ đáp án → nhập (đúng đường CLI như người thật)
    from dataminer.devtools.auto_review import fill_from_truth
    from dataminer.model.block import Block
    from dataminer.model.line import Line

    queue = p1_dir(settings) / "review" / "review_queue.csv"
    assert runner.invoke(app, ["p1", "review", "export", *root]).exit_code == 0
    blocks = list(read_jsonl(p1_dir(settings) / "blocks_fixed.jsonl", Block))
    lines = list(read_jsonl(p1_dir(settings) / "content_lines.jsonl", Line))
    filled = tmp_path / "decided.csv"
    assert fill_from_truth(queue, filled, blocks, lines, truth_of(settings)) == 2
    assert runner.invoke(app, ["p1", "review", "import", str(filled), *root]).exit_code == 0

    p2 = runner.invoke(app, ["p2", "run", *root, "--no-llm"])
    assert p2.exit_code == 0, p2.output
    assert "2 chương · 3 bệnh · 19 mục · 3 mục con · 85 block" in p2.output
    assert runner.invoke(app, ["p2", "golden", *root]).exit_code == 0
    result = runner.invoke(app, ["p2", "eval", *root])
    assert result.exit_code == 0, result.output
    assert "ĐẠT mọi chỉ tiêu G1-G7" in result.output
    nodes = list(read_jsonl(p1_dir(settings).parent / "p2_tree" / "nodes.jsonl", Node))
    # P1 hoàn hảo sửa được tiêu đề "TRIỆU CHUNG" → path sạch
    assert ["Chương 1. Bệnh cơ xương khớp", "Thoái hóa khớp gối", "Triệu chứng"] in [
        n.path for n in nodes
    ]


# ---------------------------------------------------------------- #7 khởi động nhanh


def test_07_cli_startup_does_not_load_heavy_modules() -> None:
    code = (
        "import sys, dataminer.cli; "
        "print([m for m in ('pymupdf', 'dataminer.structure.pipeline', "
        "'dataminer.structure.tree_builder') if m in sys.modules])"
    )
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert out == "[]"
