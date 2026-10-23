"""P1.4 - Guard tất định (không dùng LLM) cho bản sửa lỗi OCR, xét theo TỪNG TOKEN.

Căn chỉnh token (tách theo khoảng trắng) giữa bản gốc và bản LLM, rồi mỗi thay đổi đi qua
các luật theo thứ tự. Thay đổi hợp lệ được áp dụng; thay đổi vi phạm bị từ chối (giữ gốc) và
ghi lại. Số liệu nghi nhận nhầm (5OO, "l g") KHÔNG BAO GIỜ tự sửa - chỉ gắn cờ + gợi ý.

    G-num      token có chữ số (gốc hoặc mới), hoặc gốc trông như số nhầm chữ (5OO, l trước đơn vị)
               → từ chối; trường hợp nhầm chữ → cờ `dose_suspect` + gợi ý.
               Ngoại lệ hẹp: chữ số 1/0 dính trong chữ ("1à") → "l"/"o" cho ra âm tiết hợp lệ.
    G-protect  token gốc là thuật ngữ bảo vệ (glossary, chữ HOA giữa từ, gạch nối Latin) → từ chối
    G-punct    dấu câu của token đổi → từ chối
    G-sim      giống nhau (đã bỏ dấu, chữ thường) < min_similarity → từ chối (LLM thay từ khác)
    G-insdel   LLM thêm/bớt token (không phải tách/dính từ) → từ chối
    G-ratio    số token bị đổi > max_changed_ratio → từ chối CẢ block, cờ `fix_rejected`

Xem docs/phases/P1/P1.4_plan.md mục 3.3.
"""

import difflib
import re
from collections.abc import Iterable, Sequence

from pydantic import BaseModel, Field

from dataminer.core.text_vi import has_vietnamese_marks, is_valid_syllable, nfc, strip_diacritics
from dataminer.model.block import Fix, Rule

RE_DIGIT_LOOKALIKE = re.compile(r"\d[OoIl]|[OoIl]\d")  # 5OO, 1O, l0
UNITS = {"g", "mg", "mcg", "µg", "ml", "l", "ui", "iu", "kg"}
PUNCT = "\"'“”‘’()[]{}.,;:!?…-–—/"


class GuardResult(BaseModel):
    text: str
    fixes: list[Fix] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)


def _core(token: str) -> str:
    return token.strip(PUNCT)


def _punct(token: str) -> tuple[str, str]:
    core = _core(token)
    if not core:
        return token, ""
    start = token.find(core)
    return token[:start], token[start + len(core) :]


def _has_digit(token: str) -> bool:
    return any(c.isdigit() for c in token)


def looks_like_misread_number(token: str, next_token: str | None) -> bool:
    """5OO, 1O0, "l" / "O" đứng trước đơn vị ("l g")."""
    core = _core(token)
    if _has_digit(core) and RE_DIGIT_LOOKALIKE.search(core):
        return True
    return core in ("l", "I", "O") and next_token is not None and _core(next_token).lower() in UNITS


def _digit_letter_fix(before: str, after: str) -> bool:
    """Ngoại lệ hẹp cho G-num: "1à" → "là". Chỉ 1 chữ số 1/0 dính trong chữ, thay bằng l/o,
    kết quả không còn chữ số và là âm tiết tiếng Việt hợp lệ."""
    core_b, core_a = _core(before), _core(after)
    digits = [c for c in core_b if c.isdigit()]
    if len(digits) != 1 or digits[0] not in "10" or _has_digit(core_a) or len(core_b) < 2:
        return False
    letter = {"1": "l", "0": "o"}[digits[0]]
    if core_b.replace(digits[0], letter, 1) != core_a:
        return False
    return has_vietnamese_marks(core_a) and is_valid_syllable(core_a)


class GlossaryIndex:
    """Thuật ngữ bảo vệ (so khớp chữ thường, bỏ dấu câu bao quanh)."""

    def __init__(self, terms: Iterable[str]) -> None:
        self.terms = {nfc(t).casefold() for t in terms}

    def __contains__(self, token: str) -> bool:
        return nfc(_core(token)).casefold() in self.terms


def is_protected(token: str, glossary: GlossaryIndex) -> bool:
    core = _core(token)
    if not core:
        return False
    if core in glossary:
        return True
    if core.isascii() and any(c.isupper() for c in core[1:]) and not core.isupper():
        return True  # thuật ngữ Latin: anti-CCP, DMARDs, pH (từ có dấu Việt không thuộc loại này)
    return bool(re.search(r"[A-Za-z]-[A-Za-z0-9]", core))  # gạch nối Latin


def _shape(token: str) -> str:
    """Dạng so sánh: bỏ dấu, chữ thường, quy nhầm lẫn OCR kinh điển "rn" → "m"."""
    return strip_diacritics(_core(token)).casefold().replace("rn", "m")


