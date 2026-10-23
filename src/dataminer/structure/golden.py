"""P2.5 - Bộ câu hỏi chuẩn v1 (EV.1): 30 câu có đáp án + nguồn trỏ tới nút của cây.

Thước đo dùng xuyên suốt: P3 (tìm kiếm trúng nút nguồn?), P5 (trả lời đủ ý, trích dẫn đúng?),
P7 (loại câu gần trùng khỏi dữ liệu huấn luyện). Đáp án và trích dẫn lấy từ văn bản SẠCH (đáp án
sách mẫu), không từ OCR - golden set không mang lỗi OCR còn sót.
Mỗi câu có `check` (luật máy kiểm lại được từ cây) để `validate_golden` tự kiểm, không tin mù.
Xem docs/phases/P2/P2.5_plan.md.
"""

import difflib
import re
from collections.abc import Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field

from dataminer.core.schemas import BaseRecord
from dataminer.core.text_vi import nfc, strip_diacritics
from dataminer.model.tree import Node

GOLDEN_VERSION = "v1"
CREATED_BY = "auto (sách mẫu)"
REVIEWED_BY = "auto-check (sách mẫu)"
QUOTA = {"specific": 20, "list": 5, "refusal": 5}
RE_NUMBER = re.compile(r"\d+(?:[.,]\d+)?")


class Source(BaseModel):
    node_id: str
    path: list[str]
    quote: str  # nguyên văn (sạch); phải có trong `text` của nút


class GoldenItem(BaseRecord):
    question: str
    qtype: Literal["specific", "list", "refusal"]
    answer: str
    answer_points: list[str]  # các ý bắt buộc (P5 chấm tự động)
    sources: list[Source]
    disease: str | None = None
    section_type: str | None = None
    check: dict[str, Any] = Field(default_factory=dict)  # luật máy kiểm lại (xem validate)
    created_by: str = CREATED_BY
    reviewed_by: str | None = None
    notes: str | None = None


class GoldenReport(BaseModel):
    items: int
    by_type: dict[str, int]
    errors: list[str]
    warnings: list[str]  # vd. trích dẫn chỉ khớp khi bỏ dấu (nút còn lỗi dấu OCR)

    @property
    def ok(self) -> bool:
        return not self.errors


# --------------------------------------------------------------------------- văn bản


def squash(text: str) -> str:
    """So khớp không phân biệt khoảng trắng: bỏ mọi khoảng trắng, NFC, chữ thường."""
    return "".join(nfc(text).casefold().split())


def loose(text: str) -> str:
    """Như `squash` nhưng bỏ cả dấu (chịu lỗi dấu OCR còn sót trong nút)."""
    return squash(strip_diacritics(text))


def quote_status(quote: str, node_text: str) -> Literal["exact", "loose", "missing"]:
    """exact: có trong nút (bỏ qua khoảng trắng); loose: chỉ có khi bỏ dấu (bỏ dấu không đổi chữ
    số, nên số liệu vẫn phải trùng đúng); missing: không có - vd. "5OO mg" chưa duyệt."""
    if squash(quote) in squash(node_text):
        return "exact"
    if loose(quote) in loose(node_text):
        return "loose"
    return "missing"


def missing_numbers(text: str, node_text: str) -> list[str]:
    """Số trong `text` không có trong nút - so CẢ token số ("5" của "5OO" ≠ "500")."""
    have = set(RE_NUMBER.findall(node_text))
    return [n for n in RE_NUMBER.findall(text) if n not in have]


RE_CAPTION_LINE = re.compile(r"^(Bảng|BẢNG|Hình|HÌNH)\s+\d")


def items_of(text: str) -> list[str]:
    """Các ý của một nút: gạch đầu dòng ("- …") → một ý; đoạn văn → mỗi câu một ý. Chú thích
    bảng/hình và hàng bảng (`ô | ô`) KHÔNG là ý (câu hỏi bảng có luật riêng)."""
    items: list[str] = []
    for ln in (ln.strip() for ln in text.splitlines()):
        if not ln or "|" in ln or RE_CAPTION_LINE.match(ln):
            continue
        if ln.startswith("- "):
            items.append(ln[2:].strip())
            continue
        items += [s.strip() for s in re.split(r"(?<=[.;])\s+(?=[A-ZÀ-Ỹ])", ln) if s.strip()]
    return items


# --------------------------------------------------------------------------- văn bản sạch


# --------------------------------------------------------------------------- sinh câu hỏi


def _diseases(nodes: Sequence[Node]) -> list[Node]:
    return [n for n in nodes if n.level == "disease"]


def _descendants(nodes: Sequence[Node], root: Node) -> list[Node]:
    out: list[Node] = []
    frontier = [root.id]
    while frontier:
        pid = frontier.pop(0)
        kids = [n for n in nodes if n.parent_id == pid]
        out += kids
        frontier += [k.id for k in kids]
    return out


def diseases_with_phrase(
    nodes: Sequence[Node], texts: dict[str, str], section_types: list[str], phrase: str
) -> list[tuple[Node, Node, str]]:
    """(bệnh, nút, ý chứa cụm từ) cho mọi bệnh có cụm từ trong các mục thuộc `section_types`."""
    out = []
    for d in _diseases(nodes):
        for n in _descendants(nodes, d):
            if n.section_type not in section_types:
                continue
            hit = next((it for it in items_of(texts[n.id]) if loose(phrase) in loose(it)), None)
            if hit:
                out.append((d, n, hit))
                break
    return out


