"""P2.2 - Phân cấp tiêu đề. Số (#) khớp mục 5 của docs/phases/P2/P2.2_plan.md.

Sách mẫu chỉ có tiêu đề "ngoan" (đánh số đều, bệnh nào cũng có trong mục lục) - phần "không dựa
trên sách mẫu" (block tự dựng) là BẮT BUỘC: LƯU Ý, bệnh ngoài mục lục, thiếu mục lục, nhảy số, LLM.
"""

import json
import shutil
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from dataminer.books.book01.headings import rule_level
from dataminer.books.book01.rules import build_blocks, classify_headings
from dataminer.books.book01.toc import extract_toc
from dataminer.cli import app
from dataminer.core.config import BlocksCfg, HeadingsCfg, Settings
from dataminer.core.io import write_jsonl
from dataminer.core.llm_client import LLMClient
from dataminer.core.llm_types import LLMJSONError
from dataminer.core.prompts import load_prompt
from dataminer.evaluation.p2_eval import all_pass, eval_heading_levels
from dataminer.model.block import Block
from dataminer.model.toc import TocEntry
from dataminer.model.tree import HeadingDecision
from dataminer.pdf.furniture import strip_furniture
from dataminer.pdf.reader import body_font_size, read_lines
from dataminer.structure.heading_levels import check_numbering
from dataminer.structure.toc_match import norm_title
from tests.conftest import SampleBookFor
from tests.unit.llm_fakes import ROOT, SleepRecorder, make_settings, ok

PILOT = (4, 9)
CFG = HeadingsCfg()
runner = CliRunner()


def p1_blocks(pdf: Path) -> list[Block]:
    """Block của P1 CHỈ bằng quy tắc (chưa sửa OCR → tiêu đề còn lỗi) cho chương mẫu."""
    lines = read_lines(pdf, pages=PILOT)
    body = body_font_size(lines)
    fr = strip_furniture(lines, body, pdf_pages=list(range(PILOT[0], PILOT[1] + 1)))
    return build_blocks(fr.content, body, BlocksCfg(), {p.page: p.printed_page for p in fr.pages})


_counter = iter(range(100_000))


def hb(text: str, size: float = 11.5, *, page: int = 4, numbering: str | None = None) -> Block:
    """Block tiêu đề tự dựng (numbering/IN HOA suy từ text như P1)."""
    from dataminer.books.book01.lines import numbering_of
    from dataminer.text.blocks import is_upper_text

    n = next(_counter)
    return Block(
        id=f"b{n}",
        kind="heading",
        text=text,
        text_rules=text,
        page_start=page,
        page_end=page,
        line_ids=[f"l{n}"],
        bbox=(48, 100, 300, 113),
        x0=48,
        font_size=size,
        is_upper=is_upper_text(text),
        numbering=numbering if numbering is not None else numbering_of(text),
    )


def para(text: str = "Nội dung thân bài khá dài để làm cỡ chữ chuẩn.", page: int = 4) -> Block:
    n = next(_counter)
    return Block(
        id=f"p{n}",
        kind="paragraph",
        text=text,
        text_rules=text,
        page_start=page,
        page_end=page,
        line_ids=[f"l{n}"],
        bbox=(48, 100, 300, 113),
        x0=48,
        font_size=10.5,
    )


def toc_entry(title: str, level: str = "disease", pdf_page: int | None = 4) -> TocEntry:
    return TocEntry(
        title=title,
        title_norm=norm_title(title),
        level=level,  # type: ignore[arg-type]
        printed_page=1,
        pdf_page=pdf_page,
        toc_pdf_page=3,
        line_id="x",
        x0=48 if level == "chapter" else 62,
    )


def levels(blocks: list[Block], toc: list[TocEntry], **kw: object) -> list[tuple[str, str]]:
    return [(d.text, d.level) for d in classify_headings(blocks, toc, **kw).decisions]  # type: ignore[arg-type]


# ---------------------------------------------------------------- #1-3 trên sách mẫu


@pytest.mark.parametrize("seed", [7, 1, 2])
def test_01_pilot_matches_truth(sample_book_for: SampleBookFor, seed: int) -> None:
    sample = sample_book_for(seed)
    toc = extract_toc(sample.pdf_path, book_id="book01")
    result = classify_headings(p1_blocks(sample.pdf_path), toc.entries)
    report = eval_heading_levels(result.decisions, sample.truth, PILOT)
    assert all_pass(report), report
    g2 = report["G2_heading_levels"]
    assert (g2["correct"], g2["truth"]) == (27, 27)
    assert g2["by_source"] == {"rules": 22, "toc": 5, "llm": 0}
    assert result.llm_calls == 0 and result.toc_missing == [] and result.warnings == []
    assert all(d.confidence == "high" for d in result.decisions)


