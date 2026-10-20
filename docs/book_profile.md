# Hồ sơ sách: `book01.pdf`

> Nguồn: `dm survey` (2026-10-20) trên **sách mẫu tổng hợp** (`dm dev make-sample-book`, seed 7), đối chiếu với đáp án.
> Số liệu đầy đủ: [samples/P0.5/survey_report.md](../samples/P0.5/survey_report.md) · Đối chiếu: [survey_vs_truth.txt](../samples/P0.5/survey_vs_truth.txt)
>
> ⚠️ **Đây là sách mẫu, không phải sách thật.** Các quy tắc dưới đây là đầu vào cho thiết kế P1/P2. Mục 9 liệt kê những gì **phải kiểm lại** khi có sách thật: chép sách vào `data/raw/`, chạy `dm survey`, rồi cập nhật file này.

## 1. Tổng quan

| Mục | Giá trị |
|---|---|
| Số trang | 9 (khổ A5, 420×595 pt) |
| Cấu trúc trang | Trang 1 bìa · Trang 2 **trắng** (không có lớp text) · Trang 3 mục lục · Trang 4–9 nội dung |
| Lớp dữ liệu | **Mỗi trang = ảnh scan + lớp text OCR ẩn**. Máy chỉ đọc được lớp text. |
| Font lớp OCR | 1 font duy nhất (`Noto Sans Regular`) |
| **In đậm** | **0%** ký tự. Lớp OCR **không giữ** thông tin in đậm, dù bản in có. |
| Cỡ chữ thân bài | **10.4 pt** (thực tế 10.5; OCR ước lượng cỡ chữ có nhiễu ±6%) |
| Nội dung | 2 chương, 3 bệnh, 1 bảng |

## 2. Nhận diện tiêu đề (cho P2)

Không dùng được "in đậm" (mục 1). Chỉ còn **cỡ chữ, viết hoa, mẫu đánh số**.

| Cấp | Quy tắc nhận diện | Ví dụ | Cỡ chữ (OCR) |
|---|---|---|---|
| **Chương** | Bắt đầu bằng `CHƯƠNG <số>.`, viết hoa; luôn ở **đầu trang mới**; trang đầu chương **không có header** | `CHƯƠNG 1. BỆNH CƠ XƯƠNG KHỚP` | ~14–15 (≥ thân bài + 3) |
| **Bệnh** | **Viết hoa toàn bộ**, **không đánh số**, cỡ chữ ≥ thân bài + 2 | `VIÊM KHỚP DẠNG THẤP` | ~13–14 |
| **Mục** | `<n>. ` + **VIẾT HOA**; đánh số lại từ 1 cho mỗi bệnh | `3. TRIỆU CHỨNG` | ~11–12 (có khi chỉ hơn thân bài 0.3pt) |
| **Mục con** | `<n>.<m>. ` + chữ thường | `3.1. Lâm sàng` | **= thân bài**. Chỉ nhận ra được nhờ số thứ tự |

**Hệ quả cho P2:**
- Đánh số và viết hoa là **tín hiệu chính**. Cỡ chữ chỉ là tín hiệu phụ, và ngưỡng phải có dung sai (≥ +0.75pt).
- Ranh giới **bệnh** = dòng viết hoa, không đánh số, nằm giữa hai lần mục `1. ĐẠI CƯƠNG`. Số mục reset về 1 cũng là một dấu hiệu bệnh mới.
- Tiêu đề **có thể bị lỗi OCR** (`2. NGUYEN NHÂN`, `1. DAI CƯƠNG`). Khi so với từ điển tên mục phải so **không dấu**.
- Bìa (trang 1) cũng có dòng viết hoa, chữ lớn. Phải loại theo trang (trước mục lục) hoặc theo nội dung.

**Kết quả khảo sát:** recall tiêu đề **100%** (28/28). 3 ứng viên thừa đều nằm trên bìa.

## 3. Danh sách mục chuẩn của một bệnh (cho P2.4 `section_map`)

