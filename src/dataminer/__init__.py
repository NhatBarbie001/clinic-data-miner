"""Data-miner: khai thác dữ liệu y khoa từ sách PDF (đã OCR).

Các module con theo phase (xem plan.md):
    core        dùng chung
    ingest      P1 trích xuất & làm sạch
    structure   P2 dựng cây cấu trúc
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
    "ingest",
    "structure",
    "index",
    "kb",
    "qa",
    "batch",
    "datagen",
    "evaluation",
    "devtools",
)

__all__ = ["SUBMODULES", "__version__"]
