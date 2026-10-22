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

from dataminer.core.schemas import BaseRecord, stable_id
from dataminer.core.text_vi import nfc, strip_diacritics
from dataminer.ingest.blocks import Block
from dataminer.structure.tree_builder import Node

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


def clean_texts(
    nodes: Sequence[Node],
    blocks: Sequence[Block],
    lines: Sequence[Any],
    truth: dict[str, Any] | None,
) -> dict[str, str]:
    """Văn bản SẠCH của từng nút: ghép văn bản đáp án của các dòng thuộc block của nút (cùng
    khóa ghép dòng như P1). Không có đáp án (sách thật) → dùng `node.text` (cần người duyệt)."""
    if truth is None:
        return {n.id: n.text for n in nodes}
    from dataminer.evaluation.p1_eval import _line_key_map, _norm

    key_of = _line_key_map(list(lines))
    clean: dict[tuple[int, str, int], str] = {}
    seen: dict[tuple[int, str], int] = {}
    for ln in truth["lines"]:
        k = (ln["pdf_page"], _norm(ln["ocr"]))
        occ = seen.get(k, 0)
        seen[k] = occ + 1
        clean[(k[0], k[1], occ)] = ln["text"]
    tables = {t["pdf_page"]: t["rows"] for t in truth.get("tables", [])}
    by_id = {b.id: b for b in blocks}
    out: dict[str, str] = {}
    for n in nodes:
        parts: list[str] = []
        for bid in n.block_ids:
            b = by_id[bid]
            if b.kind == "table" and b.page_start in tables:
                parts += [" | ".join(row) for row in tables[b.page_start]]
                continue
            missing = [lid for lid in b.line_ids if key_of.get(lid) not in clean]
            if missing:  # không ghép được với đáp án → không đoán
                raise ValueError(f"block {bid}: {len(missing)} dòng không có trong đáp án")
            text = " ".join(clean[key_of[lid]] for lid in b.line_ids)
            if b.kind == "list_item" and not text.startswith("- "):
                text = f"- {text}"
            parts.append(text)
        out[n.id] = "\n".join(parts)
    return out


# --------------------------------------------------------------------------- sinh câu hỏi

# (loại mục, các cách hỏi - xoay vòng theo bệnh để không lặp một khuôn)
SPECIFIC_TEMPLATES: list[tuple[str, list[str]]] = [
    (
        "definition",
        ["{d} là bệnh gì?", "Hãy cho biết đại cương về {d}.", "{d} được định nghĩa thế nào?"],
    ),
    (
        "cause",
        ["Nguyên nhân gây {d} là gì?", "{D} do đâu mà có?", "Những nguyên nhân nào gây ra {d}?"],
    ),
    (
        "symptom",
        [
            "Triệu chứng lâm sàng của {d} là gì?",
            "{D} có biểu hiện gì?",
            "Người bị {d} thường có triệu chứng gì?",
        ],
    ),
    (
        "diagnosis",
        [
            "Chẩn đoán {d} dựa vào đâu?",
            "Làm sao để chẩn đoán {d}?",
            "Tiêu chuẩn chẩn đoán {d} là gì?",
        ],
    ),
    (
        "treatment",
        [
            "Điều trị {d} như thế nào?",
            "Các biện pháp điều trị {d} gồm những gì?",
            "{D} được điều trị ra sao?",
        ],
    ),
    (
        "prevention",
        [
            "Phòng bệnh {d} như thế nào?",
            "Làm gì để phòng {d}?",
            "Các biện pháp dự phòng {d} là gì?",
        ],
    ),
]

# Câu số liệu / bảng: (bệnh chứa, loại mục, từ khóa của ý, câu hỏi)
FACT_TEMPLATES: list[tuple[str, str, str, str]] = [
    (
        "thoai hoa khop goi",
        "treatment",
        "Paracetamol",
        "Liều paracetamol trong điều trị thoái hóa khớp gối là bao nhiêu?",
    ),
    (
        "viem loet da day",
        "treatment",
        "Omeprazol |",
        "Phác đồ diệt Helicobacter pylori 3 thuốc gồm những thuốc nào, liều bao nhiêu?",
    ),
]

