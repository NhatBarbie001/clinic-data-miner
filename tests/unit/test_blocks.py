"""P1.3 - Dựng block. Số (#) khớp mục 5 của docs/phases/P1/P1.3_plan.md.

Phần "không dựa trên sách mẫu" là BẮT BUỘC: sách mẫu không có 2 đoạn văn liền nhau và chỉ có
1 block ngắt qua trang - tắt hẳn 2 quy tắc đó mà sách mẫu vẫn đạt 98.96% (xem P1.3_report).
"""

from pathlib import Path

import pytest

from dataminer.core.config import BlocksCfg
from dataminer.devtools.sample_book import SampleBook
from dataminer.evaluation.p1_eval import eval_blocks
from dataminer.ingest.blocks import build_blocks, classify_line, join_text
from dataminer.ingest.page_furniture import strip_furniture
from dataminer.ingest.pdf_reader import body_font_size, read_lines
from dataminer.model.block import Block
from dataminer.model.line import Line
from tests.conftest import SampleBookFor

CFG = BlocksCfg()


def pipeline(pdf: Path, pages: tuple[int, int] = (1, 9)) -> tuple[list[Block], list[Line]]:
    lines = read_lines(pdf, pages=pages)
    body = body_font_size(lines)
    fr = strip_furniture(lines, body, pdf_pages=list(range(pages[0], pages[1] + 1)))
    printed = {p.page: p.printed_page for p in fr.pages}
    return build_blocks(fr.content, body, CFG, printed), fr.content


@pytest.fixture(scope="module")
def book(sample_book_for: SampleBookFor) -> SampleBook:
    return sample_book_for(7)


@pytest.fixture(scope="module")
def built(book: SampleBook) -> tuple[list[Block], list[Line]]:
    return pipeline(book.pdf_path)


# Dòng tự dựng: mỗi dòng cao 13pt; dòng tiếp của cùng đoạn cách 14.5pt (như sách mẫu).
_counter = iter(range(10_000))


def mk(
    text: str, y: float, x: float = 48, *, page: int = 1, size: float = 10.5, width: float = 280
) -> Line:
    n = next(_counter)
    return Line(
        id=f"t{n}",
        page=page,
        index=n,
        text=text,
        bbox=(x, y, x + width, y + 13),
        size=size,
        font="f",
        bold=False,
        zone="body",
    )


def texts(blocks: list[Block]) -> list[tuple[str, str]]:
    return [(b.kind, b.text) for b in blocks]


# ---------------------------------------------------------------- trên sách mẫu


@pytest.mark.parametrize("seed", [7, 2, 6])
def test_01_blocks_match_truth(sample_book_for: SampleBookFor, seed: int) -> None:
    sample = sample_book_for(seed)
    blocks, content = pipeline(sample.pdf_path)
    report = eval_blocks(blocks, content, sample.truth)
    g3 = report["G3_blocks"]
    assert g3["pass"], g3
    assert g3["merged_across_headings"] == []
    assert report["G4_tables"]["pass"], report["G4_tables"]


def test_01b_pilot_scope(book: SampleBook) -> None:
    blocks, content = pipeline(book.pdf_path, pages=(4, 9))
    report = eval_blocks(blocks, content, book.truth)
    assert report["G3_blocks"]["pass"]
    assert report["G3_blocks"]["truth_blocks"] == 85


def test_02_cross_page_block(built: tuple[list[Block], list[Line]]) -> None:
    blocks, _ = built
    joined = [b for b in blocks if "joined_across_pages" in b.flags]
    assert len(joined) == 1
    (b,) = joined
    assert b.kind == "list_item"
    assert (b.page_start, b.page_end) == (4, 5)
    assert (b.printed_start, b.printed_end) == (1, 2)
    assert b.text.endswith("bàn tay gió thổi.")
    assert len(b.line_ids) == 2


def test_03_table_and_caption(built: tuple[list[Block], list[Line]]) -> None:
    blocks, _ = built
    (table,) = [b for b in blocks if b.kind == "table"]
    assert table.rows is not None
    assert len(table.rows) == 4
    assert all(len(r) == 4 for r in table.rows)
    assert table.rows[2][1] == "l g"  # lỗi liều cài sẵn - đúng ô
    assert len(table.line_ids) == 16
    idx = blocks.index(table)
    assert blocks[idx - 1].kind == "caption"
    assert blocks[idx - 1].text.startswith("Bảng 2.1.")


def test_04_toc_entries(built: tuple[list[Block], list[Line]]) -> None:
    blocks, _ = built
    toc = [b for b in blocks if b.kind == "toc_entry"]
    assert len(toc) == 5
    assert all(b.page_start == 3 for b in toc)
    assert not any(b.kind == "heading" and "...." in b.text for b in blocks)


def test_07_subsection_heading_features(built: tuple[list[Block], list[Line]]) -> None:
    blocks, _ = built
    sub = next(b for b in blocks if b.text.startswith("3.1."))
    assert sub.kind == "heading"
    assert sub.numbering == "3.1"
    assert not sub.is_upper
    chapter = next(b for b in blocks if b.text.startswith("CHƯƠNG 1"))
    assert chapter.numbering == "CHƯƠNG 1"
    assert chapter.is_upper
    disease = next(b for b in blocks if b.text == "VIÊM KHỚP DẠNG THẤP")
    assert disease.kind == "heading"
    assert disease.numbering is None
    assert disease.font_size > chapter.font_size - 3