| Tiêu đề trong sách | `section_type` | Xuất hiện |
|---|---|---|
| ĐẠI CƯƠNG | `definition` | 3/3 bệnh |
| NGUYÊN NHÂN | `cause` | 3/3 |
| Yếu tố nguy cơ (mục con) | `risk_factor` | 1/3 |
| TRIỆU CHỨNG | `symptom` | 3/3 |
| Lâm sàng (mục con) | `symptom` | 1/3 |
| Cận lâm sàng (mục con) | `paraclinical` | 1/3 |
| BIẾN CHỨNG | `complication` | 1/3 |
| CHẨN ĐOÁN | `diagnosis` | 3/3 |
| ĐIỀU TRỊ | `treatment` | 3/3 |
| PHÒNG BỆNH | `prevention` | 3/3 |

Thứ tự mục cố định, nhưng **số thứ tự thay đổi** khi có mục thêm vào (ví dụ "BIẾN CHỨNG" là mục 4, đẩy "CHẨN ĐOÁN" xuống mục 5). Vì vậy **ánh xạ theo tên mục, không theo số**.

## 4. Header, footer và số trang (cho P1)

| Loại | Vị trí | Dạng | Quy tắc |
|---|---|---|---|
| Header chạy (trang in chẵn) | trên cùng, căn trái | `Bệnh học nội khoa (sách mẫu)` | lặp lại qua nhiều trang |
| Header chạy (trang in lẻ) | trên cùng, căn phải | `Chương 1. Bệnh cơ xương khớp` | tên chương hiện tại. **Có thể chỉ xuất hiện 1 lần** (chương ngắn) |
| Footer | dưới cùng, giữa | `– 3 –` | số trang in |
| Trang đầu chương | | **không có header** | chỉ có footer |

- **Vùng lề:** header nằm trong **9% đầu trang**, footer trong **9% cuối trang**. Thân bài không bao giờ lấn vào hai vùng này.
- **Nhận diện:** (a) lặp lại ≥ 2 trang khi coi mọi chữ số là như nhau, **hoặc** (b) chỉ gồm số trang, **hoặc** (c) chữ nhỏ hơn thân bài nằm trong vùng lề (header chương chỉ xuất hiện một lần).
- **Số trang in ≠ số trang PDF:** `trang PDF = trang in + 3`. Bìa, trang trắng và mục lục không đánh số. Mục lục dùng **số trang in**.

**Kết quả khảo sát:** header/footer recall **100%**, precision **100%** (10/10); ánh xạ số trang in đúng 6/6.

## 5. Mục lục

- Trang 3, tiêu đề `MỤC LỤC`.
- Mỗi dòng: `<tiêu đề> ....... <số trang in>`, dòng chấm dẫn ≥ 4 dấu chấm.
- Hai cấp: chương (thụt lề 0) và bệnh (thụt lề ~14pt).
- Dùng để **đối chiếu số bệnh** ở P2 (gate P2: khớp 100%).
- Mục lục cũng có thể bị lỗi OCR (`Bệnh tiêu hỏa`), nên khi so tiêu đề phải so mềm.

## 6. Thân bài

- **Đoạn văn:** dòng tự xuống giữa câu, cần nối lại (P1). Đoạn kết thúc bằng dấu chấm.
- **Gạch đầu dòng:** bắt đầu bằng `- `. Dòng tiếp theo **thụt vào ~6pt** so với dấu `-` và **không có** dấu `-`. Đây là cách phân biệt "dòng tiếp" với "gạch đầu dòng mới".
- Thuật ngữ Latin/Anh xen lẫn: `Helicobacter pylori`, `HLA-DR4`, `anti-CCP`, `DMARD`, `ACR/EULAR 2010`.
- **Liều thuốc:** `500 mg`, `7,5-15 mg mỗi tuần`, `1 g`, `3 g mỗi ngày`. Dấu phẩy thập phân kiểu Việt.

## 7. Bảng