# Câu liệt kê: (câu hỏi, luật kiểm)
LIST_TEMPLATES: list[tuple[str, dict[str, Any]]] = [
    (
        "Những bệnh nào trong sách được điều trị bằng thuốc chống viêm không steroid?",
        {
            "rule": "diseases_with_phrase",
            "section_types": ["treatment"],
            "phrase": "chống viêm không steroid",
        },
    ),
    (
        "Những bệnh nào trong sách có nguyên nhân hoặc yếu tố nguy cơ là hút thuốc lá?",
        {
            "rule": "diseases_with_phrase",
            "section_types": ["cause", "risk_factor"],
            "phrase": "thuốc lá",
        },
    ),
    (
        "Liệt kê các biến chứng của viêm loét dạ dày tá tràng.",
        {"rule": "items_of", "disease": "viem loet da day", "section_type": "complication"},
    ),
    (
        "Liệt kê các yếu tố nguy cơ của viêm khớp dạng thấp.",
        {"rule": "items_of", "disease": "viem khop dang thap", "section_type": "risk_factor"},
    ),
    (
        "Viêm khớp dạng thấp cần làm những xét nghiệm cận lâm sàng nào?",
        {"rule": "items_of", "disease": "viem khop dang thap", "section_type": "paraclinical"},
    ),
]

REFUSAL_TEMPLATES: list[tuple[str, list[str]]] = [
    ("Điều trị hen phế quản như thế nào?", ["hen phế quản"]),
    ("Liều insulin cho bệnh nhân đái tháo đường là bao nhiêu?", ["insulin", "đái tháo đường"]),
    ("Triệu chứng của viêm gan B là gì?", ["viêm gan"]),
    ("Nguyên nhân gây sỏi thận là gì?", ["sỏi thận"]),
    ("Làm thế nào để phòng bệnh tăng huyết áp?", ["huyết áp"]),
]
NOT_IN_BOOK = "Sách không đề cập nội dung này."


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


def _find_disease(nodes: Sequence[Node], key: str) -> Node:
    hits = [d for d in _diseases(nodes) if loose(key) in loose(d.display_title)]
    if len(hits) != 1:
        raise ValueError(f"cần đúng 1 bệnh khớp '{key}', có {len(hits)}")
    return hits[0]


def _section_nodes(nodes: Sequence[Node], disease: Node, section_type: str) -> list[Node]:
    """Nút có nội dung riêng thuộc loại mục này trong bệnh (mục chỉ có mục con thì lấy mục con)."""
    return [
        n for n in _descendants(nodes, disease) if n.section_type == section_type and n.block_ids
    ]


def _capital(text: str) -> str:
    return text[:1].upper() + text[1:]


def _source(node: Node, quote: str) -> Source:
    return Source(node_id=node.id, path=node.path, quote=quote)


def _item(question: str, **kw: Any) -> GoldenItem:
    return GoldenItem(
        id=stable_id("golden", GOLDEN_VERSION, question, prefix="gq"),
        question=question,
        reviewed_by=REVIEWED_BY,
        **kw,
    )


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