def test_01b_toc_title_with_char_error_matches_fuzzy(sample_book_for: SampleBookFor) -> None:
    """Seed 2: mục lục ghi 'Viêrn loét…' (OCR) → vẫn ghép với tiêu đề bệnh, ghi 'khớp gần'."""
    sample = sample_book_for(2)
    toc = extract_toc(sample.pdf_path, book_id="book01")
    assert toc.entries[4].title.startswith("Viêrn")
    result = classify_headings(p1_blocks(sample.pdf_path), toc.entries)
    d = next(d for d in result.decisions if "DẠ DÀY" in d.text)
    assert (d.level, d.source, d.confidence) == ("disease", "toc", "high")
    assert "khớp gần" in d.reasons[-1]
    assert "missing_from_toc" not in d.flags


def test_02_ocr_damaged_headings_still_match_toc() -> None:
    blocks = [
        hb("CHUONG 1. BENH CO XUONG KHOP", 14),  # P1 không nhận 'CHUONG' → numbering None
        hb("VIEM KHOP DANG THAP", 13.4),
        hb("1. ĐẠI CƯƠNG", 12),
        para(),
    ]
    assert blocks[0].numbering is None
    toc = [toc_entry("Chương 1. Bệnh cơ xương khớp", "chapter"), toc_entry("Viêm khớp dạng thấp")]
    result = classify_headings(blocks, toc)
    assert [(d.level, d.source) for d in result.decisions] == [
        ("chapter", "toc"),
        ("disease", "toc"),
        ("section", "rules"),
    ]
    # không có mục lục: quy tắc vẫn nhận 'CHUONG 1.' (so không dấu)
    assert levels(blocks, [])[0] == ("CHUONG 1. BENH CO XUONG KHOP", "chapter")


def test_03_ocr_error_in_section_title_keeps_level() -> None:
    level, conf, _ = rule_level(hb("3. TRIỆU CHUNG", 11.7), 10.5, CFG)
    assert (level, conf) == ("section", "high")


# ---------------------------------------------------------------- #4-7 không dựa sách mẫu


def test_04_note_heading_is_other() -> None:
    blocks = [hb("VIÊM GAN B", 13.5), hb("1. ĐẠI CƯƠNG"), para(), hb("LƯU Ý", 10.6), para()]
    result = classify_headings(blocks, [toc_entry("Viêm gan B")])
    note = result.decisions[2]
    assert (note.level, note.confidence) == ("other", "low")
    assert "< ngưỡng bệnh" in note.reasons[0]
    assert any("chưa được LLM xem" in w for w in result.warnings)


def test_05_disease_missing_from_toc() -> None:
    blocks = [hb("VIÊM GAN B", 13.5), para(), hb("HEN PHẾ QUẢN", 13.0, page=6), para(page=6)]
    result = classify_headings(blocks, [toc_entry("Viêm gan B")])
    hen = result.decisions[1]
    assert (hen.level, hen.confidence, hen.flags) == ("disease", "low", ["missing_from_toc"])


def test_05b_toc_entry_not_found_in_scope() -> None:
    blocks = [hb("VIÊM GAN B", 13.5, page=4), para(), hb("1. ĐẠI CƯƠNG", page=5)]
    toc = [
        toc_entry("Viêm gan B", pdf_page=4),
        toc_entry("Gout", pdf_page=5),  # trong phạm vi trang đã xử lý → cảnh báo
        toc_entry("Sỏi thận", pdf_page=40),  # ngoài phạm vi (chưa xử lý) → không cảnh báo
    ]
    result = classify_headings(blocks, toc)
    assert result.toc_missing == ["Gout"]
    assert any("'Gout'" in w for w in result.warnings)


def test_05c_toc_page_mismatch_flagged() -> None:
    blocks = [hb("VIÊM GAN B", 13.5, page=6), para(page=6)]
    result = classify_headings(blocks, [toc_entry("Viêm gan B", pdf_page=4)])
    assert result.decisions[0].flags == ["toc_page_mismatch"]
    assert "mục lục ghi trang PDF 4" in result.warnings[0]


def test_05d_toc_overrides_rule_level() -> None:
    blocks = [
        hb("BỆNH HÔ HẤP", 14),  # IN HOA to, không số → quy tắc: disease; mục lục: chapter
        hb("HEN", 10.6),  # IN HOA cỡ thường → quy tắc: other; mục lục: disease
        para(),
    ]
    toc = [toc_entry("Bệnh hô hấp", "chapter"), toc_entry("Hen")]
    result = classify_headings(blocks, toc)
    assert [(d.level, d.source) for d in result.decisions] == [
        ("chapter", "toc"),
        ("disease", "toc"),
    ]
    assert "đổi disease thành chapter" in result.decisions[0].reasons[-1]


