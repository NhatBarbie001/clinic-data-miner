"""Sách IASP - cấp tiêu đề (L5-L10), tên hiển thị, thuộc tính sau khi dựng cây (L8, L9, L11).

Cấp nhận ra bằng cỡ chữ + số hiệu (P1 đã tính `numbering`):
    cỡ lớn  "E. LOCAL SYNDROMES …"          → part     (nhóm chữ cái, L5)
            "GROUP XI: PAIN IN THE …"        → chapter  (nhóm La Mã, L6)
            "Tumors of the … (XI-1)"         → disease  (hội chứng, L7; không mã → L9)
    cỡ thường "Definition", "Site" …         → section  (L10); "1. History of …" → subsection
Xem docs/phases/P2R/I3_plan.md mục 3.
"""

import re

from dataminer.books.iasp.codes import iasp_codes, strip_code, syndrome_code, syndrome_codes
from dataminer.books.iasp.lines import BIG_DELTA, RE_GROUP, RE_LETTER
from dataminer.core.config import HeadingsCfg
from dataminer.core.text_vi import nfc
from dataminer.model.block import Block
from dataminer.model.tree import Confidence, Level, Node
from dataminer.structure.section_mapper import normalize_section_title
from dataminer.structure.tree_builder import sentence_case

TITLE_SIZE = 15.0  # "PART II", "DETAILED DESCRIPTIONS OF PAIN SYNDROMES" (cỡ 15.5): tên phần sách
# dòng IN HOA bắt đầu bằng từ nối = dòng sau của tiêu đề căn giữa dãn dòng rộng (PDF 54:
# "ITEMS USUALLY PROVIDED IN DESCRIPTIONS" ↵ "OF PAIN SYNDROMES") - P1 không nối được
RE_CONNECTOR = re.compile(r"^(OF|AND|FROM|IN|THE|WITH|FOR|TO)\b")
RE_SUBSECTION = re.compile(r"^\d{1,2}\.\s")  # "1. History of Widespread Pain"
RE_CODE_TITLE = re.compile(r"^Codes?\b|^Code\(s\)")  # mục "Code", "Codes", "Code X32.X3a"
RE_END_TITLE = re.compile(r"^References?$")


def _norm(text: str) -> str:
    return " ".join(nfc(text).split())


def rule_level(
    block: Block, body_size: float, cfg: HeadingsCfg
) -> tuple[Level, Confidence, list[str]]:
    text = _norm(block.text)
    size = f"cỡ {block.font_size:g} (thân bài {body_size:g})"
    if block.font_size < body_size + BIG_DELTA:
        if RE_SUBSECTION.match(text):
            return "subsection", "high", [f"đậm cỡ thường, đánh số '{text[:3].strip()}' - {size}"]
        return "section", "high", [f"tên mục: đậm cỡ thường (L10) - {size}"]
    if RE_GROUP.match(text):
        return "chapter", "high", [f"nhóm La Mã 'GROUP {block.numbering}' (L6) - {size}"]
    if RE_LETTER.match(text):
        return "part", "high", [f"nhóm chữ cái '{block.numbering}.' (L5) - {size}"]
    if block.is_upper:
        if block.font_size >= TITLE_SIZE:
            return "other", "high", [f"tên phần sách IN HOA cỡ ≥ {TITLE_SIZE:g} - {size}"]
        if RE_CONNECTOR.match(text):
            return "other", "medium", ["dòng IN HOA bắt đầu bằng từ nối = phần sau tiêu đề trên"]
        return "chapter", "medium", [f"IN HOA cỡ lớn nhưng không có 'GROUP' - {size}"]
    if block.numbering:
        return "disease", "high", [f"hội chứng mã {block.numbering} (L7) - {size}"]
    return "disease", "medium", [f"chữ đậm cỡ lớn, chữ thường, KHÔNG có mã (L9) - {size}"]


def display_title(text: str, level: str) -> str:
    """part "E. Local syndromes of …"; chapter "GROUP XI: Pain in the shoulder, arm, and hand";
    disease bỏ mã ở cuối "Tumors of the Brachial Plexus"; mục giữ nguyên."""
    text = _norm(text)
    if level == "part" and (m := RE_LETTER.match(text)):
        return f"{m.group(1)}. {sentence_case(text[m.end() :])}"
    if level == "chapter":
        text = strip_code(text)  # "GROUP XVI: … LOWER LIMBS (XVI-1)": nhóm chỉ có 1 hội chứng
        if m := RE_GROUP.match(text):
            return f"GROUP {m.group(1)}: {sentence_case(text[m.end() :].strip())}"
        return sentence_case(text)
    if level == "disease":
        return strip_code(text)
    return text


