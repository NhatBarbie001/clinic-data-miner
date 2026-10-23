"""Data-miner: khai thác dữ liệu y khoa từ sách PDF (đã OCR).

Các module con theo phase (xem plan.md):
    core        dùng chung (cấu hình, AI, cache, manifest, I/O)
    model       hợp đồng dữ liệu giữa các bước: Line, Block, TocEntry, HeadingDecision, Node
    pdf         đọc PDF: dòng, thứ tự đọc, đầu/chân trang, số trang in
    text        ghép dòng → block (đoạn, tiêu đề, gạch đầu dòng, bảng)
    ocrfix      sửa lỗi OCR bằng LLM + bộ lọc an toàn + duyệt CSV
    structure   P2 dựng cây cấu trúc (mục lục, cấp tiêu đề, cây, loại mục)
    pipeline    chạy cả chuỗi P1, P2 (manifest, đầu ra, báo cáo)
    survey      khảo sát sách mới, chương mẫu (pilot)
    books       LUẬT RIÊNG từng sách (book01 = sách mẫu), qua giao diện books.base.BookRules
    index       P3 index & retrieval
    kb          P4 knowledge base
    qa          P5 hỏi đáp
    batch       P6 batch & export
    datagen     P7 sinh dữ liệu huấn luyện
    evaluation  đánh giá xuyên suốt
    devtools    công cụ phát triển (sách mẫu tổng hợp, đối chiếu đáp án) - không thuộc pipeline
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("dataminer")
except PackageNotFoundError:  # chạy từ source chưa cài đặt
    __version__ = "0.0.0+unknown"

SUBMODULES: tuple[str, ...] = (
    "core",
    "model",
    "pdf",
    "text",
    "ocrfix",
    "structure",
    "pipeline",
    "survey",
    "books",
    "index",
    "kb",
    "qa",
    "batch",
    "datagen",
    "evaluation",
    "devtools",
)

__all__ = ["SUBMODULES", "__version__"]