def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _shape(a), _shape(b), autojunk=False).ratio()


def _check_pair(
    before: str, after: str, next_before: str | None, glossary: GlossaryIndex, min_sim: float
) -> tuple[bool, Rule, str | None]:
    """(chấp nhận?, luật, gợi ý-cho-người-duyệt) cho 1 cặp token."""
    if _has_digit(before) or _has_digit(after) or looks_like_misread_number(before, next_before):
        if _digit_letter_fix(before, after):
            return True, "digit_letter", None
        suspect = looks_like_misread_number(before, next_before)
        return False, "G-num", after if suspect else None
    if is_protected(before, glossary):  # kể cả đổi sang thuật ngữ khác (mg → g)
        return False, "G-protect", None
    if _punct(before) != _punct(after):
        return False, "G-punct", None
    if similarity(before, after) < min_sim:
        return False, "G-sim", None
    return True, "ok", None


MIN_TOKENS_FOR_RATIO = 5  # đoạn ngắn (ô bảng, tiêu đề 1-2 từ): chỉ dùng luật theo token


def _substantive_changes(
    a: list[str], b: list[str], ops: Sequence[tuple[str, int, int, int, int]]
) -> int:
    """Số token đổi THỰC CHẤT - không tính sửa dấu thuần túy (luôn an toàn)."""
    count = 0
    for tag, i1, i2, j1, j2 in ops:
        if tag == "equal":
            continue
        if tag == "replace" and i2 - i1 == j2 - j1:
            count += sum(_shape(x) != _shape(y) for x, y in zip(a[i1:i2], b[j1:j2], strict=True))
        elif tag == "replace" and _shape("".join(a[i1:i2])) == _shape("".join(b[j1:j2])):
            continue  # tách/dính từ giữ nguyên chữ cái - an toàn như sửa dấu
        else:
            count += max(i2 - i1, j2 - j1)
    return count


def apply_guarded_fix(
    original: str,
    proposed: str,
    glossary: GlossaryIndex,
    *,
    min_similarity: float = 0.6,
    max_changed_ratio: float = 0.35,
) -> GuardResult:
    """Áp các thay đổi hợp lệ của `proposed` lên `original` (theo token)."""
    a, b = original.split(), nfc(proposed).split()
    if a == b:
        return GuardResult(text=original)
    ops = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
    if len(a) >= MIN_TOKENS_FOR_RATIO and _substantive_changes(a, b, ops) > max_changed_ratio * len(
        a
    ):
        fix = Fix(position=0, before=original, after=nfc(proposed), accepted=False, rule="G-ratio")
        return GuardResult(text=original, fixes=[fix], flags=["fix_rejected"])

    out: list[str] = []
    fixes: list[Fix] = []
    flags: set[str] = set()
    for tag, i1, i2, j1, j2 in ops:
        if tag == "equal":
            out.extend(a[i1:i2])
            continue
        before, after = " ".join(a[i1:i2]), " ".join(b[j1:j2])
        if tag == "replace" and i2 - i1 == j2 - j1:  # đổi từng token tương ứng
            for k in range(i2 - i1):
                tb, ta = a[i1 + k], b[j1 + k]
                if tb == ta:
                    out.append(tb)
                    continue
                nxt = a[i1 + k + 1] if i1 + k + 1 < len(a) else None
                ok, rule, suggestion = _check_pair(tb, ta, nxt, glossary, min_similarity)
                out.append(ta if ok else tb)
                fixes.append(
                    Fix(
                        position=i1 + k,
                        before=tb,
                        after=ta,
                        accepted=ok,
                        rule=rule,
                        suggestion=suggestion,
                    )
                )
                if suggestion is not None:
                    flags.add("dose_suspect")
                elif rule == "G-num":
                    flags.add("number_change_rejected")
            continue
        # số token khác nhau: chỉ chấp nhận tách/dính từ (cùng chữ sau khi bỏ dấu + khoảng trắng)
        same_letters = tag == "replace" and (
            strip_diacritics("".join(a[i1:i2])).casefold()
            == strip_diacritics("".join(b[j1:j2])).casefold()
        )
        ok = (
            same_letters
            and not _has_digit(before)
            and not any(is_protected(t, glossary) for t in a[i1:i2])
        )
        span_rule: Rule = "split_merge" if ok else ("G-num" if _has_digit(before) else "G-insdel")
        out.extend(b[j1:j2] if ok else a[i1:i2])
        fixes.append(Fix(position=i1, before=before, after=after, accepted=ok, rule=span_rule))
    if any(not f.accepted for f in fixes):
        flags.add("fix_partially_rejected")
    return GuardResult(text=" ".join(out), fixes=fixes, flags=sorted(flags))
