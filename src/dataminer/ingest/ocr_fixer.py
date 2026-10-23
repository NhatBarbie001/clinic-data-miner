"""P1.4 - Sửa lỗi OCR bằng LLM theo trang, rồi lọc từng thay đổi bằng guard tất định.

- Mọi block văn bản đều được gửi (72% lỗi OCR không phát hiện được bằng quy tắc - P0.5).
- Gửi theo TRANG để model có ngữ cảnh; bảng gửi từng Ô.
- Tiến độ ghi theo lô (`fix_progress.jsonl`) → chạy lại bỏ qua lô đã xong (N4); output LLM
  lưu trong tiến độ nên guard áp lại được tất định, không cần gọi lại API.
Xem docs/phases/P1/P1.4_plan.md.
"""

import asyncio
import json
import logging
from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from dataminer.core.config import FixCfg, Settings
from dataminer.core.io import append_jsonl, read_jsonl, repair_tail
from dataminer.core.llm_client import LLMClient
from dataminer.core.prompts import Prompt, load_prompt
from dataminer.core.schemas import BaseRecord, stable_id
from dataminer.core.text_vi import nfc
from dataminer.ingest.guards import GlossaryIndex, apply_guarded_fix
from dataminer.ingest.survey import text_ocr_signals
from dataminer.model.block import Block

log = logging.getLogger("dataminer.ingest")

FIXABLE = ("heading", "paragraph", "list_item", "caption", "toc_entry", "table")


class FixItem(BaseModel):
    id: str
    text: str


class FixBatch(BaseModel):
    """Schema JSON model phải trả về."""

    items: list[FixItem]


class BatchRecord(BaseRecord):
    """Một lô đã gọi LLM (lưu output thô để áp guard lại tất định)."""

    page: int
    prompt: str  # id@version
    item_ids: list[str]
    outputs: dict[str, str]  # id → văn bản LLM trả về
    missing: list[str] = Field(default_factory=list)  # id LLM không trả về
    model: str = ""
    cost_usd: float = 0.0
    cached: bool = False


def load_glossary(path: Path) -> GlossaryIndex:
    if not path.is_file():
        return GlossaryIndex([])
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return GlossaryIndex(data.get("terms", []))


def block_items(block: Block) -> list[tuple[str, str]]:
    """(id mục, văn bản) gửi LLM: block thường là 1 mục; bảng là mỗi ô một mục."""
    if block.kind == "table" and block.rows:
        return [
            (f"{block.id}#r{r}c{c}", cell)
            for r, row in enumerate(block.rows)
            for c, cell in enumerate(row)
            if cell.strip()
        ]
    return [(block.id, block.text_rules)]


def plan_batches(
    blocks: list[Block], per_call: int
) -> list[tuple[str, int, list[tuple[str, str]]]]:
    """Gom mục theo trang (trang đầu của block), cắt thành lô ≤ per_call mục."""
    by_page: dict[int, list[tuple[str, str]]] = {}
    for block in blocks:
        if block.kind in FIXABLE:
            by_page.setdefault(block.page_start, []).extend(block_items(block))
    batches = []
    for page, items in sorted(by_page.items()):
        for k in range(0, len(items), per_call):
            chunk = items[k : k + per_call]
            batch_id = stable_id(
                page, *(i for i, _ in chunk), *(t for _, t in chunk), prefix="fixb"
            )
            batches.append((batch_id, page, chunk))
    return batches