- Có chú thích `Bảng <chương>.<n>. <tên>` căn giữa, phía trên bảng.
- **Mỗi ô là một dòng text riêng.** Các ô cùng hàng có cùng toạ độ y; các cột thẳng hàng theo x (4 cột ở x ≈ 52, 169, 253, 318).
- Hàng đầu là tiêu đề cột. Kẻ ngang chỉ có trong lớp ảnh, **không có trong lớp text**.
- **Nhận diện:** ≥ 3 dòng ngắn cùng toạ độ y trên một trang, ngay sau dòng `Bảng ...`.

## 8. Lỗi OCR

| Loại | Ví dụ thật trong sách | Tần suất | Khảo sát phát hiện? | Xử lý ở P1 |
|---|---|---|---|---|
| **Mất dấu** | `là`→`la`, `truyền`→`truyen`, `NGUYÊN`→`NGUYEN` | 56% số lỗi | ✗ (tạo từ hợp lệ) | LLM + ngữ cảnh |
| **Sai dấu** | `hóa`→`hỏa`, `và`→`vá`, `đặc`→`đắc` | 16% | ✗ | LLM + ngữ cảnh |
| **Nhầm ký tự** | `viêm`→`viêrn`, `thuốc`→`tbuốc`, `là`→`1à`, `hạn`→`bạn` | 16% | ✓ 71% (trừ khi tạo ra từ có nghĩa) | quy tắc + LLM |
| **Dính từ** | `phản ứng`→`phảnứng`; ở seed khác: `ngày (Bảng`→`ngày(Bảng`; hai từ **không dấu** dính nhau không phát hiện được: `X quang`→`Xquang`, `acid folic`→`acidfolic` | 2% | ✓ 100% số có thể phát hiện | quy tắc tách âm tiết |
| ⚠️ **Nhầm số trong liều** | `500 mg`→`5OO mg`, `1 g`→`l g` | 2 chỗ | ✓ 100% | **guard bắt buộc**: số liệu sau khi sửa phải khớp mẫu số hợp lệ; nghi ngờ thì **gắn cờ cho người duyệt**, không tự đoán |
| **Mã hóa NFD** | cả dòng ở dạng Unicode tổ hợp | 2 dòng | ✓ 100% | chuẩn hóa NFC (quy tắc, trước mọi bước) |

- Tổng **43 lỗi trên khoảng 1.130 từ (~3.8%)**.
- **72% số lỗi (mất dấu, sai dấu) không thể phát hiện chỉ bằng quy tắc**, nên P1 cần LLM hoặc mô hình ngôn ngữ.
- Header và footer không có lỗi.

## 9. ⚠️ Phải kiểm lại khi có sách thật

| Giả định từ sách mẫu | Rủi ro nếu sai | Cách kiểm |
|---|---|---|
| Lớp OCR mất hoàn toàn in đậm | Nếu sách thật giữ được, nên dùng thêm tín hiệu in đậm | `bold_char_ratio` trong `stats.json` |
| Một cột chữ | Sách 2 cột làm sai thứ tự đọc | Xem ảnh `pages/*.png`; phân bố toạ độ x |
| Mỗi dòng text là một dòng in | Có OCR gộp hoặc tách dòng khác | Đối chiếu ảnh với `lines.jsonl` |
| Ô bảng tách thành từng dòng | OCR khác có thể nối cả hàng thành một chuỗi | `pages/` trang có bảng |
| Đánh số mục `n.` / `n.m.` | Sách thật có thể dùng `I.`, `A.`, `a)` | `heading_candidates.json`; thêm mẫu vào cấu hình |
| Không có chú thích chân trang, hình ảnh | Chú thích có thể bị nhận nhầm là footer | Kiểm vùng lề |
| Mật độ lỗi khoảng 4% | Có thể cao hơn nhiều, nên tăng chi phí P1 | `ocr_signals.json` |
| Tiêu đề không xuống dòng | Tiêu đề dài 2 dòng làm tách sai | Ứng viên tiêu đề kết thúc giữa câu |
