"""P1.4 - Bộ sửa lỗi OCR với LLM giả lập (httpx.MockTransport). #13-#17 + đối chứng dương."""

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any

import httpx
import pytest

from dataminer.core.config import Settings
from dataminer.core.llm_client import LLMClient
from dataminer.core.llm_types import LLMError
from dataminer.core.prompts import PromptError, load_prompt
from dataminer.devtools.oracle_fix import oracle_outputs
from dataminer.devtools.sample_book import SampleBook
from dataminer.evaluation.p1_eval import eval_ocr
from dataminer.ingest.blocks import build_blocks
from dataminer.ingest.ocr_fixer import OCRFixer, plan_batches
from dataminer.ingest.page_furniture import strip_furniture
from dataminer.ingest.pdf_reader import body_font_size, read_lines
from dataminer.model.block import Block
from dataminer.model.line import Line
from tests.conftest import SampleBookFor
from tests.unit.llm_fakes import ROOT, SleepRecorder, make_settings, ok

PILOT = (4, 9)


def project(tmp: Path, **env: str) -> Settings:
    (tmp / "prompts").mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "prompts" / "p1_fix_ocr.md", tmp / "prompts" / "p1_fix_ocr.md")
    (tmp / "configs").mkdir(exist_ok=True)
    for name in ("default.yaml", "models.yaml", "glossary.yaml"):
        shutil.copy(ROOT / "configs" / name, tmp / "configs" / name)
    return make_settings(tmp, **env)


@pytest.fixture(scope="module")
def book(sample_book_for: SampleBookFor) -> SampleBook:
    return sample_book_for(7)


@pytest.fixture(scope="module")
def pilot(book: SampleBook) -> tuple[list[Block], list[Line]]:
    lines = read_lines(book.pdf_path, pages=PILOT)
    body = body_font_size(lines)
    fr = strip_furniture(lines, body, pdf_pages=list(range(PILOT[0], PILOT[1] + 1)))
    return build_blocks(
        fr.content, body, printed={p.page: p.printed_page for p in fr.pages}
    ), fr.content


class FakeLLM:
    """Trả lời theo hàm `respond(items) -> {id: text}`; ghi lại mọi request."""

    def __init__(self, respond: Any) -> None:
        self.respond = respond
        self.requests: list[dict[str, Any]] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        self.requests.append(payload)
        items = json.loads(payload["messages"][1]["content"])["items"]
        answer = self.respond(items)
        return ok(
            json.dumps(
                {"items": [{"id": k, "text": v} for k, v in answer.items()]}, ensure_ascii=False
            )
        )


def fixer_for(settings: Settings, fake: FakeLLM) -> OCRFixer:
    client = LLMClient(settings, transport=httpx.MockTransport(fake), sleep=SleepRecorder())
    return OCRFixer.from_settings(settings, client)


def echo(items: list[dict[str, str]]) -> dict[str, str]:
    return {it["id"]: it["text"] for it in items}


# ---------------------------------------------------------------- #13 payload, chia lô


def test_13_batches_per_page_and_payload(
    tmp_path: Path, pilot: tuple[list[Block], list[Line]]
) -> None:
    blocks, _ = pilot
    settings = project(tmp_path)
    fake = FakeLLM(echo)
    fixer = fixer_for(settings, fake)
    asyncio.run(fixer.fix(blocks, tmp_path / "progress.jsonl"))
    assert len(fake.requests) == len(plan_batches(blocks, 25)) == 6  # 6 trang, mỗi trang 1 lô
    p = fake.requests[0]
    assert p["temperature"] == 0.0
    assert p["reasoning"] == {"enabled": False}  # fix_ocr tắt suy luận (P0.3: tiết kiệm ~60%)
    assert p["response_format"]["json_schema"]["name"] == "FixBatch"
    assert p["messages"][0]["content"] == load_prompt(tmp_path / "prompts", "p1_fix_ocr").text
    sent = [
        it["id"] for r in fake.requests for it in json.loads(r["messages"][1]["content"])["items"]
    ]
    table = next(b for b in blocks if b.kind == "table")
    assert f"{table.id}#r2c1" in sent  # bảng gửi từng ô
    assert len(sent) == len(set(sent))


