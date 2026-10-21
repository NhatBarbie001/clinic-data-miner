# Cấp tiêu đề - pilot sách mẫu (seed 7)

Đầu vào: 27 block `heading` của P1 (`data/p1_clean/blocks.jsonl`) + `toc.json` (P2.1).

| # | Trang | Tiêu đề | Cỡ | IN HOA | Số | → Cấp | Tin cậy | Nguồn | Lý do |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | `CHƯƠNG 1. BỆNH CƠ XƯƠNG KHỚP` | 14.3 | ✓ | CHƯƠNG 1 | **chapter** | high | toc | mẫu 'CHƯƠNG 1' · khớp mục lục: 'Chương 1. Bệnh cơ xương khớp' (tr.in 1, trùng khóa) |
| 2 | 4 | `VIÊM KHỚP DẠNG THẤP` | 13.4 | ✓ |  | **disease** | high | toc | IN HOA, không đánh số, cỡ 13.4 ≥ thân bài 10.5 + 1.5 · khớp mục lục: 'Viêm khớp dạng thấp' (tr.in 1, trùng khóa) |
| 3 | 4 | `1. ĐẠI CƯƠNG` | 12.0 | ✓ | 1 | **section** | high | rules | đánh số mục '1' + IN HOA |
| 4 | 4 | `2. NGUYÊN NHÂN` | 11.4 | ✓ | 2 | **section** | high | rules | đánh số mục '2' + IN HOA |
| 5 | 4 | `2.1. Yếu tố nguy cơ` | 10.2 |  | 2.1 | **subsection** | high | rules | đánh số mục con '2.1' |
| 6 | 4 | `3. TRIỆU CHỨNG` | 11.6 | ✓ | 3 | **section** | high | rules | đánh số mục '3' + IN HOA |
| 7 | 4 | `3.1. Lâm sàng` | 10.7 |  | 3.1 | **subsection** | high | rules | đánh số mục con '3.1' |
| 8 | 5 | `3.2. Cận lâm sàng` | 10.4 |  | 3.2 | **subsection** | high | rules | đánh số mục con '3.2' |
| 9 | 5 | `4. CHẨN ĐOÁN` | 11.5 | ✓ | 4 | **section** | high | rules | đánh số mục '4' + IN HOA |
| 10 | 5 | `5. ĐIỀU TRỊ` | 11.0 | ✓ | 5 | **section** | high | rules | đánh số mục '5' + IN HOA |
| 11 | 5 | `6. PHÒNG BỆNH` | 12.0 | ✓ | 6 | **section** | high | rules | đánh số mục '6' + IN HOA |
| 12 | 6 | `THOÁI HÓA KHỚP GỐI` | 14.1 | ✓ |  | **disease** | high | toc | IN HOA, không đánh số, cỡ 14.1 ≥ thân bài 10.5 + 1.5 · khớp mục lục: 'Thoái hóa khớp gối' (tr.in 3, trùng khóa) |
| 13 | 6 | `1. ĐẠI CƯƠNG` | 12.1 | ✓ | 1 | **section** | high | rules | đánh số mục '1' + IN HOA |
| 14 | 6 | `2. NGUYÊN NHÂN` | 11.7 | ✓ | 2 | **section** | high | rules | đánh số mục '2' + IN HOA |
| 15 | 6 | `3. TRIỆU CHUNG` | 11.7 | ✓ | 3 | **section** | high | rules | đánh số mục '3' + IN HOA |
| 16 | 6 | `4. CHẨN ĐOÁN` | 11.2 | ✓ | 4 | **section** | high | rules | đánh số mục '4' + IN HOA |
| 17 | 7 | `5. ĐIỀU TRỊ` | 11.9 | ✓ | 5 | **section** | high | rules | đánh số mục '5' + IN HOA |
| 18 | 7 | `6. PHÒNG BỆNH` | 11.1 | ✓ | 6 | **section** | high | rules | đánh số mục '6' + IN HOA |
| 19 | 8 | `CHƯƠNG 2. BỆNH TIÊU HÓA` | 15.2 | ✓ | CHƯƠNG 2 | **chapter** | high | toc | mẫu 'CHƯƠNG 2' · khớp mục lục: 'Chương 2. Bệnh tiêu hỏa' (tr.in 5, trùng khóa) |
| 20 | 8 | `VIÊM LOÉT DẠ DÀY TÁ TRÀNG` | 13.1 | ✓ |  | **disease** | high | toc | IN HOA, không đánh số, cỡ 13.1 ≥ thân bài 10.5 + 1.5 · khớp mục lục: 'Viêm loét dạ dày tá tràng' (tr.in 5, trùng khóa) |
| 21 | 8 | `1. ĐẠI CƯƠNG` | 10.8 | ✓ | 1 | **section** | high | rules | đánh số mục '1' + IN HOA |
| 22 | 8 | `2. NGUYÊN NHÂN` | 12.1 | ✓ | 2 | **section** | high | rules | đánh số mục '2' + IN HOA |
| 23 | 8 | `3. TRIỆU CHỨNG` | 12.1 | ✓ | 3 | **section** | high | rules | đánh số mục '3' + IN HOA |
| 24 | 8 | `4. BIẾN CHỨNG` | 11.4 | ✓ | 4 | **section** | high | rules | đánh số mục '4' + IN HOA |
| 25 | 8 | `5. CHẨN ĐOÁN` | 10.9 | ✓ | 5 | **section** | high | rules | đánh số mục '5' + IN HOA |
| 26 | 9 | `6. ĐIỀU TRỊ` | 10.8 | ✓ | 6 | **section** | high | rules | đánh số mục '6' + IN HOA |
| 27 | 9 | `7. PHÒNG BỆNH` | 12.1 | ✓ | 7 | **section** | high | rules | đánh số mục '7' + IN HOA |
