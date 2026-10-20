"""P0.4 - Đọc/ghi JSONL an toàn. Số (#) khớp mục 5 của docs/phases/P0/P0.4_plan.md."""

import json
import unicodedata
from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import Field

from dataminer.core.io import (
    DataFileError,
    append_jsonl,
    file_info,
    read_done_ids,
    read_json,
    read_jsonl,
    repair_tail,
    write_json,
    write_jsonl,
)
from dataminer.core.schemas import BaseRecord

NFC = unicodedata.normalize("NFC", "Viêm khớp dạng thấp - đau, sưng khớp")
NFD = unicodedata.normalize("NFD", "Viêm khớp dạng thấp - đau, sưng khớp")


class Item(BaseRecord):
    name: str
    pages: list[int] = Field(default_factory=list)


def items(n: int) -> list[Item]:
    return [Item(id=f"i{k}", name=f"Bệnh số {k}", pages=[k]) for k in range(n)]


# ---------------------------------------------------------------- 1: roundtrip


def test_01_roundtrip_preserves_text_byte_exact(tmp_path: Path) -> None:
    assert NFC != NFD  # hai dạng Unicode thật sự khác nhau
    records = [
        Item(id="a", name=NFC),
        Item(id="b", name=NFD),
        Item(id="c", name='Có "ngoặc kép", \\ gạch chéo,\nxuống dòng và tab\t; µg/kg ≥ 5 °C'),
    ]
    path = tmp_path / "out" / "items.jsonl"  # thư mục con chưa tồn tại
    assert write_jsonl(path, records) == 3
    back = list(read_jsonl(path, Item))
    assert back == records
    assert back[0].name == NFC
    assert back[1].name == NFD  # io KHÔNG tự chuẩn hóa
    raw = path.read_text(encoding="utf-8")
    assert "Viêm" in raw  # ensure_ascii=False: đọc được bằng mắt, không phải \\u...
    assert raw.count("\n") == 3


# ---------------------------------------------------------------- 2: atomic