def draft_golden(nodes: Sequence[Node], texts: dict[str, str]) -> list[GoldenItem]:
    """Sinh bộ câu hỏi (xác định: cùng cây + văn bản → cùng file). `texts` = văn bản sạch."""
    items: list[GoldenItem] = []
    diseases = _diseases(nodes)
    for di, d in enumerate(diseases):
        name = d.display_title.lower()
        for section_type, variants in SPECIFIC_TEMPLATES:
            targets = _section_nodes(nodes, d, section_type)
            if not targets:
                continue
            node = targets[0]  # vd. "Triệu chứng" của VKDT chỉ có mục con → lấy "Lâm sàng"
            points = items_of(texts[node.id])
            question = _capital(variants[di % len(variants)].format(d=name, D=d.display_title))
            items.append(
                _item(
                    question,
                    qtype="specific",
                    answer=" ".join(p if p.endswith((".", ";")) else p + "." for p in points),
                    answer_points=points,
                    sources=[_source(node, points[0])],
                    disease=d.display_title,
                    section_type=section_type,
                    check={"rule": "items_of_node", "node_id": node.id},
                )
            )
    for disease_key, section_type, keyword, question in FACT_TEMPLATES:
        d = _find_disease(nodes, disease_key)
        node = next(n for n in _section_nodes(nodes, d, section_type) if keyword in texts[n.id])
        if "|" in keyword:  # câu hỏi bảng: mỗi hàng thuốc là một ý
            rows = [r for r in texts[node.id].splitlines() if r.count("|") >= 3]
            drugs = [r.split(" | ") for r in rows[1:]]
            points = [f"{c[0]} {c[1]}" for c in drugs] + [
                f"{drugs[0][2]} lần/ngày",
                drugs[0][3],
            ]
            answer = (
                ", ".join(f"{c[0]} {c[1]}" for c in drugs)
                + f"; mỗi thuốc {drugs[0][2]} lần/ngày trong {drugs[0][3]}."
            )
            quote = rows[1]
            notes = "Câu cần đọc BẢNG (Bảng 2.1); kiểm số liệu đã duyệt ở P1.5 (OCR gốc 'l g')."
        else:
            item = next(it for it in items_of(texts[node.id]) if keyword in it)
            rest = item.split(keyword, 1)[1].strip().rstrip(".")
            points = [p.strip() for p in re.split(r"[,;]\s*", rest) if p.strip()]
            answer, quote = item, item
            notes = "Câu SỐ LIỆU: giá trị đã duyệt ở P1.5 (OCR gốc '5OO mg')."
        items.append(
            _item(
                question,
                qtype="specific",
                answer=answer,
                answer_points=points,
                sources=[_source(node, quote)],
                disease=d.display_title,
                section_type=section_type,
                check={"rule": "numbers_in_node", "node_id": node.id},
                notes=notes,
            )
        )
    for question, rule in LIST_TEMPLATES:
        if rule["rule"] == "diseases_with_phrase":
            hits = diseases_with_phrase(nodes, texts, rule["section_types"], rule["phrase"])
            items.append(
                _item(
                    question,
                    qtype="list",
                    answer="; ".join(d.display_title for d, _, _ in hits) + ".",
                    answer_points=[d.display_title for d, _, _ in hits],
                    sources=[_source(n, it) for _, n, it in hits],
                    check=rule,
                    notes=_list_note(nodes, texts, rule, [d for d, _, _ in hits]),
                )
            )
        else:
            d = _find_disease(nodes, rule["disease"])
            node = _section_nodes(nodes, d, rule["section_type"])[0]
            points = items_of(texts[node.id])
            items.append(
                _item(
                    question,
                    qtype="list",
                    answer="; ".join(points),
                    answer_points=points,
                    sources=[_source(node, points[0])],
                    disease=d.display_title,
                    section_type=rule["section_type"],
                    check={**rule, "node_id": node.id},
                )
            )
    for question, keywords in REFUSAL_TEMPLATES:
        items.append(
            _item(
                question,
                qtype="refusal",
                answer=NOT_IN_BOOK,
                answer_points=[],
                sources=[],
                check={"rule": "absent", "keywords": keywords},
                notes="auto-check: không từ khóa nào xuất hiện trong nội dung sách.",
            )
        )
    return items


def _list_note(
    nodes: Sequence[Node], texts: dict[str, str], rule: dict[str, Any], hits: list[Node]
) -> str | None:
    """Ghi chú bẫy ngữ nghĩa: bệnh có cụm từ nhưng ở loại mục KHÁC (không thuộc đáp án)."""
    others = [
        f"{d.display_title} ({n.section_type})"
        for d in _diseases(nodes)
        if d not in hits
        for n in _descendants(nodes, d)
        if loose(rule["phrase"]) in loose(texts.get(n.id, ""))
    ]
    if not others:
        return None
    return (
        f"KHÔNG thuộc đáp án: cụm '{rule['phrase']}' cũng có ở {', '.join(others)} "
        "- không phải loại mục được hỏi. Kiểm việc lọc theo loại mục (P2.4)."
    )


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