def test_10_traceability(built: tuple[list[Block], list[Line]]) -> None:
    blocks, content = built
    ids = [lid for b in blocks for lid in b.line_ids]
    assert sorted(ids) == sorted(ln.id for ln in content)  # mọi dòng thuộc đúng 1 block
    assert len({b.id for b in blocks}) == len(blocks)
    assert all(b.text == b.text_rules for b in blocks)
    assert all(b.printed_start is None for b in blocks if b.page_start <= 3)


def test_stable_ids(book: SampleBook, built: tuple[list[Block], list[Line]]) -> None:
    again, _ = pipeline(book.pdf_path)
    assert [b.id for b in again] == [b.id for b in built[0]]


# ---------------------------------------------------------------- không dựa trên sách mẫu


def test_05_list_item_continuation_and_new_item() -> None:
    lines = [
        mk("- Viêm nhiều khớp nhỏ ở bàn tay như khớp cổ tay, khớp bàn", 100, 58),
        mk("ngón và khớp ngón gần.", 114.5, 64),
        mk("- Cứng khớp buổi sáng kéo dài trên 1 giờ.", 130.5, 58),
    ]
    blocks = build_blocks(lines, 10.5)
    assert texts(blocks) == [
        (
            "list_item",
            "Viêm nhiều khớp nhỏ ở bàn tay như khớp cổ tay, khớp bàn ngón và khớp ngón gần.",
        ),
        ("list_item", "Cứng khớp buổi sáng kéo dài trên 1 giờ."),
    ]
    assert [b.marker for b in blocks] == ["-", "-"]


def test_06_consecutive_paragraphs_split_by_gap() -> None:
    """Hai đoạn cùng lề, cách nhau khoảng dôi ~4pt → 2 block (sách mẫu không có ca này)."""
    lines = [
        mk("Đoạn một dòng thứ nhất kết thúc ở đây.", 100),
        mk("Đoạn một dòng thứ hai vẫn cùng đoạn.", 114.5),
        mk("Đoạn hai bắt đầu sau khoảng trống.", 133),  # 18.5pt: dôi 4pt
        mk("Đoạn hai dòng cuối.", 147.5),
    ]
    blocks = build_blocks(lines, 10.5)
    assert [b.kind for b in blocks] == ["paragraph", "paragraph"]
    assert [len(b.line_ids) for b in blocks] == [2, 2]


def test_06b_line_ending_with_period_inside_paragraph_is_joined() -> None:
    """Câu kết thúc đúng cuối dòng nhưng đoạn vẫn tiếp (khoảng cách bình thường) → nối."""
    lines = [
        mk("xứng. Bệnh gặp chủ yếu ở nữ, tuổi từ 30 đến 50.", 100),
        mk("Nếu không được điều trị, bệnh tiến triển.", 114.5),
    ]
    assert len(build_blocks(lines, 10.5)) == 1


def test_06c_indented_first_line_paragraph() -> None:
    lines = [
        mk("Đoạn thụt đầu dòng bắt đầu ở đây và chạy", 100, 63),
        mk("tiếp về lề trái.", 114.5, 48),
        mk("Đoạn sau cũng thụt đầu dòng.", 129, 63),  # thụt vào lại → đoạn mới
    ]
    assert [len(b.line_ids) for b in build_blocks(lines, 10.5)] == [2, 1]


def test_cross_page_join_rules() -> None:
    def run(prev_text: str, next_text: str, next_x: float = 48) -> int:
        lines = [mk(prev_text, 500, page=4), mk(next_text, 62, next_x, page=5)]
        return len(build_blocks(lines, 10.5))

    assert run("đoạn văn chưa kết thúc ở cuối trang và", "tiếp tục ở trang sau.") == 1
    assert run("đoạn văn đã kết thúc.", "Đoạn mới ở trang sau.") == 2
    assert run("câu chưa xong", "4. ĐIỀU TRỊ") == 2  # trang sau mở đầu bằng tiêu đề
    assert run("câu chưa xong", "- gạch đầu dòng mới", 58) == 2
    lines = [mk("đoạn chưa kết thúc", 500, page=4), mk("tiếp tục.", 62, page=5)]
    assert len(build_blocks(lines, 10.5, BlocksCfg(join_across_pages=False))) == 2


