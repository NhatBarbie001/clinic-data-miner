"""P1.6 - Pipeline `dm p1`: chạy, chạy lại xác định (G10), đánh giá, báo cáo, duyệt tay qua CLI.

LLM giả lập trả về văn bản sạch của đáp án (oracle) - nên mọi chỉ tiêu phải đạt, và mọi khác
biệt đều do pipeline/CLI chứ không do LLM. Số (#) khớp mục 6 của P1.6_plan.md.
"""

import csv
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import httpx
import pytest
from typer.testing import CliRunner

from dataminer.cli import app
from dataminer.core.config import Settings
from dataminer.core.io import read_json, read_jsonl
from dataminer.core.llm_client import LLMClient
from dataminer.devtools.oracle_fix import oracle_outputs
from dataminer.evaluation.p1_eval import all_pass, evaluate_p1
from dataminer.ingest.pipeline import p1_dir, run_p1
from dataminer.model.block import Block
from dataminer.model.line import Line
from tests.conftest import SampleBookFor
from tests.unit.llm_fakes import ROOT, SleepRecorder, make_settings, ok

runner = CliRunner()


def project(tmp: Path, book_for: SampleBookFor, **env: str) -> Settings:
    for folder, names in (
        ("configs", ("default.yaml", "models.yaml", "glossary.yaml")),
        ("prompts", ("p1_fix_ocr.md",)),
    ):
        (tmp / folder).mkdir(parents=True, exist_ok=True)
        for name in names:
            shutil.copy(ROOT / folder / name, tmp / folder / name)
    raw = tmp / "data" / "raw"
    if not (raw / "book01.pdf").exists():
        raw.mkdir(parents=True, exist_ok=True)
        book = book_for(7)
        shutil.copy(book.pdf_path, raw / "book01.pdf")
        shutil.copy(book.truth_path, raw / "book01.truth.json")
    return make_settings(tmp, **env)


class OracleLLM:
    """Trả văn bản sạch của đáp án cho từng id; đếm request."""

    def __init__(self, outputs: dict[str, str]) -> None:
        self.outputs = outputs
        self.requests = 0

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests += 1
        items = json.loads(json.loads(request.content)["messages"][1]["content"])["items"]
        answer = [{"id": it["id"], "text": self.outputs[it["id"]]} for it in items]
        return ok(json.dumps({"items": answer}, ensure_ascii=False))


def oracle_for(settings: Settings, truth: dict[str, Any]) -> OracleLLM:
    """Chạy --no-llm để có block + dòng nội dung, rồi dựng output 'hoàn hảo' cho chúng."""
    run_p1(settings, use_llm=False)
    out = p1_dir(settings)
    blocks = list(read_jsonl(out / "blocks_rules.jsonl", Block))
    lines = list(read_jsonl(out / "content_lines.jsonl", Line))
    return OracleLLM(oracle_outputs(blocks, lines, truth))


def client(settings: Settings, fake: OracleLLM) -> LLMClient:
    return LLMClient(settings, transport=httpx.MockTransport(fake), sleep=SleepRecorder())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def truth_of(settings: Settings) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(
        (settings.paths.raw_dir / "book01.truth.json").read_text(encoding="utf-8")
    )
    return data


# ---------------------------------------------------------------- #1 --no-llm


