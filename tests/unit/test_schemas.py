"""P0.4 - BaseRecord (schema_version, khóa lạ) và stable_id. #8-#10 của plan."""

import unicodedata
from typing import ClassVar

import pytest
from pydantic import ValidationError

from dataminer.core.schemas import BaseRecord, stable_id


class V1(BaseRecord):
    name: str


class V2(BaseRecord):
    SCHEMA_VERSION: ClassVar[int] = 2
    name: str


def test_08_schema_version_filled_automatically() -> None:
    assert V1(id="a", name="x").schema_version == 1
    assert V2(id="a", name="x").schema_version == 2
    assert V2.model_validate({"id": "a", "name": "x"}).schema_version == 2


def test_08b_version_mismatch_explains_what_to_do() -> None:
    old = V1(id="a", name="x").model_dump()  # dữ liệu do code v1 tạo
    with pytest.raises(ValidationError) as info:
        V2.model_validate(old)
    msg = str(info.value)
    assert "schema_version=1" in msg
    assert "V2 là v2" in msg
    assert "chạy lại phase" in msg


def test_09_unknown_field_rejected() -> None:
    with pytest.raises(ValidationError) as info:
        V1.model_validate({"id": "a", "name": "x", "nmae": "gõ nhầm"})
    assert "nmae" in str(info.value)


def test_09b_empty_id_rejected() -> None:
    with pytest.raises(ValidationError):
        V1(id="", name="x")


def test_10_stable_id_deterministic() -> None:
    a = stable_id("book01", 12, "Viêm khớp dạng thấp", prefix="node")
    b = stable_id("book01", 12, "Viêm khớp dạng thấp", prefix="node")
    assert a == b
    assert a.startswith("node_")
    assert len(a) == len("node_") + 16
    assert len(stable_id("x")) == 16


def test_10b_stable_id_unicode_normalized() -> None:
    nfc = unicodedata.normalize("NFC", "Triệu chứng")
    nfd = unicodedata.normalize("NFD", "Triệu chứng")
    assert nfc != nfd
    assert stable_id(nfc) == stable_id(nfd)


def test_10c_stable_id_sensitive_to_parts() -> None:
    assert stable_id("ab", "c") != stable_id("a", "bc")  # ranh giới các phần
    assert stable_id("a", "b") != stable_id("b", "a")  # thứ tự
    assert stable_id("a", prefix="x") != stable_id("a", prefix="y")
    assert stable_id(1) == stable_id("1")  # số được chuyển thành chuỗi
