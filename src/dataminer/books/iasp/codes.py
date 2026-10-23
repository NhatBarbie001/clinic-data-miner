"""Sách IASP - mã hội chứng (L8) và mã IASP 5 trục (L11).

Mã hội chứng ở CUỐI tên: "Tumors of the Brachial Plexus (XI-1)". Sách in không thống nhất:
nhóm I-III in bằng chữ số "(1-4)", "(11-13)", "(111-2)" (= I-4, II-13, III-2); chữ I thay số 1
"(XXV-I)"; có dấu cách "(XIX- 2)"; mã con "(1-16.1)". Ngoặc cuối không phải mã: "(CRPS)".

Mã IASP 5 trục trong mục "Code": "102.X4b", "203.X1cR", "222.68a", "2XX.XXz". Lỗi kiểu chữ
thường gặp: l thay 1 ("203.XlcR") và ngược lại ("006.X81" = 006.X8l), O thay 0 ("X34.XOa"),
có cách ("X4X.X l b", "023 .X l b"), x thường ("002.x2a").
"""

import re

from dataminer.core.text_vi import nfc

RE_ROMAN = re.compile(r"^[IVXLC]+$")
# "(XI-1)", "(1-16.1)", "(XIX- 2)", "(XXV-I)"; RE_CODE_END: ở cuối tên
_CODE = r"\(\s*([0-9IVXLC]+)\s*-\s*([0-9Il]+(?:\.[0-9Il]+)?)\s*\)"
RE_CODE = re.compile(_CODE)
RE_CODE_END = re.compile(_CODE + r"\s*$")
RE_IASP_CODE = re.compile(
    r"(?<![\w.])((?:[0-9XOl]\s?){2}[0-9XOl])\s?\.\s?"  # trục I-III: "203", "X1X", "2XX"
    r"([0-9XxO])\s?([0-9OlIX])\s?([a-z1]?)([RSC]{0,2})"  # trục IV-V + chữ + hậu tố: ".X1cR"
    r"(?![A-Za-z0-9])"
)


def _group(raw: str) -> str | None:
    """Phần nhóm của mã: La Mã giữ nguyên; "1", "11", "111" (chữ I in thành số 1) → I, II, III."""
    if RE_ROMAN.match(raw):
        return raw
    if set(raw) == {"1"} and len(raw) <= 3:
        return "I" * len(raw)
    return None


def _normalize(match: re.Match[str]) -> str | None:
    group = _group(match.group(1))
    if group is None:
        return None
    return f"{group}-{match.group(2).replace('I', '1').replace('l', '1')}"


def syndrome_code(title: str) -> str | None:
    """Mã hội chứng đã chuẩn hóa ở cuối tên ("XI-1", "I-16.1"), None nếu không có."""
    match = RE_CODE_END.search(" ".join(nfc(title).split()))
    return _normalize(match) if match else None


def syndrome_codes(title: str) -> list[str]:
    """MỌI mã hội chứng trong tên - mục gộp 2 hội chứng:
    "Intermittent Claudication (XV-1) and Rest Pain (XV-2)" → ["XV-1", "XV-2"]."""
    found = (_normalize(m) for m in RE_CODE.finditer(" ".join(nfc(title).split())))
    return [c for c in found if c]


def strip_code(title: str) -> str:
    """Tên hội chứng bỏ mã ở cuối: "Tumors of the Brachial Plexus (XI-1)" → "Tumors of the …"."""
    text = " ".join(nfc(title).split())
    return RE_CODE_END.sub("", text).strip() if syndrome_code(text) else text


def iasp_codes(text: str) -> list[str]:
    """Mọi mã IASP 5 trục trong `text`, đã chuẩn hóa (l→1, O→0, x→X, bỏ cách), giữ thứ tự,
    không lặp."""
    out: list[str] = []
    for m in RE_IASP_CODE.finditer(nfc(text)):
        head = m.group(1).replace(" ", "").replace("O", "0").replace("l", "1")
        axis4 = m.group(2).upper().replace("O", "0")
        axis5 = m.group(3).replace("O", "0").replace("l", "1").replace("I", "1")
        letter = m.group(4).replace("1", "l")  # chữ l in thành số 1: "006.X81", "533.X11S"
        code = f"{head}.{axis4}{axis5}{letter}{m.group(5)}"
        if code not in out:
            out.append(code)
    return out
