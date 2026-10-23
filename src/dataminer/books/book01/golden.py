"""Sách mẫu (book01) - SINH bộ câu hỏi chuẩn v1 từ cây + đáp án sách mẫu (mẫu câu tiếng Việt).
Phần KIỂM TRA bộ câu hỏi là dùng chung (structure/golden.py). Sách thật không có đáp án →
câu hỏi phải do người viết (eval/README.md)."""

import re
from collections.abc import Sequence
from typing import Any

from dataminer.core.schemas import stable_id
from dataminer.evaluation.golden import (
    GOLDEN_VERSION,
    REVIEWED_BY,
    GoldenItem,
    Source,
    _descendants,
    _diseases,
    diseases_with_phrase,
    items_of,
    loose,
)
from dataminer.model.block import Block
from dataminer.model.tree import Node


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
    from dataminer.evaluation.truth.p1_eval import _line_key_map, _norm

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