def test_13b_long_page_split_into_batches(pilot: tuple[list[Block], list[Line]]) -> None:
    blocks, _ = pilot
    batches = plan_batches(blocks, per_call=5)
    assert all(len(items) <= 5 for _, _, items in batches)
    assert len({b[0] for b in batches}) == len(batches)  # id lô duy nhất


def test_echo_changes_nothing(tmp_path: Path, pilot: tuple[list[Block], list[Line]]) -> None:
    blocks, _ = pilot
    fixed = asyncio.run(
        fixer_for(project(tmp_path), FakeLLM(echo)).fix(blocks, tmp_path / "p.jsonl")
    )
    assert [b.text for b in fixed] == [b.text_rules for b in blocks]
    assert all(b.fixes == [] for b in fixed)


# ---------------------------------------------------------------- #14 thiếu id


def test_14_missing_id_retried_then_flagged(
    tmp_path: Path, pilot: tuple[list[Block], list[Line]]
) -> None:
    blocks, _ = pilot
    victim = blocks[3].id

    def drop(items: list[dict[str, str]]) -> dict[str, str]:
        return {k: v for k, v in echo(items).items() if k != victim}

    fake = FakeLLM(drop)
    fixed = asyncio.run(fixer_for(project(tmp_path), fake).fix(blocks, tmp_path / "p.jsonl"))
    retries = [r for r in fake.requests if "Thiếu các id" in r["messages"][-1]["content"]]
    assert len(retries) == 1
    block = next(b for b in fixed if b.id == victim)
    assert "fix_failed" in block.flags
    assert block.text == block.text_rules


# ---------------------------------------------------------------- #15 chạy tiếp


def test_15_resume_skips_finished_batches(
    tmp_path: Path, pilot: tuple[list[Block], list[Line]]
) -> None:
    blocks, _ = pilot
    progress = tmp_path / "progress.jsonl"
    calls = {"n": 0}

    def crash_after_two(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] > 2:
            return httpx.Response(400, json={"error": {"message": "giả lập lỗi"}})
        return FakeLLM(echo)(request)

    settings = project(tmp_path, DM__LLM__CONCURRENCY="1")
    client = LLMClient(
        settings, transport=httpx.MockTransport(crash_after_two), sleep=SleepRecorder()
    )
    with pytest.raises(LLMError):
        asyncio.run(OCRFixer.from_settings(settings, client).fix(blocks, progress))
    assert len(progress.read_text(encoding="utf-8").splitlines()) == 2  # 2 lô đã xong được giữ

    # chạy lại ở chế độ refresh (bỏ qua cache LLM) → chỉ tiến độ giúp bỏ qua 2 lô đã xong
    fake = FakeLLM(echo)
    settings2 = project(tmp_path, DM__LLM__MODE="refresh")
    asyncio.run(fixer_for(settings2, fake).fix(blocks, progress))
    assert len(fake.requests) == 6 - 2


# ---------------------------------------------------------------- #16 tắt


def test_16_disabled_makes_no_calls(tmp_path: Path, pilot: tuple[list[Block], list[Line]]) -> None:
    blocks, _ = pilot
    fake = FakeLLM(echo)
    fixed = asyncio.run(
        fixer_for(project(tmp_path, DM__P1__FIX__ENABLED="false"), fake).fix(blocks, tmp_path / "p")
    )
    assert fake.requests == []
    assert [b.text for b in fixed] == [b.text_rules for b in blocks]


# ---------------------------------------------------------------- #17 prompt