@pytest.mark.parametrize(
    ("text", "size", "kind"),
    [
        ("50 tuổi và là nguyên nhân hàng đầu gây đau khớp gối.", 10.5, "body"),
        ("2 lần mỗi ngày.", 10.5, "body"),
        ("1. Uống thuốc sau ăn no.", 10.5, "numbered_item"),
        ("3. TRIỆU CHỨNG", 10.8, "heading"),
        ("3.1. Lâm sàng", 10.5, "heading"),
        ("CHƯƠNG 2. BỆNH TIÊU HÓA", 14, "heading"),
        ("HEN PHẾ QUẢN", 13, "heading"),
        ("Bảng 2.1. Phác đồ ba thuốc", 9.5, "caption"),
        ("Chương 1. Bệnh khớp .............. 1", 10.5, "toc_entry"),
        ("- Ngừng thuốc gây loét.", 10.5, "bullet_start"),
        ("Một dòng thân bài OCR ước lượng cỡ chữ hơi to.", 11.1, "body"),  # nhiễu cỡ chữ
    ],
)
def test_08_classify_line(text: str, size: float, kind: str) -> None:
    assert classify_line(mk(text, 100, size=size), 10.4, CFG) == kind


def test_numbered_list_item_block() -> None:
    lines = [
        mk("1. Uống thuốc sau ăn no, chia làm", 100),
        mk("hai lần.", 114.5, 61),
        mk("2. Tái khám sau 2 tuần.", 130.5),
    ]
    blocks = build_blocks(lines, 10.5)
    assert texts(blocks) == [
        ("list_item", "Uống thuốc sau ăn no, chia làm hai lần."),
        ("list_item", "Tái khám sau 2 tuần."),
    ]
    assert [b.marker for b in blocks] == ["1.", "2."]


def test_wrapped_long_heading_joined() -> None:
    lines = [
        mk("VIÊM PHỔI MẮC PHẢI Ở CỘNG ĐỒNG DO", 100, size=13.5),
        mk("PHẾ CẦU KHUẨN", 117, size=13.4),
        mk("1. ĐẠI CƯƠNG", 150, size=11.5),
    ]
    blocks = build_blocks(lines, 10.5)
    assert texts(blocks) == [
        ("heading", "VIÊM PHỔI MẮC PHẢI Ở CỘNG ĐỒNG DO PHẾ CẦU KHUẨN"),
        ("heading", "1. ĐẠI CƯƠNG"),
    ]


def test_two_column_table_with_missing_cell() -> None:
    """Bảng 2 cột; hàng cuối thiếu ô liều → vẫn thuộc bảng, ô trống đúng cột. Đoạn văn ngay
    sau bảng (chạy hết chiều ngang) KHÔNG bị nuốt vào bảng."""
    lines = [
        mk("Thuốc", 100, 52, width=40),
        mk("Liều", 100.5, 200, width=30),
        mk("Omeprazol", 116, 52, width=50),
        mk("20 mg", 116.4, 200, width=30),
        mk("Amoxicilin", 132, 52, width=50),  # thiếu ô liều
        mk("Đoạn văn sau bảng chạy hết chiều ngang trang.", 148, 48, width=300),
    ]
    blocks = build_blocks(lines, 10.5)
    assert [b.kind for b in blocks] == ["table", "paragraph"]
    assert blocks[0].rows == [["Thuốc", "Liều"], ["Omeprazol", "20 mg"], ["Amoxicilin", ""]]


def test_missing_cell_in_first_column() -> None:
    lines = [
        mk("Thuốc", 100, 52, width=40),
        mk("Liều", 100, 200, width=30),
        mk("20 mg", 116, 200, width=30),  # thiếu tên thuốc
        mk("Amoxicilin", 132, 52, width=50),
        mk("1 g", 132, 200, width=20),
    ]
    (table,) = build_blocks(lines, 10.5)
    assert table.rows == [["Thuốc", "Liều"], ["", "20 mg"], ["Amoxicilin", "1 g"]]


def test_two_lines_same_row_only_once_is_not_table() -> None:
    lines = [mk("Một dòng", 100, 52), mk("dòng song song", 100.3, 250), mk("Thân bài.", 130)]
    assert all(b.kind != "table" for b in build_blocks(lines, 10.5))


@pytest.mark.parametrize(
    ("a", "b", "joined"),
    [
        ("kháng thể anti-", "CCP có độ đặc hiệu cao", "kháng thể anti-CCP có độ đặc hiệu cao"),
        ("đặc trưng bởi", "tình trạng viêm", "đặc trưng bởi tình trạng viêm"),
        ("liều 7,5-", "15 mg", "liều 7,5- 15 mg"),  # số: không tự ghép (để P1.4/duyệt)
        ("viêm khớp -", "đau", "viêm khớp - đau"),
    ],
)
def test_09_join_text(a: str, b: str, joined: str) -> None:
    assert join_text(a, b) == joined


def test_paragraph_at_margin_after_list_item_not_joined() -> None:
    """Đoạn văn ở lề trái ngay sau gạch đầu dòng, khoảng cách hẹp (chỉ dôi 1.5pt - dưới ngưỡng
    tách đoạn): chỉ lề trái phân biệt được → phải là block riêng."""
    lines = [
        mk("- Ngừng các thuốc gây loét nếu có thể", 100, 58),
        mk("Sau đó đánh giá lại triệu chứng.", 116, 48),
    ]
    assert texts(build_blocks(lines, 10.5)) == [
        ("list_item", "Ngừng các thuốc gây loét nếu có thể"),
        ("paragraph", "Sau đó đánh giá lại triệu chứng."),
    ]
