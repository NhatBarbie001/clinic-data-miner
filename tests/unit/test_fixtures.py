"""P0.5c - Fixture trang (tests/fixtures/pages) đủ đặc trưng cho test P1/P2."""

import json
import unicodedata
from pathlib import Path
from typing import Any

import pytest

PAGES = Path(__file__).resolve().parents[1] / "fixtures" / "pages"


def load(page: int) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(
        (PAGES / f"book01_page_{page:03d}.json").read_text(encoding="utf-8")
    )
    return data


def texts(page: int) -> list[str]:
    return [unicodedata.normalize("NFC", s["text"]) for s in load(page)["spans"]]


@pytest.mark.parametrize("page", [3, 4, 7, 9])
def test_fixture_structure(page: int) -> None:
    data = load(page)
    assert data["page"] == page
    assert data["images"] == 1  # lớp ảnh scan
    assert data["spans"]
    for span in data["spans"]:
        assert set(span) == {"text", "bbox", "size", "font", "flags"}
        assert len(span["bbox"]) == 4


def test_toc_page_has_dot_leaders() -> None:
    assert sum("....." in t for t in texts(3)) == 5


def test_chapter_page_has_no_running_header() -> None:
    first = load(4)["spans"][0]
    assert first["text"].startswith("CHƯƠNG 1")
    assert first["size"] > 13


def test_dose_error_page() -> None:
    assert any("5OO mg" in t for t in texts(7))
    assert any(t.startswith("– 4 –") for t in texts(7))  # footer số trang in


def test_table_page() -> None:
    page = texts(9)
    assert "l g" in page  # lỗi liều trong ô bảng
    assert {"Omeprazol", "Amoxicilin", "Clarithromycin"} <= set(page)
    raw = [s["text"] for s in load(9)["spans"]]
    assert any(not unicodedata.is_normalized("NFC", t) for t in raw)  # có dòng NFD
