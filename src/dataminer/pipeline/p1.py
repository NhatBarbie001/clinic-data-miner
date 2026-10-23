"""P1.6 - Chạy cả phase P1: đọc PDF → bỏ header/footer → dựng block → sửa OCR → áp duyệt.

Mọi file trung gian được ghi ra `data/p1_clean/` (N1) và một manifest cho lần chạy (N8):
    lines.jsonl          dòng PDF (P1.1)
    furniture.json       header/footer đã bỏ + số trang in (P1.2)
    content_lines.jsonl  dòng nội dung (P1.2)
    blocks_rules.jsonl   block sau quy tắc (P1.3)
    blocks_fixed.jsonl   block sau sửa OCR (P1.4) - tất định với cùng output LLM
    blocks.jsonl         block CUỐI sau áp quyết định duyệt (P1.5) - đầu vào P2
Chạy lại: tiến độ sửa OCR + cache LLM → $0 và kết quả giống hệt (G10).
Xem docs/phases/P1/P1.6_plan.md.
"""

import asyncio
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from dataminer.books.registry import rules_for
from dataminer.core.config import Settings
from dataminer.core.io import read_jsonl, write_jsonl
from dataminer.core.llm_client import LLMClient
from dataminer.core.run import RunRecorder
from dataminer.model.block import Block
from dataminer.ocrfix.fixer import OCRFixer, fix_stats
from dataminer.ocrfix.review import Decision, apply_decisions, build_queue
from dataminer.pdf.furniture import save_furniture, strip_furniture
from dataminer.pdf.reader import body_font_size, read_lines
from dataminer.text.blocks import blocks_summary, build_blocks

PHASE = "p1_clean"
Scope = Literal["pilot", "all"]


class P1Result(BaseModel):
    out_dir: str
    pages: tuple[int, int]
    run_id: str
    counts: dict[str, int]
    pending_review: int
    stale_decisions: list[str]
    llm_cost_usd: float


def p1_dir(settings: Settings) -> Path:
    return settings.paths.data_dir / PHASE


def resolve_pages(
    settings: Settings, scope: Scope, pages: tuple[int, int] | None, page_count: int
) -> tuple[int, int]:
    if pages:
        return pages
    pilot = settings.pilot
    if scope == "pilot" and pilot.page_start is not None and pilot.page_end is not None:
        return pilot.page_start, pilot.page_end
    content = settings.project.content_pages
    if content is not None:
        return content[0], min(content[1], page_count)
    return 1, page_count


def load_decisions(out: Path) -> list[Decision]:
    path = out / "review" / "decisions.jsonl"
    return list(read_jsonl(path, Decision)) if path.is_file() else []


def finalize(settings: Settings, fixed: list[Block]) -> tuple[list[Block], list[str]]:
    """Áp các quyết định duyệt đã lưu lên block đã sửa → ghi blocks.jsonl. Trả (block, stale)."""
    out = p1_dir(settings)
    final, report = apply_decisions(fixed, load_decisions(out))
    write_jsonl(out / "blocks.jsonl", final)
    return final, report.stale


def run_p1(
    settings: Settings,
    *,
    scope: Scope = "pilot",
    pages: tuple[int, int] | None = None,
    use_llm: bool = True,
    force: bool = False,
    client: LLMClient | None = None,
) -> P1Result:
    import pymupdf  # nạp chậm (~2s) - chỉ khi thực sự chạy

    out = p1_dir(settings)
    pdf = settings.paths.raw_dir / settings.project.book_file
    if not pdf.is_file():
        raise FileNotFoundError(
            f"Không thấy {pdf} - chép sách vào đó hoặc `dm dev make-sample-book`."
        )
    with pymupdf.open(pdf) as doc:
        page_count = doc.page_count
    start, end = resolve_pages(settings, scope, pages, page_count)
    p1 = settings.p1

    rules = rules_for(settings)

    with RunRecorder(settings, PHASE, out_dir=out) as run:
        run.add_input(pdf, records=False)
        run.note(f"phạm vi: trang PDF {start}-{end} ({scope if not pages else 'tùy chọn'})")

        lines = read_lines(
            pdf,
            book_id=settings.project.book_id,
            pages=(start, end),
            top_zone=p1.furniture.top_zone,
            bottom_zone=p1.furniture.bottom_zone,
            order=rules.order_lines,
        )
        write_jsonl(out / "lines.jsonl", lines)
        body = body_font_size(lines)

        furniture = strip_furniture(
            lines,
            body,
            p1.furniture,
            pdf_pages=list(range(start, end + 1)),
            page_number=rules.page_number,
        )
        save_furniture(furniture, out / "furniture.json")
        write_jsonl(out / "content_lines.jsonl", furniture.content)
        for warning in furniture.warnings:
            run.note(f"số trang: {warning}")

        printed = {p.page: p.printed_page for p in furniture.pages}
        blocks = build_blocks(
            furniture.content,
            body,
            p1.blocks,
            printed,
            settings.project.book_id,
            classify=rules.classify_line,
            numbering=rules.numbering,
        )
        write_jsonl(out / "blocks_rules.jsonl", blocks)

        progress = out / "fix_progress.jsonl"
        if force:
            progress.unlink(missing_ok=True)  # cache LLM vẫn dùng → không tốn tiền lại
        if use_llm and p1.fix.enabled:
            fixer = OCRFixer.from_settings(settings, client)
            run.use_prompt(fixer.prompt.id, fixer.prompt.version)
            fixed = asyncio.run(fixer.fix(blocks, progress))
        else:
            run.note("bỏ qua sửa OCR bằng LLM (--no-llm hoặc p1.fix.enabled=false)")
            fixed = [b.model_copy(deep=True) for b in blocks]
        write_jsonl(out / "blocks_fixed.jsonl", fixed)

        final, stale = finalize(settings, fixed)
        for item in stale:
            run.note(f"quyết định duyệt không còn khớp (stale): {item}")
        pending = build_queue(final)

        for name in (
            "lines.jsonl",
            "content_lines.jsonl",
            "blocks_rules.jsonl",
            "blocks_fixed.jsonl",
            "blocks.jsonl",
        ):
            run.add_output(out / name)
        run.add_output(out / "furniture.json", records=False)
        summary = blocks_summary(final)
        stats = fix_stats(fixed)
        counts = {
            "pages": end - start + 1,
            "lines": len(lines),
            "furniture_removed": len(furniture.removed),
            "content_lines": len(furniture.content),
            "blocks": summary["blocks"],
            **{f"blocks_{k}": v for k, v in summary["by_kind"].items()},
            "fixes_accepted": stats["fixes_accepted"],
            "fixes_rejected": sum(stats["fixes_rejected"].values()),
            "reviews_applied": sum(len(b.reviews) for b in final),
            "pending_review": len(pending),
        }
        for key, value in counts.items():
            run.count(key, value)

    return P1Result(
        out_dir=str(out),
        pages=(start, end),
        run_id=run.run_id,
        counts=counts,
        pending_review=len(pending),
        stale_decisions=stale,
        llm_cost_usd=run.manifest.llm.cost_usd,
    )