def test_06_no_toc_rules_only() -> None:
    blocks = [
        hb("CHƯƠNG 2. TIM MẠCH", 14),
        hb("TĂNG HUYẾT ÁP", 13.5),
        hb("1. ĐẠI CƯƠNG"),
        hb("1.1. Định nghĩa", 10.6),
        para(),
    ]
    result = classify_headings(blocks, [])
    assert [d.level for d in result.decisions] == ["chapter", "disease", "section", "subsection"]
    assert result.decisions[1].confidence == "medium"  # chưa có mục lục xác nhận
    assert "missing_from_toc" not in result.decisions[1].flags
    assert any("Không có mục lục" in w for w in result.warnings)


def test_06b_lowercase_numbered_rules() -> None:
    assert rule_level(hb("3. Triệu chứng", 11.5), 10.5, CFG)[:2] == ("section", "medium")
    assert rule_level(hb("3. Uống thuốc sau ăn", 10.5), 10.5, CFG)[:2] == ("other", "low")
    assert rule_level(hb("Ghi chú thêm", 13), 10.5, CFG)[:2] == ("other", "low")


def _decision(text: str, level: str, numbering: str | None) -> HeadingDecision:
    return HeadingDecision(
        block_id=text,
        text=text,
        page=4,
        level=level,  # type: ignore[arg-type]
        confidence="high",
        reasons=[],
        numbering=numbering,
    )


def test_07_numbering_gap() -> None:
    ds = [
        _decision("BỆNH A", "disease", None),
        _decision("1. A", "section", "1"),
        _decision("2. B", "section", "2"),
        _decision("2.1. x", "subsection", "2.1"),
        _decision("2.3. y", "subsection", "2.3"),  # nhảy 2.2
        _decision("4. D", "section", "4"),  # nhảy 3
        _decision("3.1. z", "subsection", "3.1"),  # mục con không thuộc mục 4
        _decision("BỆNH B", "disease", None),
        _decision("1. A", "section", "1"),  # bệnh mới: đếm lại từ 1 → không cờ
    ]
    warnings = check_numbering(ds)
    assert [d.text for d in ds if "numbering_gap" in d.flags] == ["2.3. y", "4. D", "3.1. z"]
    assert "mong đợi '3'" in warnings[1]


# ---------------------------------------------------------------- #8 LLM (giả lập)


class FakeClassifier:
    def __init__(self, answers: list[str]) -> None:
        self.answers = answers
        self.requests: list[dict] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        self.requests.append(payload)
        answer = self.answers[min(len(self.requests), len(self.answers)) - 1]
        return ok(answer)


def _llm(settings: Settings, fake: FakeClassifier) -> LLMClient:
    return LLMClient(settings, transport=httpx.MockTransport(fake), sleep=SleepRecorder())