def test_02_atomic_write_keeps_old_file_on_error(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    write_jsonl(path, items(2))
    before = path.read_bytes()

    def broken() -> Iterator[Item]:
        yield Item(id="x", name="mới")
        raise RuntimeError("tiến trình lỗi giữa chừng")

    with pytest.raises(RuntimeError):
        write_jsonl(path, broken())
    assert path.read_bytes() == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["items.jsonl"]  # không còn file tạm


# ---------------------------------------------------------------- 3-5: đọc lỗi


def test_03_schema_error_reports_file_line_and_field(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    path.write_text(
        '{"id": "a", "name": "ok"}\n{"id": "b", "name": "ok"}\n{"id": "c", "pages": ["x"]}\n',
        encoding="utf-8",
    )
    with pytest.raises(DataFileError) as info:
        list(read_jsonl(path, Item))
    msg = str(info.value)
    assert msg.startswith("items.jsonl:3:")
    assert "name: thiếu giá trị bắt buộc" in msg  # thông báo tiếng Việt (errors_vi)
    assert "pages.0: phải là số nguyên (nhận: 'x')" in msg
    assert "Field required" not in msg


def test_04_invalid_json_reports_line(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    path.write_text('{"id": "a", "name": "ok"}\n{"id": "b", name}\n', encoding="utf-8")
    with pytest.raises(DataFileError) as info:
        list(read_jsonl(path, Item))
    assert "items.jsonl:2: không phải JSON" in str(info.value)


def test_04b_missing_file(tmp_path: Path) -> None:
    with pytest.raises(DataFileError):
        list(read_jsonl(tmp_path / "khong_co.jsonl", Item))


def test_05_blank_lines_and_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    path.write_text(
        '\n{"id": "a", "name": "x"}\n\n   \n{"id": "b", "name": "y"}\n', encoding="utf-8"
    )
    assert [r.id for r in read_jsonl(path, Item)] == ["a", "b"]
    empty = tmp_path / "empty.jsonl"
    assert write_jsonl(empty, []) == 0
    assert list(read_jsonl(empty, Item)) == []


# ---------------------------------------------------------------- 6-7: chạy tiếp


def test_06_resume_skips_done_ids(tmp_path: Path) -> None:
    path = tmp_path / "progress.jsonl"
    todo = items(5)
    for rec in todo[:3]:  # lần chạy 1 dừng sau 3 bản ghi
        append_jsonl(path, rec)

    done = read_done_ids(path)
    assert done == {"i0", "i1", "i2"}
    remaining = [r for r in todo if r.id not in done]
    for rec in remaining:  # lần chạy 2
        append_jsonl(path, rec)
    assert [r.id for r in read_jsonl(path, Item)] == ["i0", "i1", "i2", "i3", "i4"]


def test_07_truncated_tail_is_repaired(tmp_path: Path) -> None:
    path = tmp_path / "progress.jsonl"
    for rec in items(2):
        append_jsonl(path, rec)
    with path.open("a", encoding="utf-8") as fh:
        fh.write('{"id": "i2", "name": "Bệnh đang gh')  # tiến trình chết giữa lúc ghi

    assert read_done_ids(path) == {"i0", "i1"}  # tự dọn dòng dở
    assert [r.id for r in read_jsonl(path, Item)] == ["i0", "i1"]
    append_jsonl(path, items(3)[2])  # ghi tiếp bình thường
    assert [r.id for r in read_jsonl(path, Item)] == ["i0", "i1", "i2"]


def test_07b_complete_tail_without_newline_is_kept(tmp_path: Path) -> None:
    path = tmp_path / "p.jsonl"
    path.write_text('{"id": "a", "name": "x"}', encoding="utf-8")  # JSON đủ, thiếu "\n"
    assert repair_tail(path) is False
    append_jsonl(path, Item(id="b", name="y"))
    assert [r.id for r in read_jsonl(path, Item)] == ["a", "b"]


def test_07c_single_broken_line(tmp_path: Path) -> None:
    path = tmp_path / "p.jsonl"
    path.write_text('{"id": "a", "na', encoding="utf-8")
    assert repair_tail(path) is True
    assert path.read_bytes() == b""
    assert read_done_ids(tmp_path / "chua_co.jsonl") == set()


def test_07d_corrupt_middle_line_is_an_error(tmp_path: Path) -> None:
    path = tmp_path / "p.jsonl"
    path.write_text('{"id": "a"}\n{hỏng}\n{"id": "c"}\n', encoding="utf-8")
    with pytest.raises(DataFileError) as info:
        read_done_ids(path)
    assert "p.jsonl:2" in str(info.value)


# ---------------------------------------------------------------- json, file_info


def test_write_read_json_atomic(tmp_path: Path) -> None:
    path = tmp_path / "m" / "manifest.json"
    write_json(path, {"phase": "p1", "ghi_chú": "tiếng Việt"})
    assert read_json(path) == {"phase": "p1", "ghi_chú": "tiếng Việt"}
    assert "tiếng Việt" in path.read_text(encoding="utf-8")
    (tmp_path / "bad.json").write_text("{", encoding="utf-8")
    with pytest.raises(DataFileError):
        read_json(tmp_path / "bad.json")


def test_file_info(tmp_path: Path) -> None:
    path = tmp_path / "data" / "items.jsonl"
    write_jsonl(path, items(4))
    info = file_info(path, tmp_path)
    assert info.path == "data/items.jsonl"
    assert info.records == 4
    assert info.bytes == path.stat().st_size
    assert len(info.sha256) == 64
    # Nội dung đổi → sha256 đổi
    write_jsonl(path, items(5))
    assert file_info(path, tmp_path).sha256 != info.sha256
    # File nhị phân: không đếm bản ghi
    pdf = tmp_path / "book.pdf"
    pdf.write_bytes(b"%PDF-1.7\x00\xff")
    assert file_info(pdf, tmp_path, records=False).records is None


def test_written_lines_are_plain_json(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    write_jsonl(path, items(1))
    line = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    assert line == {"id": "i0", "schema_version": 1, "name": "Bệnh số 0", "pages": [0]}
