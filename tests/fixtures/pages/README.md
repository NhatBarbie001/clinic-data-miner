# Fixture trang PDF (P0.5)

Trích từ **sách mẫu tổng hợp** (`dm dev make-sample-book`, seed 7) bằng `scripts/export_p05_samples.py`.
Mỗi file là các span text của lớp OCR (text, bbox, cỡ chữ, font, flags) của một trang - đúng dạng
PyMuPDF trả về - để test P1/P2 chạy nhanh mà không cần sinh lại PDF.

| File | Trang | Vì sao chọn |
|---|---|---|
| `book01_page_003.json` | Mục lục | dòng chấm dẫn + số trang in |
| `book01_page_004.json` | Đầu chương 1 | tiêu đề chương/bệnh/mục, không có header, nhiều lỗi OCR |
| `book01_page_007.json` | Trang in 4 | lỗi liều thuốc `5OO mg`, header chạy, footer |
| `book01_page_009.json` | Trang in 6 | bảng phác đồ (ô rời nhau), lỗi `l g`, dòng NFD |

Đáp án đầy đủ: `samples/P0.5/book01.truth.json`.