def test_01_run_without_llm(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    settings = project(tmp_path, sample_book_for)
    result = run_p1(settings, use_llm=False)
    out = p1_dir(settings)
    blocks = list(read_jsonl(out / "blocks.jsonl", Block))
    assert result.pages == (4, 9)
    assert len(blocks) == result.counts["blocks"] == 85
    assert all(b.text == b.text_rules for b in blocks)
    manifest = read_json(out / "manifest.json")
    assert manifest["status"] == "success"
    assert {o["path"] for o in manifest["outputs"]} == {
        f"data/p1_clean/{n}"
        for n in (
            "lines.jsonl",
            "content_lines.jsonl",
            "blocks_rules.jsonl",
            "blocks_fixed.jsonl",
            "blocks.jsonl",
            "furniture.json",
        )
    }
    assert manifest["prompts"] == {}  # không dùng LLM
    report = evaluate_p1(out, truth_of(settings))
    assert all(
        report[g]["pass"] for g in ("G1_furniture", "G2_printed_pages", "G3_blocks", "G4_tables")
    )
    assert not report["G5_wer"]["pass"]  # chưa sửa OCR


# ---------------------------------------------------------------- #2 đầu-cuối với LLM giả lập


def test_02_full_run_with_oracle_llm_passes_all_gates(
    tmp_path: Path, sample_book_for: SampleBookFor
) -> None:
    settings = project(tmp_path, sample_book_for)
    fake = oracle_for(settings, truth_of(settings))
    result = run_p1(settings, client=client(settings, fake))
    assert fake.requests == 6
    assert result.counts["fixes_rejected"] == 2  # đúng 2 số liệu bị chặn
    assert result.pending_review == 2
    manifest = read_json(p1_dir(settings) / "manifest.json")
    assert manifest["prompts"] == {"p1_fix_ocr": "v1"}
    report = evaluate_p1(p1_dir(settings), truth_of(settings))
    assert all_pass(report), {k: v for k, v in report.items() if not v["pass"]}


# ---------------------------------------------------------------- #3-4 chạy tiếp, tái lập (G10)


def test_04_rerun_identical_and_free(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    settings = project(tmp_path, sample_book_for)
    fake = oracle_for(settings, truth_of(settings))
    run_p1(settings, client=client(settings, fake))
    out = p1_dir(settings)
    first = (sha(out / "blocks.jsonl"), sha(out / "blocks_fixed.jsonl"))

    fake.requests = 0
    run_p1(settings, client=client(settings, fake))  # tiến độ → không gọi lại
    assert fake.requests == 0
    assert (sha(out / "blocks.jsonl"), sha(out / "blocks_fixed.jsonl")) == first

    replay = project(tmp_path, sample_book_for, DM__LLM__MODE="replay")
    run_p1(replay, force=True, client=client(replay, fake))  # bỏ tiến độ, chỉ đọc cache
    assert fake.requests == 0
    assert (sha(out / "blocks.jsonl"), sha(out / "blocks_fixed.jsonl")) == first


def test_03_interrupted_run_resumes(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    settings = project(tmp_path, sample_book_for, DM__LLM__CONCURRENCY="1")
    fake = oracle_for(settings, truth_of(settings))
    calls = {"n": 0}

    def crash_after_three(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] > 3:
            return httpx.Response(400, json={"error": {"message": "giả lập lỗi"}})
        return fake(request)

    crashing = LLMClient(
        settings, transport=httpx.MockTransport(crash_after_three), sleep=SleepRecorder()
    )
    with pytest.raises(Exception, match="400"):
        run_p1(settings, client=crashing)
    manifest = read_json(p1_dir(settings) / "manifest.json")
    assert manifest["status"] == "failed"

    fake.requests = 0
    refresh = project(tmp_path, sample_book_for, DM__LLM__MODE="refresh")  # không nhờ cache
    run_p1(refresh, client=client(refresh, fake))
    assert fake.requests == 6 - 3  # chỉ các trang còn lại


# ---------------------------------------------------------------- #5 phạm vi trang


def test_05_pages_option(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    settings = project(tmp_path, sample_book_for)
    result = run_p1(settings, pages=(6, 7), use_llm=False)
    lines = list(read_jsonl(p1_dir(settings) / "lines.jsonl", Line))
    assert {ln.page for ln in lines} == {6, 7}
    assert result.counts["pages"] == 2


def test_scope_all(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    settings = project(tmp_path, sample_book_for)
    assert run_p1(settings, scope="all", use_llm=False).pages == (1, 9)


# ---------------------------------------------------------------- #6-7 CLI eval, report


def test_06_cli_eval_exit_codes(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    settings = project(tmp_path, sample_book_for)
    root = ["--root", str(tmp_path)]
    no_result = runner.invoke(app, ["p1", "eval", *root])
    assert no_result.exit_code == 1
    assert "dm p1 run" in no_result.output

    fake = oracle_for(settings, truth_of(settings))
    run_p1(settings, client=client(settings, fake))
    good = runner.invoke(app, ["p1", "eval", *root])
    assert good.exit_code == 0, good.output
    assert "ĐẠT mọi chỉ tiêu G1-G9" in good.output
    assert (p1_dir(settings) / "eval.json").is_file()

    wrong = truth_of(settings)
    for page in wrong["pages"]:
        if page["pdf_page"] == 5:
            page["printed_page"] = 99
    bad_truth = tmp_path / "wrong.truth.json"
    bad_truth.write_text(json.dumps(wrong, ensure_ascii=False), encoding="utf-8")
    bad = runner.invoke(app, ["p1", "eval", *root, "--truth", str(bad_truth)])
    assert bad.exit_code == 1
    assert "CHƯA ĐẠT" in bad.output


def test_07_report_sections(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    settings = project(tmp_path, sample_book_for)
    fake = oracle_for(settings, truth_of(settings))
    run_p1(settings, client=client(settings, fake))
    root = ["--root", str(tmp_path)]
    assert runner.invoke(app, ["p1", "eval", *root]).exit_code == 0
    assert runner.invoke(app, ["p1", "report", *root]).exit_code == 0
    text = (p1_dir(settings) / "report.md").read_text(encoding="utf-8")
    for heading in (
        "## 1. Tổng quan",
        "## 2. Chỉ tiêu",
        "## 3. Trước / sau",
        "## 4. Mục chờ duyệt (2)",
    ):
        assert heading in text
    assert "**viêm**" in text  # token đã sửa được in đậm
    assert "| G8 số liệu không đổi nếu chưa qua duyệt | ✅ |" in text


# ---------------------------------------------------------------- duyệt tay qua CLI + mẫu kiểm tra


def test_cli_review_roundtrip_with_audit(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    settings = project(tmp_path, sample_book_for)
    fake = oracle_for(settings, truth_of(settings))
    run_p1(settings, client=client(settings, fake))
    root = ["--root", str(tmp_path)]
    exported = runner.invoke(app, ["p1", "review", "export", "--audit", "0.1", *root])
    assert exported.exit_code == 0, exported.output
    assert "2 mục cần quyết định + 4 mục kiểm tra mẫu" in exported.output

    path = p1_dir(settings) / "review" / "review_queue.csv"
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        row["decision"] = "accept" if row["priority"] == "1-SỐ LIỆU" else "keep"
        row["reviewer"] = "người thử"
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    imported = runner.invoke(app, ["p1", "review", "import", str(path), *root])
    assert imported.exit_code == 0, imported.output
    assert "nhập 6 quyết định · còn chờ 0" in imported.output
    blocks = list(read_jsonl(p1_dir(settings) / "blocks.jsonl", Block))
    assert sum(len(b.reviews) for b in blocks) == 6
    assert any("Paracetamol 500 mg" in b.text for b in blocks)

    # chạy lại toàn bộ P1 → quyết định tự áp lại; mẫu kiểm tra không hỏi lại mục đã duyệt
    run_p1(settings, client=client(settings, fake))
    again = runner.invoke(app, ["p1", "review", "export", "--audit", "0.1", *root])
    assert "0 mục cần quyết định" in again.output
    with path.open(encoding="utf-8-sig", newline="") as fh:
        second = {row["item_id"] for row in csv.DictReader(fh)}
    reviewed = {row["item_id"] for row in rows}
    assert second  # vẫn còn thay đổi chưa kiểm tra → có mẫu mới
    assert not second & reviewed  # không hỏi lại mục đã duyệt


def test_audit_sample_deterministic_and_keep_edit_only(
    tmp_path: Path, sample_book_for: SampleBookFor
) -> None:
    from dataminer.ingest.review import ReviewError, audit_sample, export_csv, import_csv

    settings = project(tmp_path, sample_book_for)
    fake = oracle_for(settings, truth_of(settings))
    run_p1(settings, client=client(settings, fake))
    blocks = list(read_jsonl(p1_dir(settings) / "blocks.jsonl", Block))
    a, b = audit_sample(blocks, 0.1), audit_sample(blocks, 0.1)
    assert [i.item_id for i in a] == [i.item_id for i in b]
    assert all(i.priority == "4-KIỂM TRA MẪU" for i in a)
    assert len(audit_sample(blocks, 1.0)) > len(a) > 0
    assert audit_sample(blocks, 0) == []

    export_csv(a, tmp_path / "a.csv")
    with (tmp_path / "a.csv").open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    rows[0]["decision"] = "accept"  # mẫu kiểm tra không có gợi ý → chỉ keep/edit
    with (tmp_path / "a.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ReviewError, match="không có gợi ý"):
        import_csv(tmp_path / "a.csv", a)


def test_run_missing_pdf(tmp_path: Path) -> None:
    for folder, names in (("configs", ("default.yaml", "models.yaml", "glossary.yaml")),):
        (tmp_path / folder).mkdir()
        for name in names:
            shutil.copy(ROOT / folder / name, tmp_path / folder / name)
    result = runner.invoke(app, ["p1", "run", "--root", str(tmp_path)])
    assert result.exit_code == 1
    assert "make-sample-book" in result.output


def test_force_discards_progress(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    """Ở chế độ refresh (không dùng cache): không --force → tiến độ bỏ qua mọi lô (0 lời gọi);
    --force → bỏ tiến độ → gọi lại đủ 6 lô. Phân biệt được --force có tác dụng hay không."""
    settings = project(tmp_path, sample_book_for)
    fake = oracle_for(settings, truth_of(settings))
    run_p1(settings, client=client(settings, fake))
    refresh = project(tmp_path, sample_book_for, DM__LLM__MODE="refresh")
    fake.requests = 0
    run_p1(refresh, client=client(refresh, fake))
    assert fake.requests == 0
    run_p1(refresh, force=True, client=client(refresh, fake))
    assert fake.requests == 6
