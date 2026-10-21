# Tình huống ngoài sách mẫu (block tự dựng, chạy thật bằng `classify_headings`, KHÔNG LLM)

Mục lục giả lập: `Chương 3. Bệnh thận` (PDF 10), `Sỏi thận` (PDF 10), `Gout` (PDF 12).

| Trang | Tiêu đề | Cỡ | → Cấp | Tin cậy | Nguồn | Cờ | Lý do |
|---|---|---|---|---|---|---|---|
| 10 | `CHUONG 3. BENH THAN` | 14.0 | **chapter** | high | toc |  | mẫu 'chuong 3' (so không dấu) · khớp mục lục: 'Chương 3. Bệnh thận' (tr.in 7, trùng khóa) |
| 10 | `SỎI THẬN` | 13.5 | **disease** | high | toc |  | IN HOA, không đánh số, cỡ 13.5 ≥ thân bài 10.5 + 1.5 · khớp mục lục: 'Sỏi thận' (tr.in 7, trùng khóa) |
| 10 | `1. ĐẠI CƯƠNG` | 12.0 | **section** | high | rules |  | đánh số mục '1' + IN HOA |
| 10 | `2. NGUYÊN NHÂN` | 12.0 | **section** | high | rules |  | đánh số mục '2' + IN HOA |
| 10 | `LƯU Ý` | 10.6 | **other** | low | rules |  | IN HOA, không đánh số, cỡ 10.6 < ngưỡng bệnh 12.0 |
| 11 | `4. ĐIỀU TRỊ` | 12.0 | **section** | high | rules | numbering_gap | đánh số mục '4' + IN HOA |
| 11 | `4.2. Ngoại khoa` | 10.6 | **subsection** | high | rules | numbering_gap | đánh số mục con '4.2' |
| 12 | `HEN PHẾ QUẢN` | 13.0 | **disease** | low | rules | missing_from_toc | IN HOA, không đánh số, cỡ 13.0 ≥ thân bài 10.5 + 1.5 · không khớp mục nào trong mục lục |
| 12 | `1. ĐẠI CƯƠNG` | 12.0 | **section** | high | rules |  | đánh số mục '1' + IN HOA |

**Cảnh báo:**

- Mục lục có 'Gout' nhưng không tìm thấy tiêu đề nào khớp trong thân sách.
- 2 tiêu đề tin cậy thấp chưa được LLM xem (llm_fallback tắt hoặc --no-llm).
- '4. ĐIỀU TRỊ' (trang PDF 11): số '4', mong đợi '3' - có thể sót tiêu đề hoặc OCR đọc nhầm số.
- '4.2. Ngoại khoa' (trang PDF 11): số '4.2', mong đợi '4.1' - có thể sót tiêu đề hoặc OCR đọc nhầm số.

Ghi chú: chạy thật (có LLM), 2 tiêu đề tin cậy `low` (`LƯU Ý`, `HEN PHẾ QUẢN`) sẽ được hỏi LLM (tác vụ `classify`); ở đây tắt LLM để minh họa lớp 1-2. Đường LLM được kiểm bằng LLM giả lập trong test #8.
