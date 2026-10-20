# Gate report P0: Setup và khảo sát sách

> Ngày: 2026-10-20 · Plan: [plan.md](plan.md) · Bằng chứng chạy lại hôm nay: [samples/P0.6/gate_evidence.txt](../../../samples/P0.6/gate_evidence.txt)
>
> **Kết luận: ✅ P0 QUA GATE**, có 1 lưu ý lớn: sách dùng để khảo sát là **sách mẫu tổng hợp**. Xem mục 4.

## 1. Đối chiếu từng mục Gate P0

| # | Mục gate (plan P0, mục 8) | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | Mọi task P0.1–P0.6 có báo cáo và mẫu dữ liệu | ✅ 6/6 | Báo cáo: [P0.1](P0.1_report.md) · [P0.2](P0.2_report.md) · [P0.3](P0.3_report.md) · [P0.4](P0.4_report.md) · [P0.5](P0.5_report.md) · [P0.6](P0.6_report.md); `samples/P0.1` … `samples/P0.6` |
| 2 | Kiểm tra cục bộ (ruff, mypy, pytest, pre-commit) pass | ✅ | ruff ✓ · ruff format ✓ · **mypy strict ✓ (31 file)** · **pytest 256 passed** · pre-commit 9/9 ✓ ([quality_checks.txt](../../../samples/P0.6/quality_checks.txt)) |
| 3 | Gọi được OpenRouter qua `llm_client`, cache hoạt động | ✅ | `pytest -m live` **1 passed** (gọi thật); `DM__LLM__MODE=replay dm llm ping`: 2/2 lời gọi `cached=True`, **$0**, không có request HTTP; `dm llm models`: 7/7 tác vụ trỏ tới model tồn tại |
| 4 | `book_profile.md` mô tả được bằng quy tắc "đầu bệnh mới trông thế nào" và "mục Triệu chứng trông thế nào" | ✅ | [book_profile.md](../../book_profile.md) mục 2–3. Khảo sát đối chiếu đáp án: tiêu đề recall 100%, header/footer 100%/100%, **0 báo động giả**, đạt trên **24 sách** |
| 5 | Chương mẫu đã được duyệt | ✅ | Đề xuất "dùng toàn bộ trang 4–9" (cuối P0.5); chủ dự án yêu cầu triển khai (2026-10-20). `dm pilot check`: **pilot HỢP LỆ** |

## 2. Tổng kết P0

| Hạng mục | Số liệu |
|---|---|
| Commit | 6 commit trên `main` (P0.1 → P0.6), đã push lên `origin` (`NhatBarbie001/clinic-data-miner`) |
| Code | 31 file nguồn (`src/dataminer`), mypy strict |
| Test | **256 offline + 1 live**. Theo task: P0.1: 39 · P0.2: 39 · P0.3: 43 · P0.4: 32 · P0.5: 92 · P0.6: 11 |
| Mutation check | 10 lần cố ý làm hỏng code (cache, ngân sách, retry, atomic, repair_tail, nuốt exception, mốc thời gian, dấu thanh...) đều bị test bắt |
| **Chi phí LLM** | Sổ chi phí: **$0.000100** (4 lời gọi). Cộng thăm dò reasoning và các lần chạy test live (dùng sổ chi phí tạm): **khoảng $0.0005**. Ngân sách P0: $1 |
| Lỗi thật tìm thấy và sửa | 15 lỗi, mỗi lỗi có test chống tái diễn (liệt kê trong mục 7 của từng báo cáo) |

**Lệnh CLI đã có:**
```
dm info | version
dm config show | validate
dm llm models | ping | cost
dm runs list | show
dm survey
dm pilot check
dm dev make-sample-book | check-survey
```

**Thành phần lõi P1+ sẽ dùng:**

| Thành phần | Vai trò |
|---|---|
| `core/config` | Cấu hình |
| `core/llm_client` | Cache, retry, ngân sách, `chat_json` |
| `core/io` | Atomic, chạy tiếp được |
| `core/run` | Manifest |
| `core/text_vi` | Âm tiết, dấu |
| `ingest/survey.extract_lines` | Trích dòng từ PDF |
| `devtools/sample_book` | Sách mẫu + **đáp án để đo P1/P2** |

## 3. Phát hiện quan trọng chuyển sang P1

1. **72% lỗi OCR (mất dấu, sai dấu) chỉ sửa được bằng ngữ cảnh**, nên P1 *bắt buộc* cần LLM cho bước sửa. Quy tắc chỉ xử lý được NFC, nối dòng, bỏ header/footer, và phát hiện lỗi số hoặc ký tự lạ.
2. **Lỗi liều thuốc (`5OO mg`, `l g`) phát hiện được 100% bằng quy tắc.** P1 phải **gắn cờ chứ không tự sửa** các lỗi này, kèm guard: số liệu sau khi sửa phải khớp mẫu hợp lệ.
3. **DeepSeek tự suy luận khi không được tắt.** Client đã luôn gửi `reasoning.enabled`, tiết kiệm khoảng 60% token ra. `fix_ocr` để tắt reasoning.
4. **Giá ×2 vào 8–11h và 13–17h giờ Việt Nam (ngày thường).** Nên chạy lô P1 ngoài khung này.
5. **Lớp OCR mất in đậm,** nên P2 nhận diện tiêu đề bằng đánh số, viết hoa và cỡ chữ (đã kiểm chứng ở P0.5).
6. **Bảng:** mỗi ô là một dòng riêng, cùng toạ độ y. P1 cần ghép thành hàng trước khi nối dòng thân bài.

## 4. ⚠️ Tồn đọng và rủi ro mang sang

| Mục | Mức | Hành động |
|---|---|---|
| **Chưa có sách thật.** Mọi quy tắc khảo sát được kiểm trên sách mẫu do chính mình sinh ra | **Cao** | Khi có sách: chép vào `data/raw/`, chạy `dm survey`, cập nhật [book_profile.md](../../book_profile.md) theo checklist mục 9, chọn lại pilot, chạy `dm pilot check` |
| `judge` dùng cùng model với `qa` và `datagen` (thiên vị khi tự chấm) | Trung bình | Quyết định trước P5: đổi `judge` sang model khác hãng (1 dòng trong `models.yaml`) |
| Bản quyền sách và điều khoản teacher model khi huấn luyện thật | Trung bình | Trước P8 (problem.md mục 6.8) |
| Test suite chạy khoảng 42 giây (sinh sách mẫu nhiều lần) | Thấp | Theo dõi; nếu tăng mạnh thì dùng fixture cấp phiên |

## 5. Đề xuất bước tiếp theo

**P1: Trích xuất và làm sạch text** (plan.md mục P1). Đầu vào là sách mẫu và pilot trang 4–9. **Có đáp án** nên đo được bằng số:
- tỉ lệ header/footer bị bỏ đúng;
- tỉ lệ dòng được nối đúng đoạn;
- số lỗi OCR sửa đúng;
- và quan trọng nhất: **0 lần sửa sai số liệu**.

Bước đầu tiên là viết `docs/phases/P1/plan.md` để chủ dự án duyệt.