def test_08_llm_fallback_for_low_only(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    prompt = load_prompt(ROOT / "prompts", "p2_classify_heading")
    fake = FakeClassifier(['{"level": "other", "reason": "ghi chú, không phải tên bệnh"}'])
    blocks = [
        hb("VIÊM GAN B", 13.5),
        hb("1. ĐẠI CƯƠNG"),
        para(),
        hb("LƯU Ý", 10.6),
        para("Không tự ý dùng thuốc."),
    ]
    result = classify_headings(
        blocks, [toc_entry("Viêm gan B")], client=_llm(settings, fake), prompt=prompt
    )
    assert len(fake.requests) == 1  # chỉ tiêu đề tin cậy thấp
    sent = json.loads(fake.requests[0]["messages"][1]["content"])
    assert sent["heading"] == "LƯU Ý" and sent["previous_heading"] == "1. ĐẠI CƯƠNG"
    assert sent["first_content_after"] == "Không tự ý dùng thuốc."
    assert fake.requests[0]["model"] == settings.model_for("classify").model
    note = result.decisions[2]
    assert (note.level, note.source, note.confidence) == ("other", "llm", "medium")
    assert note.flags == ["level_from_llm"] and "LLM xác nhận other" in note.reasons[-1]
    assert (result.llm_calls, result.prompt) == (1, "p2_classify_heading@v1")

    # chạy lại: cache → 0 lời gọi mới
    again = classify_headings(
        blocks, [toc_entry("Viêm gan B")], client=_llm(settings, fake), prompt=prompt
    )
    assert again.llm_calls == 0 and len(fake.requests) == 1


def test_08b_llm_label_outside_set_is_clear_error(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    prompt = load_prompt(ROOT / "prompts", "p2_classify_heading")
    fake = FakeClassifier(['{"level": "note", "reason": "?"}'])
    blocks = [hb("LƯU Ý", 10.6), para()]
    with pytest.raises(LLMJSONError, match="sai schema"):
        classify_headings(blocks, [], client=_llm(settings, fake), prompt=prompt)
    assert len(fake.requests) == settings.llm.json_retries + 1  # đã yêu cầu sửa trước khi bỏ


def test_08c_llm_disabled_by_config(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    fake = FakeClassifier(['{"level": "other", "reason": "x"}'])
    classify_headings(
        [hb("LƯU Ý", 10.6), para()],
        [],
        HeadingsCfg(llm_fallback=False),
        client=_llm(settings, fake),
        prompt=load_prompt(ROOT / "prompts", "p2_classify_heading"),
    )
    assert fake.requests == []


# ---------------------------------------------------------------- #9 đối chứng âm


@pytest.fixture(scope="module")
def pilot(sample_book_for: SampleBookFor) -> tuple[list[HeadingDecision], dict]:
    sample = sample_book_for(7)
    toc = extract_toc(sample.pdf_path, book_id="book01")
    return classify_headings(p1_blocks(sample.pdf_path), toc.entries).decisions, sample.truth


def test_09_eval_fails_on_wrong_truth(pilot: tuple[list[HeadingDecision], dict]) -> None:
    decisions, truth = pilot
    assert all_pass(eval_heading_levels(decisions, truth, PILOT))
    wrong = json.loads(json.dumps(truth))
    target = next(h for h in wrong["headings"] if h["text"] == "2.1. Yếu tố nguy cơ")
    target["level"] = "section"
    report = eval_heading_levels(decisions, wrong, PILOT)
    assert not all_pass(report)
    assert report["G2_heading_levels"]["correct"] == 26


def test_09b_eval_fails_on_missing_extra_misaligned(
    pilot: tuple[list[HeadingDecision], dict],
) -> None:
    decisions, truth = pilot
    dropped = decisions[:5] + decisions[6:]  # P1 sót 1 tiêu đề → lệch thứ tự
    assert "lệch thứ tự" in str(eval_heading_levels(dropped, truth, PILOT))
    assert not all_pass(eval_heading_levels(decisions[:-1], truth, PILOT))
    assert not all_pass(eval_heading_levels([*decisions, decisions[0]], truth, PILOT))
    assert not all_pass(eval_heading_levels([], truth, PILOT))
    # phạm vi trang không có tiêu đề nào → không được "đạt" im lặng
    assert not all_pass(eval_heading_levels([], truth, (1, 2)))


# ---------------------------------------------------------------- CLI


def test_cli_headings(tmp_path: Path, sample_book_for: SampleBookFor) -> None:
    sample = sample_book_for(7)
    make_settings(tmp_path)
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    shutil.copytree(ROOT / "prompts", tmp_path / "prompts")
    root = ["--root", str(tmp_path)]

    missing = runner.invoke(app, ["p2", "headings", *root])
    assert missing.exit_code == 1 and "dm p1 run" in missing.output

    raw = tmp_path / "data" / "books" / "book01" / "raw"
    raw.mkdir(parents=True)
    shutil.copy(sample.pdf_path, raw / "book01.pdf")
    shutil.copy(sample.truth_path, raw / "book01.truth.json")
    write_jsonl(
        tmp_path / "data" / "books" / "book01" / "p1_clean" / "blocks.jsonl",
        p1_blocks(sample.pdf_path),
    )

    good = runner.invoke(app, ["p2", "headings", *root, "--eval", "--no-llm"])
    assert good.exit_code == 0, good.output
    assert "chapter 2 · disease 3 · section 19 · subsection 3 · other 0" in good.output
    assert "✓ G2_heading_levels" in good.output
    out = tmp_path / "data" / "books" / "book01" / "p2_tree"
    assert (out / "toc.json").is_file()  # tự chạy P2.1 khi chưa có
    assert len((out / "heading_levels.jsonl").read_text(encoding="utf-8").splitlines()) == 27

    wrong = json.loads(json.dumps(sample.truth))
    wrong["headings"][1]["level"] = "disease"  # 'CHƯƠNG 1…' sai cấp trong đáp án
    bad_truth = tmp_path / "bad.truth.json"
    bad_truth.write_text(json.dumps(wrong, ensure_ascii=False), encoding="utf-8")
    bad = runner.invoke(app, ["p2", "headings", *root, "--eval", "--truth", str(bad_truth)])
    assert bad.exit_code == 1 and "✗ G2_heading_levels" in bad.output


def test_05e_each_toc_entry_used_once() -> None:
    """Tiêu đề bệnh lặp lại (vd. tiêu đề chạy bị P1 giữ lại) không được ghép 2 lần vào 1 mục lục."""
    blocks = [hb("VIÊM GAN B", 13.5), para(), hb("VIÊM GAN B", 13.5, page=5), para(page=5)]
    first, second = classify_headings(blocks, [toc_entry("Viêm gan B")]).decisions
    assert (first.source, first.flags) == ("toc", [])
    assert (second.source, second.flags) == ("rules", ["missing_from_toc"])
