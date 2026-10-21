# Gate report P1: Trích xuất và làm sạch text

> Ngày: 2026-10-21 · Plan: [plan.md](plan.md) · Bằng chứng: [samples/P1.6/](../../../samples/P1.6/)
>
> **Kết luận: ✅ P1 QUA GATE trên pilot sách mẫu** (trang PDF 4–9, 85 block, khoảng 1.000 từ).
> Lưu ý lớn: sách mẫu do chính mình sinh. Xem mục 4 về những gì **phải kiểm lại khi có sách thật**.

## 1. Đối chiếu từng chỉ tiêu (plan P1, mục 8)

| # | Chỉ tiêu | Ngưỡng | Kết quả | Bằng chứng |
|---|---|---|---|---|
| G1 | Header/footer/số trang bị bỏ | 100%, 0 bỏ nhầm | ✅ **10/10, 0 bỏ nhầm** (cả 3 seed toàn sách) | [p1_eval.txt](../../../samples/P1.6/p1_eval.txt), [P1.2](P1.2_report.md) |
| G2 | Số trang in | 100% | ✅ **6/6**; có suy ra khi thiếu, phát hiện khi mâu thuẫn | như trên |
| G3 | Block đúng tập dòng; 0 gộp nhầm | ≥ 97% | ✅ **85/85 (100%)**, 0 gộp nhầm; **24/24 sách** đều 100% | [P1.3](P1.3_report.md) |
| G4 | Bảng | 4×4 đúng | ✅ **4×4**, ô lỗi liều đúng vị trí | như trên |
| G5 | WER | ≤ 1% | ✅ **4.08% → 0.50%** (LLM) **→ 0.30%** (sau duyệt) | [P1.4](P1.4_report.md), [P1.5](P1.5_report.md) |
| G6 | Lỗi đã cài được sửa | ≥ 80% | ✅ **35/38 = 92%**. Chưa sửa: `dien`, `CHUNG`, `độ` (đều là từ có nghĩa); **1 sửa sai** (`kinh diễn`) | [ocr_eval.txt](../../../samples/P1.4/ocr_eval.txt) |
| G7 | Từ đúng bị sửa sai | ≤ 0.3% | ✅ **0** | như trên |
| G8 | Số liệu | 0 đổi khi chưa duyệt; 2/2 gắn cờ | ✅ Trước duyệt: **giữ nguyên + gắn cờ + gợi ý**. Sau duyệt: **sửa đúng qua người duyệt** (`500`, `1`) | [review_applied.md](../../../samples/P1.5/review_applied.md) |
| G9 | NFC | 100% | ✅ | [p1_eval.txt](../../../samples/P1.6/p1_eval.txt) |
| G10 | Tái lập | $0, giống hệt | ✅ Chạy lại, và replay + `--force`: **cùng sha256**, 0 lời gọi API | [p1_run_again.txt](../../../samples/P1.6/p1_run_again.txt) |
| G11 | Kỹ thuật | Mọi kiểm tra pass; báo cáo + samples | ✅ ruff, mypy strict (44 file), pre-commit; **393 test + 3 live**; 6/6 task có báo cáo và samples | [quality_checks.txt](../../../samples/P1.6/quality_checks.txt) |
| G12 | Duyệt tay | 100% hàng đợi có quyết định | ✅ 2/2 mục số liệu + 4/4 mục kiểm tra mẫu. ⚠️ Người duyệt là **auto-truth (sách mẫu)** | [review_cli.txt](../../../samples/P1.6/review_cli.txt) |

**Chạy thật với DeepSeek: 4 lần độc lập** (P1.4 chạy chính, 2 test live sửa OCR, 1 test live trọn P1), lần nào cũng đạt.

## 2. Tổng kết P1

