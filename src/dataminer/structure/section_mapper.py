"""P2.4 - Ánh xạ loại mục: mỗi nút section/subsection → một loại chuẩn (definition, cause…).

Thứ tự tra cứu cho mỗi tên mục (đã bỏ số thứ tự, bỏ dấu, chữ thường):
    1. khớp chính xác từ điển configs/section_map.yaml           → nguồn `map`
    2. khớp gần (≥ fuzzy_min, chịu lỗi OCR nhầm 1 ký tự)          → `map_fuzzy` + đề xuất duyệt
    3. mục con không tra được → kế thừa loại của mục cha          → `inherited`
    4. LLM (tác vụ `classify`, nhãn đóng; mỗi tên lạ hỏi 1 lần)   → `llm` + đề xuất duyệt
    5. LLM tắt / không có → `other` + cờ                          → `none`
Đề xuất (2, 4) → CSV → người duyệt → GHI THÊM vào từ điển: lần sau tra được, không gọi LLM.
Xem docs/phases/P2/P2.4_plan.md.
"""

import asyncio
import csv
import difflib
import json
import re
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from dataminer.core.config import SectionsCfg
from dataminer.core.llm_client import LLMClient
from dataminer.core.prompts import Prompt
from dataminer.core.schemas import stable_id
from dataminer.core.text_vi import nfc, strip_diacritics
from dataminer.structure.tree_builder import RE_SECTION_PREFIX, Node

SectionType = Literal[
    "definition",
    "cause",
    "risk_factor",
    "pathophysiology",
    "symptom",
    "paraclinical",
    "diagnosis",
    "differential_diagnosis",
    "treatment",
    "complication",
    "prognosis",
    "prevention",
    "other",
]
SECTION_TYPES: tuple[str, ...] = SectionType.__args__  # type: ignore[attr-defined]
SECTION_FLAGS = ("section_type_fuzzy", "section_type_from_llm", "section_type_unknown")
CSV_COLUMNS = (
    "item_id",
    "source",
    "disease",
    "title",
    "normalized",
    "proposal",
    "reason",
    "decision",
    "edited_value",
)
RE_MAP_LINE = re.compile(r"^(?P<key>[^:#]+?)\s*:\s*(?P<value>[a-z_]+)\s*(?:#.*)?$")


class SectionMapError(Exception):
    """Từ điển hoặc CSV duyệt sai định dạng. Thông điệp đã kèm số dòng."""


class SectionProposal(BaseModel):
    """Một tên mục cần người duyệt (khớp gần hoặc LLM đề xuất)."""

    item_id: str
    source: Literal["map_fuzzy", "llm"]
    key: str  # tên mục đã chuẩn hóa - khóa sẽ thêm vào từ điển
    proposal: str
    reason: str
    titles: list[str]  # tên gốc (có thể nhiều bệnh cùng tên mục)
    diseases: list[str]
    node_ids: list[str]


class SectionResult(BaseModel):
    counts: dict[str, int]  # theo nguồn
    proposals: list[SectionProposal]
    warnings: list[str] = Field(default_factory=list)
    llm_calls: int = 0
    llm_cost_usd: float = 0.0
    prompt: str | None = None


class LLMSectionLabel(BaseModel):
    section_type: SectionType
    reason: str = Field(max_length=300)


# --------------------------------------------------------------------------- từ điển


def normalize_section_title(title: str) -> str:
    """ "3.1. Lâm sàng:" → "lam sang": bỏ số thứ tự, bỏ dấu, chữ thường, gộp khoảng trắng,
    bỏ dấu câu ở hai đầu."""
    text = RE_SECTION_PREFIX.sub("", nfc(title).strip())
    text = " ".join(strip_diacritics(text).casefold().split())
    return text.strip(" .:;,-")


def load_section_map(path: Path) -> dict[str, str]:
    """Đọc từ điển; lỗi (định dạng, khóa có dấu/chưa chuẩn hóa, loại ngoài tập, khóa trùng)
    được GOM LẠI kèm số dòng rồi báo một lần."""
    if not path.is_file():
        raise SectionMapError(f"Không có từ điển tên mục {path}")
    mapping: dict[str, str] = {}
    errors: list[str] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = RE_MAP_LINE.match(line)
        if m is None:
            errors.append(f"dòng {lineno}: không đúng dạng 'khóa: loại' - {raw!r}")
            continue
        key, value = m.group("key").strip(), m.group("value")
        if key != normalize_section_title(key):
            errors.append(
                f"dòng {lineno}: khóa '{key}' phải không dấu, chữ thường, không số thứ tự "
                f"(viết '{normalize_section_title(key)}')"
            )
        if value not in SECTION_TYPES:
            errors.append(
                f"dòng {lineno}: loại '{value}' không hợp lệ ({', '.join(SECTION_TYPES)})"
            )
        if key in mapping and mapping[key] != value:
            errors.append(f"dòng {lineno}: khóa '{key}' đã có loại '{mapping[key]}'")
        mapping[key] = value
    if errors:
        raise SectionMapError(f"{path.name} sai ({len(errors)} lỗi):\n  - " + "\n  - ".join(errors))
    return mapping