class OCRFixer:
    def __init__(
        self, client: LLMClient, prompt: Prompt, glossary: GlossaryIndex, cfg: FixCfg
    ) -> None:
        self.client = client
        self.prompt = prompt
        self.glossary = glossary
        self.cfg = cfg
        self.failed: set[str] = set()  # id mục LLM không trả về (sau khi đã nhắc lại)

    @classmethod
    def from_settings(cls, settings: Settings, client: LLMClient | None = None) -> "OCRFixer":
        cfg = settings.p1.fix
        root = settings.paths.data_dir.parent
        return cls(
            client or LLMClient(settings),
            load_prompt(settings.paths.prompts_dir, cfg.prompt),
            load_glossary(root / cfg.glossary),
            cfg,
        )

    def _messages(self, items: list[tuple[str, str]]) -> list[dict[str, Any]]:
        payload = {"items": [{"id": i, "text": t} for i, t in items]}
        return [
            {"role": "system", "content": self.prompt.text},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ]

    async def _call(self, batch_id: str, page: int, items: list[tuple[str, str]]) -> BatchRecord:
        messages = self._messages(items)
        wanted = [i for i, _ in items]
        parsed, resp = await self.client.chat_json("fix_ocr", messages, FixBatch)
        outputs = {it.id: it.text for it in parsed.items if it.id in wanted}
        missing = [i for i in wanted if i not in outputs]
        cost, cached = resp.usage.cost_usd, resp.cached
        if missing:  # nhắc model trả đủ id một lần
            retry = [
                *messages,
                resp.as_assistant_message(),
                {"role": "user", "content": f"Thiếu các id: {missing}. Trả lại JSON đủ mọi id."},
            ]
            parsed2, resp2 = await self.client.chat_json("fix_ocr", retry, FixBatch)
            outputs.update({it.id: it.text for it in parsed2.items if it.id in missing})
            missing = [i for i in wanted if i not in outputs]
            cost += resp2.usage.cost_usd
            cached = cached and resp2.cached
        return BatchRecord(
            id=batch_id,
            page=page,
            prompt=self.prompt.ref,
            item_ids=wanted,
            outputs=outputs,
            missing=missing,
            model=resp.model,
            cost_usd=cost,
            cached=cached,
        )

    async def run_batches(self, blocks: list[Block], progress: Path) -> dict[str, str]:
        """Gọi LLM cho các lô chưa xong; trả {id mục: văn bản LLM} của mọi lô."""
        done: dict[str, BatchRecord] = {}
        if progress.is_file():
            repair_tail(progress)
            done = {r.id: r for r in read_jsonl(progress, BatchRecord)}
        batches = plan_batches(blocks, self.cfg.blocks_per_call)
        todo = [b for b in batches if b[0] not in done]
        log.info("fix_ocr: %d lô (%d đã xong từ trước)", len(batches), len(batches) - len(todo))

        async def one(batch: tuple[str, int, list[tuple[str, str]]]) -> BatchRecord:
            record = await self._call(*batch)
            append_jsonl(progress, record)  # ghi ngay từng lô - ngắt giữa chừng vẫn giữ phần xong
            return record

        for record in await asyncio.gather(*(one(b) for b in todo)):
            done[record.id] = record
        outputs: dict[str, str] = {}
        self.failed = set()
        for batch_id, _, _ in batches:
            outputs.update(done[batch_id].outputs)
            self.failed.update(done[batch_id].missing)
        return outputs

    def apply(self, blocks: list[Block], outputs: dict[str, str]) -> list[Block]:
        """Áp guard lên output LLM → block mới (text, fixes, flags). Tất định."""
        fixed: list[Block] = []
        for block in blocks:
            new = block.model_copy(deep=True)
            if block.kind not in FIXABLE:
                fixed.append(new)
                continue
            flags = set(block.flags)
            new.fixes = []
            if block.kind == "table" and block.rows:
                rows = [list(r) for r in block.rows]
                for item_id, cell_text in block_items(block):
                    r, c = (int(x) for x in item_id.split("#r")[1].split("c"))
                    rows[r][c] = self._guard(
                        item_id, cell_text, outputs, flags, new, cell=f"r{r}c{c}"
                    )
                new.rows = rows
                new.text = "\n".join(" | ".join(row) for row in rows)
            else:
                new.text = self._guard(block.id, block.text_rules, outputs, flags, new)
            for kind, token, _ in text_ocr_signals(new.text):
                if kind != "digit_lookalike":  # số liệu nghi sai đã có cờ dose_suspect
                    flags.add("ocr_suspect")
                    log.debug("còn dấu hiệu %s: %s", kind, token)
            new.flags = sorted(flags)
            fixed.append(new)
        return fixed

    def _guard(
        self,
        item_id: str,
        original: str,
        outputs: dict[str, str],
        flags: set[str],
        block: Block,
        cell: str | None = None,
    ) -> str:
        if item_id in self.failed or item_id not in outputs:
            flags.add("fix_failed")
            return original
        result = apply_guarded_fix(
            original,
            outputs[item_id],
            self.glossary,
            min_similarity=self.cfg.min_similarity,
            max_changed_ratio=self.cfg.max_changed_ratio,
        )
        for fix in result.fixes:
            fix.cell = cell
            block.fixes.append(fix)
        flags.update(result.flags)
        return nfc(result.text)

    async def fix(self, blocks: list[Block], progress: Path) -> list[Block]:
        if not self.cfg.enabled:
            return [b.model_copy(deep=True) for b in blocks]
        outputs = await self.run_batches(blocks, progress)
        return self.apply(blocks, outputs)


def fix_stats(blocks: list[Block]) -> dict[str, Any]:
    fixes = [f for b in blocks for f in b.fixes]
    return {
        "blocks_changed": sum(b.text != b.text_rules for b in blocks),
        "fixes_accepted": sum(f.accepted for f in fixes),
        "fixes_rejected": dict(Counter(f.rule for f in fixes if not f.accepted)),
        "flags": dict(Counter(flag for b in blocks for flag in b.flags)),
    }