| Hạng mục | Số liệu |
|---|---|
| Task | 6/6 hoàn thành (P1.1–P1.6), mỗi task có plan, báo cáo, samples, commit |
| Test | **393 offline + 3 live**. Mới trong P1: P1.1: 12 · P1.2: 23 · P1.3: 36 · P1.4: 37 · P1.5: 18 · P1.6: 13 |
| Mutation check | **37 đột biến**, tất cả bị bắt. 4 đột biến ban đầu sống sót đã dẫn tới thêm test |
| Lỗi thật tìm thấy và sửa | **22** (liệt kê ở mục 7 các báo cáo task). Nổi bật: guard từ chối nhầm ô bảng làm mất cờ lỗi liều; `mg`→`g` lọt guard; đánh giá lặng lẽ báo "đạt" khi không đối chiếu được |
| **Chi phí LLM P1** | Sổ chính: **$0.0028**. Cộng 4 lần chạy thật trong sổ tạm của test live: **tổng khoảng $0.015**. Ngân sách `fix_ocr`: $2 |
| Đầu ra cho P2 | `data/p1_clean/blocks.jsonl`: 85 block (27 tiêu đề, 7 đoạn, 49 gạch đầu dòng, 1 chú thích, 1 bảng) có `numbering`, `is_upper`, `font_size`, `x0`, truy vết về dòng và trang |

**Lệnh mới:** `dm p1 run | eval | report | review export [--audit] | review import`.

## 3. Phát hiện quan trọng mang sang P2

1. **Block đã có đủ đặc trưng tiêu đề** (`numbering`, `is_upper`, `font_size`). P2 chỉ cần quyết định cấp: chương / bệnh / mục / mục con, và ánh xạ `section_type`.
2. **Tiêu đề có thể vẫn còn lỗi OCR** sau P1 (`3. TRIỆU CHUNG`: LLM không sửa vì "CHUNG" là từ có nghĩa). P2 khi ánh xạ tên mục **phải so không dấu** (đúng như book_profile mục 2).
3. **Bảng đã có `rows`.** P2/P4 dùng trực tiếp, không cần phân tích lại.
4. **Số trang in** có sẵn trong mỗi block, phục vụ trích dẫn ở P5.

## 4. ⚠️ Rủi ro và tồn đọng

| Mục | Mức | Hành động |
|---|---|---|
| **Chưa có sách thật**: mọi chỉ tiêu đo trên sách mẫu tự sinh | **Cao** | Khi có sách: `dm survey` → cập nhật `book_profile.md` → `dm p1 run` → **duyệt tay khoảng 10 trang** `report.md` (không có đáp án tự động) → `dm p1 review export --audit 0.05` để ước lượng tỉ lệ sửa sai |
| Lỗi tạo ra **từ có nghĩa** (khoảng 8% lỗi đã cài) và **sửa sai** không có tín hiệu nào | Trung bình | Mẫu kiểm tra `--audit` chỉ ước lượng. Nếu tỉ lệ cao: prompt v2, hoặc gửi kèm ngữ cảnh rộng hơn |
| Duyệt tay hiện là auto-truth | Trung bình | Sách thật cần người có chuyên môn y khoa cho hàng đợi `1-SỐ LIỆU` |
| Bảng có ô nhiều dòng, bảng qua 2 trang, sách 2 cột: chưa xử lý | Trung bình | Kiểm khi có sách thật (`dm survey` cảnh báo trang 2 cột) |
| `judge` cùng model với `qa`/`datagen` (từ P0.2) | Trung bình | Quyết định trước P5 |
| Thời gian test khoảng 69 giây | Thấp | Theo dõi |

## 5. Đề xuất bước tiếp theo

**P2: Dựng cấu trúc tài liệu** (plan.md mục P2). Đầu vào: `blocks.jsonl` đã sạch. Đầu ra: cây Chương → Bệnh → Mục → Mục con, kèm `section_type`.

Đáp án sách mẫu đã có sẵn `headings` với `level` và `section_type`, nên P2 cũng đo được bằng số. Chỉ tiêu gate P2 (plan.md): số bệnh khớp mục lục 100%, mục ánh xạ đúng ≥ 95%, `other` < 5%.

Bước đầu tiên: viết `docs/phases/P2/plan.md` để chủ dự án duyệt.