def lookup(key: str, mapping: dict[str, str], fuzzy_min: float) -> tuple[str, str, float] | None:
    """(loại, khóa khớp, độ giống) - trùng khóa trước, rồi khóa gần nhất ≥ fuzzy_min."""
    if key in mapping:
        return mapping[key], key, 1.0
    best = max(
        ((difflib.SequenceMatcher(None, key, k).ratio(), k) for k in mapping), default=(0.0, "")
    )
    if best[0] >= fuzzy_min:
        return mapping[best[1]], best[1], best[0]
    return None


# --------------------------------------------------------------------------- ánh xạ


async def _ask(
    client: LLMClient, prompt: Prompt, context: str
) -> tuple[LLMSectionLabel, float, bool]:
    messages = [
        {"role": "system", "content": prompt.text},
        {"role": "user", "content": context},
    ]
    label, resp = await client.chat_json("classify", messages, LLMSectionLabel)
    return label, resp.usage.cost_usd, resp.cached


def map_sections(
    nodes: Sequence[Node],
    mapping: dict[str, str],
    cfg: SectionsCfg | None = None,
    *,
    client: LLMClient | None = None,
    prompt: Prompt | None = None,
) -> SectionResult:
    """Điền `section_type`/`section_source`/cờ cho các nút mục (TẠI CHỖ, chạy lại được: kết quả
    cũ bị xóa trước). Nút phải theo thứ tự duyệt trước để mục cha có loại trước mục con."""
    cfg = cfg or SectionsCfg()
    by_id = {n.id: n for n in nodes}

    def disease_of(n: Node) -> str:
        cur: Node | None = n
        while cur is not None and cur.level != "disease":
            cur = by_id.get(cur.parent_id or "")
        return cur.display_title if cur else "-"

    fuzzy: dict[str, SectionProposal] = {}
    unknown: dict[str, list[Node]] = {}
    for n in nodes:
        if n.level not in ("section", "subsection"):
            continue
        n.section_type, n.section_source = None, None
        n.flags = [f for f in n.flags if f not in SECTION_FLAGS]
        key = normalize_section_title(n.title)
        hit = lookup(key, mapping, cfg.fuzzy_min)
        if hit is not None:
            n.section_type = hit[0]
            if hit[2] == 1.0:
                n.section_source = "map"
                continue
            n.section_source = "map_fuzzy"
            n.flags.append("section_type_fuzzy")
            p = fuzzy.setdefault(
                key,
                SectionProposal(
                    item_id=stable_id("section", key, prefix="sp"),
                    source="map_fuzzy",
                    key=key,
                    proposal=hit[0],
                    reason=f"khớp gần '{hit[1]}' ({hit[2]:.2f})",
                    titles=[],
                    diseases=[],
                    node_ids=[],
                ),
            )
            p.titles.append(n.title)
            p.diseases.append(disease_of(n))
            p.node_ids.append(n.id)
            continue
        parent = by_id.get(n.parent_id or "")
        if n.level == "subsection" and parent is not None and parent.section_type:
            n.section_type, n.section_source = parent.section_type, "inherited"
            continue
        unknown.setdefault(key, []).append(n)

    result = SectionResult(counts={}, proposals=list(fuzzy.values()))
    use_llm = cfg.llm_fallback and client is not None and prompt is not None
    if unknown and use_llm:
        assert client is not None and prompt is not None
        keys = list(unknown)
        contexts = []
        for key in keys:
            first = unknown[key][0]
            parent = by_id.get(first.parent_id or "")
            contexts.append(
                json.dumps(
                    {
                        "disease": disease_of(first),
                        "section_title": first.title,
                        "parent_section": parent.title
                        if parent and parent.level == "section"
                        else None,
                        "content_start": first.text[: cfg.context_chars],
                    },
                    ensure_ascii=False,
                )
            )

        async def run_all() -> list[tuple[LLMSectionLabel, float, bool]]:
            return await asyncio.gather(*(_ask(client, prompt, c) for c in contexts))

        for key, (label, cost, cached) in zip(keys, asyncio.run(run_all()), strict=True):
            group = unknown[key]
            for n in group:
                n.section_type, n.section_source = label.section_type, "llm"
                n.flags.append("section_type_from_llm")
            result.proposals.append(
                SectionProposal(
                    item_id=stable_id("section", key, prefix="sp"),
                    source="llm",
                    key=key,
                    proposal=label.section_type,
                    reason=label.reason,
                    titles=[n.title for n in group],
                    diseases=[disease_of(n) for n in group],
                    node_ids=[n.id for n in group],
                )
            )
            result.llm_calls += 0 if cached else 1
            result.llm_cost_usd += 0.0 if cached else cost
        result.prompt = prompt.ref
    elif unknown:
        for group in unknown.values():
            for n in group:
                n.section_type, n.section_source = "other", "none"
                n.flags.append("section_type_unknown")
        names = sorted({n.title for g in unknown.values() for n in g})
        result.warnings.append(
            f"{len(names)} tên mục không tra được và chưa hỏi LLM (tắt hoặc --no-llm) → 'other': "
            + ", ".join(f"'{t}'" for t in names)
        )
    sources = [n.section_source for n in nodes if n.level in ("section", "subsection")]
    result.counts = {s: sources.count(s) for s in ("map", "map_fuzzy", "inherited", "llm", "none")}
    return result