def is_syndrome(node: Node) -> bool:
    """Nút mô tả MỘT hội chứng: cấp disease, hoặc GROUP chỉ có một hội chứng và mang luôn mã
    của nó ("GROUP XVI: PAIN OF PSYCHOLOGICAL ORIGIN IN THE LOWER LIMBS (XVI-1)")."""
    return node.level == "disease" or (
        node.level == "chapter" and syndrome_code(node.title) is not None
    )


def code_of(node: Node) -> str | None:
    """Mã hội chứng đã chuẩn hóa của nút (disease: `numbering`; GROUP-hội chứng: từ tiêu đề)."""
    return node.numbering if node.level == "disease" else syndrome_code(node.title)


def section_key(title: str) -> str:
    """Khóa tra từ điển loại mục: như mặc định, nhưng mục Code có mã dính sau tên
    ("Code X32.X3a", "Code(s)", "Codes") → "code"."""
    if RE_CODE_TITLE.match(_norm(title)):
        return "code"
    return normalize_section_title(title)


def annotate_tree(nodes: list[Node]) -> list[str]:
    """Sau khi dựng cây: mã IASP 5 trục (`attrs.iasp_codes`, L11) + cờ `no_code` (L9),
    `code_group_mismatch`, `no_iasp_code`, `unnumbered_chapter`, `chapter_is_syndrome`.
    Trả cảnh báo."""
    by_id = {n.id: n for n in nodes}
    kids: dict[str, list[Node]] = {}
    for n in nodes:
        if n.parent_id:
            kids.setdefault(n.parent_id, []).append(n)

    def own_sections(node: Node) -> list[Node]:
        """Mục + mục con của nút, KHÔNG đi vào hội chứng con."""
        out: list[Node] = []
        for child in kids.get(node.id, []):
            if child.level in ("section", "subsection"):
                out += [child, *own_sections(child)]
        return out

    def chapter_of(node: Node) -> Node | None:
        cur = by_id.get(node.parent_id or "")
        while cur is not None and cur.level != "chapter":
            cur = by_id.get(cur.parent_id or "")
        return cur

    warnings: list[str] = []
    no_code: list[str] = []
    for n in nodes:
        if n.level == "chapter" and n.numbering is None:
            n.flags.append("unnumbered_chapter")
        if not is_syndrome(n):
            continue
        code = code_of(n)
        chapter = n if n.level == "chapter" else chapter_of(n)
        if n.level == "chapter":
            n.flags.append("chapter_is_syndrome")
        if n.level == "chapter" or len(syndrome_codes(n.title)) > 1:
            n.attrs["codes"] = syndrome_codes(n.title)  # GROUP-hội chứng; mục gộp 2 hội chứng
        # sách thiếu dòng tên hội chứng → 2 hội chứng dính nhau: "Definition" lại xuất hiện SAU
        # mục Code / References (mục cuối của một hội chứng). PDF 185 thiếu tên XXIV-7.
        ended = False
        for s in kids.get(n.id, []):
            if RE_CODE_TITLE.match(s.title) or RE_END_TITLE.match(s.title):
                ended = True
            elif s.title == "Definition" and ended:
                n.flags.append("missing_syndrome_title")
                warnings.append(
                    f"'{n.display_title}': mục Definition ở PDF {s.page_start} nằm sau mục "
                    "Code/References - nghi sách thiếu tên một hội chứng (nội dung bị gộp vào đây)."
                )
                break
        if code is None:
            n.flags.append("no_code")
            no_code.append(f"'{n.display_title}' (PDF {n.page_start})")
        elif (
            chapter is not None and chapter.numbering and (code.split("-")[0] != chapter.numbering)
        ):
            n.flags.append("code_group_mismatch")
            warnings.append(
                f"'{n.display_title}' mã {code} nằm trong GROUP {chapter.numbering} "
                f"(PDF {n.page_start})."
            )
        sections = [s for s in own_sections(n) if RE_CODE_TITLE.match(s.title)]
        texts = [f"{s.title}\n{s.text}" for s in sections] or [
            line for line in n.text.splitlines() if line.startswith("Code")
        ]
        codes = [c for t in texts for c in iasp_codes(t)]
        if codes:
            n.attrs["iasp_codes"] = list(dict.fromkeys(codes))
        else:
            n.flags.append("no_iasp_code")
    if no_code:
        warnings.append(f"{len(no_code)} hội chứng không có mã (L9): " + "; ".join(no_code))
    missing = sum("no_iasp_code" in n.flags for n in nodes)
    if missing:
        warnings.append(f"{missing} hội chứng không tìm thấy mã IASP 5 trục (mục Code).")
    return warnings
