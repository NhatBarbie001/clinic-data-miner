"""P0.5 - Tiện ích tiếng Việt: âm tiết hợp lệ, dấu thanh, chuẩn hóa Unicode."""

import re
import unicodedata

import pytest

from dataminer.core.text_vi import (
    has_vietnamese_marks,
    is_nfc,
    is_valid_syllable,
    strip_diacritics,
    strip_tones,
)
from dataminer.devtools import sample_book_content as content


@pytest.mark.parametrize(
    "word",
    [
        "khớp",
        "nghiêng",
        "giường",
        "quyết",
        "uyên",
        "Ợ",
        "ổ",
        "thuốc",
        "ngoài",
        "khuẩn",
        "giữa",
        "chuyển",
        "người",
        "TRIỆU",
        "CHỨNG",
        "Đau",
        "ăn",
        "ươn",
        "khuya",
        "khoẻ",
        "lý",
        "dưỡng",
    ],
)
def test_valid_syllables(word: str) -> None:
    assert is_valid_syllable(word)


@pytest.mark.parametrize(
    "word",
    [
        "viêrn",
        "kbớp",
        "tbuốc",
        "rnỗi",
        "đaukhớp",
        "phảnứng",
        "corticoidnội",
        "ngàyy",
        "khớpp",
        "mạnhcơ",
    ],
)
def test_invalid_syllables_from_ocr_errors(word: str) -> None:
    assert not is_valid_syllable(word)


def test_no_false_positive_on_book_text() -> None:
    """Mọi từ có dấu trong nội dung sách mẫu (văn bản sạch) phải là âm tiết hợp lệ."""
    texts: list[str] = []
    for item in content.BOOK:
        for part in item[1:]:
            if isinstance(part, str):
                texts.append(part)
            elif isinstance(part, list):
                for x in part:
                    texts.extend(x if isinstance(x, list) else [x])
    words = [w for t in texts for w in re.findall(r"[^\W\d_]+", t) if has_vietnamese_marks(w)]
    assert len(words) > 500
    assert [w for w in words if not is_valid_syllable(w)] == []


def test_strip_tones_keeps_vowel_marks() -> None:
    assert strip_tones("khớp") == "khơp"
    assert strip_tones("Triệu chứng") == "Triêu chưng"
    assert strip_tones("đau") == "đau"


def test_strip_diacritics() -> None:
    assert strip_diacritics("Đau khớp gối") == "Dau khop goi"


def test_marks_and_normalization() -> None:
    assert has_vietnamese_marks("khớp")
    assert has_vietnamese_marks("đau")
    assert not has_vietnamese_marks("khop")
    assert not has_vietnamese_marks("Helicobacter")
    nfd = unicodedata.normalize("NFD", "khớp")
    assert not is_nfc(nfd)
    assert has_vietnamese_marks(nfd)
    assert is_valid_syllable(nfd)  # NFD vẫn được chuẩn hóa trước khi kiểm tra