# --------------------------------------------------------------------------- kiểm tra (G7)


def validate_golden(items: Sequence[GoldenItem], nodes: Sequence[Node]) -> GoldenReport:
    """G7: phân bổ đúng hạn ngạch; mọi nguồn trỏ tới nút tồn tại, path khớp, trích dẫn có thật
    trong nút (số liệu phải trùng đúng); luật `check` của từng câu kiểm lại được từ cây; câu
    từ chối không có từ khóa nào trong sách; không có câu trùng / gần trùng."""
    by_id = {n.id: n for n in nodes}
    texts = {n.id: n.text for n in nodes}
    book = loose("\n".join(n.text + " " + n.title for n in nodes))
    errors: list[str] = []
    warnings: list[str] = []
    by_type = {t: sum(i.qtype == t for i in items) for t in QUOTA}
    for t, want in QUOTA.items():
        if by_type[t] != want:
            errors.append(f"số câu '{t}' = {by_type[t]}, cần {want}")

    for i, item in enumerate(items, 1):
        tag = f"#{i} '{item.question[:60]}'"
        if not item.question.strip() or not item.answer.strip():
            errors.append(f"{tag}: thiếu câu hỏi hoặc đáp án")
        if item.qtype == "refusal":
            if item.sources or item.answer_points:
                errors.append(f"{tag}: câu từ chối không được có nguồn / ý")
            found = [k for k in item.check.get("keywords", []) if loose(k) in book]
            if not item.check.get("keywords"):
                errors.append(f"{tag}: câu từ chối thiếu từ khóa để tự kiểm")
            if found:
                errors.append(f"{tag}: từ khóa {found} CÓ trong sách - không phải câu từ chối")
            continue
        if not item.sources or not item.answer_points:
            errors.append(f"{tag}: thiếu nguồn hoặc ý bắt buộc")
        for s in item.sources:
            node = by_id.get(s.node_id)
            if node is None:
                errors.append(f"{tag}: nút nguồn {s.node_id} không tồn tại (cây đã đổi?)")
                continue
            if node.path != s.path:
                errors.append(f"{tag}: path {s.path} ≠ nút {node.path}")
            status = quote_status(s.quote, node.text)
            if status == "missing":
                errors.append(f"{tag}: trích dẫn không có trong nút {s.node_id}: '{s.quote[:60]}'")
            elif status == "loose":
                warnings.append(
                    f"{tag}: trích dẫn chỉ khớp khi bỏ dấu (nút còn lỗi dấu OCR): '{s.quote[:60]}'"
                )
        errors += [f"{tag}: {e}" for e in _check_rule(item, nodes, by_id, texts)]

    keys = [(loose(i.question), i.question) for i in items]
    for a in range(len(keys)):
        for b in range(a + 1, len(keys)):
            if difflib.SequenceMatcher(None, keys[a][0], keys[b][0]).ratio() >= 0.9:
                errors.append(f"câu gần trùng: '{keys[a][1]}' ~ '{keys[b][1]}'")
    return GoldenReport(items=len(items), by_type=by_type, errors=errors, warnings=warnings)


def _check_rule(
    item: GoldenItem, nodes: Sequence[Node], by_id: dict[str, Node], texts: dict[str, str]
) -> list[str]:
    """Kiểm lại đáp án từ cây theo `check` - đáp án không được lệch khỏi nội dung nút."""
    rule = item.check.get("rule")
    node = by_id.get(item.check.get("node_id", ""))
    if rule in ("items_of_node", "items_of"):
        if node is None:
            return [f"luật {rule}: nút {item.check.get('node_id')} không tồn tại"]
        got = [loose(p) for p in items_of(texts[node.id])]
        want = [loose(p) for p in item.answer_points]
        if got != want:
            return [f"ý bắt buộc khác nội dung nút ({len(want)} ý ↔ nút có {len(got)} ý)"]
        return []
    if rule == "numbers_in_node":
        if node is None:
            return [f"luật {rule}: nút {item.check.get('node_id')} không tồn tại"]
        text = texts[node.id]
        errors = []
        absent = missing_numbers(" ".join(item.answer_points), text)
        if absent:
            errors.append(f"số liệu {absent} không có trong nút (chưa duyệt?)")
        flat = text.replace("|", " ")  # hàng bảng "Omeprazol | 20 mg" ↔ ý "Omeprazol 20 mg"
        words = set(strip_diacritics(nfc(flat)).casefold().split())

        def present(point: str) -> bool:
            # nguyên văn; hoặc (ý ghép từ bảng: "2 lần/ngày" = ô "2" + cột "Số lần/ngày")
            # mọi từ/số của ý đều có trong nút
            if quote_status(point, flat) != "missing":
                return True
            return set(strip_diacritics(nfc(point)).casefold().split()) <= words

        missing = [p for p in item.answer_points if not present(p)]
        if missing:
            errors.append(f"ý {missing} không có trong nút")
        return errors
    if rule == "diseases_with_phrase":
        hits = diseases_with_phrase(nodes, texts, item.check["section_types"], item.check["phrase"])
        want = [d.display_title for d, _, _ in hits]
        if item.answer_points != want:
            return [f"tập bệnh {item.answer_points} ≠ tính lại từ cây {want}"]
        return []
    return [f"luật kiểm '{rule}' không hợp lệ"]
