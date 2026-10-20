"""Tiện ích văn bản tiếng Việt: chuẩn hóa Unicode, dấu thanh, kiểm tra âm tiết hợp lệ.

`is_valid_syllable` kiểm tra CẤU TRÚC chính tả (phụ âm đầu + vần + phụ âm cuối), không phải
từ điển: "khop" (mất dấu) vẫn hợp lệ về cấu trúc, nhưng "viêrn", "kbớp", "đaukhớp" thì không.
Dùng để phát hiện lỗi OCR kiểu nhầm ký tự / dính từ trên các token có chữ đặc thù tiếng Việt.
"""

import re
import unicodedata

TONE_MARKS = frozenset("̣̀́̃̉")  # huyền, sắc, ngã, hỏi, nặng
VI_SPECIFIC = frozenset("ăâêôơưđĂÂÊÔƠƯĐ")

_ONSETS = "ngh|ng|nh|ch|gh|gi|kh|ph|qu|th|tr|b|c|d|đ|g|h|k|l|m|n|p|r|s|t|v|x"
_NUCLEI = (
    # 3 nguyên âm
    "iêu|yêu|oai|oay|oeo|uây|uôi|ươi|ươu|uya|uyê|uyu|"
    # 2 nguyên âm
    "ai|ao|au|ay|âu|ây|eo|êu|ia|iê|iu|oa|oă|oe|oi|ôi|ơi|ua|uâ|uê|ui|uô|uơ|ưa|ưi|ưu|ươ|uy|yê|"
    # 1 nguyên âm
    "a|ă|â|e|ê|i|y|o|ô|ơ|u|ư"
)
_CODAS = "ch|ng|nh|c|m|n|p|t"
_SYLLABLE = re.compile(f"(?:{_ONSETS})?(?:{_NUCLEI})(?:{_CODAS})?")


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def is_nfc(text: str) -> bool:
    return unicodedata.is_normalized("NFC", text)


def strip_tones(text: str) -> str:
    """Bỏ dấu thanh, GIỮ dấu mũ/móc/trăng và đ: "khớp" → "khơp"."""
    decomposed = unicodedata.normalize("NFD", text)
    return nfc("".join(c for c in decomposed if c not in TONE_MARKS))


def strip_diacritics(text: str) -> str:
    """Bỏ mọi dấu: "Đau khớp" → "Dau khop"."""
    decomposed = unicodedata.normalize("NFD", text)
    plain = "".join(c for c in decomposed if not unicodedata.combining(c))
    return plain.replace("đ", "d").replace("Đ", "D")


def has_vietnamese_marks(token: str) -> bool:
    """Token có dấu thanh hoặc chữ đặc thù (ă â ê ô ơ ư đ) → chắc chắn là chữ Việt."""
    decomposed = unicodedata.normalize("NFD", token)
    return any(c in TONE_MARKS for c in decomposed) or any(c in VI_SPECIFIC for c in nfc(token))


def is_valid_syllable(token: str) -> bool:
    """Token (chỉ gồm chữ) có cấu trúc một âm tiết tiếng Việt hợp lệ không."""
    base = strip_tones(token).lower()
    return bool(base) and _SYLLABLE.fullmatch(base) is not None