def test_17_prompt_loader(tmp_path: Path) -> None:
    prompt = load_prompt(ROOT / "prompts", "p1_fix_ocr")
    assert prompt.ref == "p1_fix_ocr@v1"
    assert prompt.task == "fix_ocr"
    assert "TUYỆT ĐỐI KHÔNG" in prompt.text
    (tmp_path / "x.md").write_text("---\nid: x\n---\nnội dung", encoding="utf-8")
    with pytest.raises(PromptError, match="version"):
        load_prompt(tmp_path, "x")
    (tmp_path / "y.md").write_text("---\nid: khac\nversion: v1\n---\nnội dung", encoding="utf-8")
    with pytest.raises(PromptError, match="không trùng tên file"):
        load_prompt(tmp_path, "y")
    (tmp_path / "z.md").write_text("không có front matter", encoding="utf-8")
    with pytest.raises(PromptError, match="front matter"):
        load_prompt(tmp_path, "z")


def test_prompt_examples_not_from_book() -> None:
    """Ví dụ few-shot không được chứa câu trong sách (tránh rò rỉ đáp án vào đánh giá)."""
    from dataminer.devtools import sample_book_content as content

    text = load_prompt(ROOT / "prompts", "p1_fix_ocr").text
    sentences = [s for item in content.BOOK for s in item[1:] if isinstance(s, str) and len(s) > 25]
    assert not any(s[:25] in text for s in sentences)


# ---------------------------------------------------------------- đối chứng dương đầu-cuối


def test_oracle_llm_end_to_end_meets_all_gates(
    tmp_path: Path, book: SampleBook, pilot: tuple[list[Block], list[Line]]
) -> None:
    """LLM giả lập trả đúng văn bản sạch → qua HTTP, guard, đánh giá: G5-G9 đều đạt, và guard
    chặn ĐÚNG 2 thay đổi số liệu (gắn cờ + gợi ý), không chặn gì khác."""
    blocks, lines = pilot
    perfect = oracle_outputs(blocks, lines, book.truth)
    fake = FakeLLM(lambda items: {it["id"]: perfect[it["id"]] for it in items})
    fixed = asyncio.run(fixer_for(project(tmp_path), fake).fix(blocks, tmp_path / "p.jsonl"))
    report = eval_ocr(fixed, lines, book.truth)
    assert all(report[g]["pass"] for g in report), report
    rejected = [
        (f.before, f.after, f.rule, f.suggestion) for b in fixed for f in b.fixes if not f.accepted
    ]
    assert rejected == [("5OO", "500", "G-num", "500"), ("l", "1", "G-num", "1")]
    assert report["G6_errors_fixed"]["rate"] == 1.0


def test_eval_fails_loudly_when_lines_do_not_match(
    book: SampleBook, pilot: tuple[list[Block], list[Line]]
) -> None:
    """Đánh giá với dòng có ID khác (vd. đọc sai book_id) phải KHÔNG ĐẠT, không được bỏ qua
    im lặng rồi báo đạt (lỗi đã gặp khi làm P1.4)."""
    blocks, _ = pilot
    other_ids = read_lines(book.pdf_path, pages=PILOT, book_id="sach_khac")
    report = eval_ocr(blocks, other_ids, book.truth)
    assert not report["G6_errors_fixed"]["pass"]
    assert report["G6_errors_fixed"]["unmatched_errors"]
    assert not report["G5_wer"]["pass"]


def test_miscorrection_is_reported(
    tmp_path: Path, book: SampleBook, pilot: tuple[list[Block], list[Line]]
) -> None:
    """LLM đổi bản lỗi thành một từ SAI KHÁC (gặp thật: "kinh dien" → "kinh diễn", đúng là
    "kinh điển") - không tính là lỗi tạo thêm (G7) nhưng phải được báo riêng."""
    blocks, lines = pilot
    outputs = oracle_outputs(blocks, lines, book.truth)
    victim = next(k for k, v in outputs.items() if "Viêm khớp dạng thấp là bệnh lý" in v)
    outputs[victim] = outputs[victim].replace(" là bệnh lý", " lá bệnh lý", 1)  # "la" → "lá" (sai)
    fixer = OCRFixer.from_settings(project(tmp_path), client=None)  # type: ignore[arg-type]
    report = eval_ocr(fixer.apply(blocks, outputs), lines, book.truth)
    assert report["G6_errors_fixed"]["miscorrected"] == ["tr.4 drop_diacritics: là → la"]
    assert report["G7_introduced"]["tokens"] == 0