# --------------------------------------------------------------------------- vòng duyệt


def export_proposals(proposals: Sequence[SectionProposal], path: Path) -> None:
    """CSV (UTF-8 có BOM, mở được bằng Excel). Người duyệt điền `decision` = accept | edit |
    skip, và `edited_value` (một loại trong tập đóng) khi edit."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for p in proposals:
            writer.writerow(
                {
                    "item_id": p.item_id,
                    "source": p.source,
                    "disease": "; ".join(dict.fromkeys(p.diseases)),
                    "title": "; ".join(dict.fromkeys(p.titles)),
                    "normalized": p.key,
                    "proposal": p.proposal,
                    "reason": p.reason,
                    "decision": "",
                    "edited_value": "",
                }
            )


def import_proposals(
    csv_path: Path, proposals: Sequence[SectionProposal], map_path: Path, *, reviewer: str
) -> list[tuple[str, str]]:
    """Đọc CSV đã duyệt → GHI THÊM các khóa được chấp nhận vào từ điển. Mọi lỗi được gom kèm số
    dòng CSV; có lỗi thì KHÔNG ghi gì. Trả các (khóa, loại) đã thêm."""
    known = {p.item_id: p for p in proposals}
    current = load_section_map(map_path)
    accepted: list[tuple[str, str, str]] = []
    errors: list[str] = []
    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        for lineno, row in enumerate(csv.DictReader(fh), start=2):
            decision = (row.get("decision") or "").strip().lower()
            if decision in ("", "skip"):
                continue
            p = known.get((row.get("item_id") or "").strip())
            if p is None:
                errors.append(
                    f"dòng {lineno}: item_id '{row.get('item_id')}' không có trong đề xuất"
                )
                continue
            if decision == "accept":
                value = p.proposal
            elif decision == "edit":
                value = (row.get("edited_value") or "").strip()
                if value not in SECTION_TYPES:
                    errors.append(
                        f"dòng {lineno}: edited_value '{value}' không hợp lệ "
                        f"({', '.join(SECTION_TYPES)})"
                    )
                    continue
            else:
                errors.append(f"dòng {lineno}: decision '{decision}' (chỉ accept | edit | skip)")
                continue
            if current.get(p.key, value) != value:
                errors.append(
                    f"dòng {lineno}: '{p.key}' đã có trong từ điển với loại '{current[p.key]}'"
                )
                continue
            if p.key not in current:
                accepted.append((p.key, value, p.source))
    if errors:
        raise SectionMapError(
            f"{csv_path.name} sai ({len(errors)} lỗi):\n  - " + "\n  - ".join(errors)
        )
    if accepted:
        stamp = date.today().isoformat()
        text = map_path.read_text(encoding="utf-8").rstrip("\n") + "\n"
        text += "".join(
            f"{key}: {value}   # thêm {stamp}, duyệt bởi {reviewer} (nguồn: {source})\n"
            for key, value, source in accepted
        )
        map_path.write_text(text, encoding="utf-8")
        load_section_map(map_path)  # kiểm lại: file sau khi ghi vẫn hợp lệ
    return [(k, v) for k, v, _ in accepted]
