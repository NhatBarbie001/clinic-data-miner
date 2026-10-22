# Báo cáo cấu trúc P2: cây chương → bệnh → mục

## 1. Tổng quan

- Lần chạy `p2_tree_20261022-100225-556_a6da` · **success** · 0.109s · git `ae011dd` · LLM: 0 lời gọi, $0.000000 · prompt dùng: không
- Cây: **2 chương · 3 bệnh · 19 mục · 3 mục con** · 85 block
- Cấp tiêu đề: quy tắc 22 · xác nhận/sửa bằng mục lục 5 · LLM 0
- Loại mục: từ điển 22 · khớp gần 0 · kế thừa 0 · LLM 0 · chưa rõ 0

| Bệnh | Trang PDF | Trang in | Mục / mục con | Block | Số từ |
|---|---|---|---|---|---|
| Viêm khớp dạng thấp | 4–5 | 1–2 | 9 | 32 | 406 |
| Thoái hóa khớp gối | 6–7 | 3–4 | 6 | 25 | 280 |
| Viêm loét dạ dày tá tràng | 8–9 | 5–6 | 7 | 26 | 285 |

## 2. Đối chiếu mục lục

Trang mục lục: PDF [3] · trang PDF = trang in +3

| Mục lục | Cấp | Tr.in (mục lục) | Nút trong cây | Trang khớp |
|---|---|---|---|---|
| Chương 1. Bệnh cơ xương khớp | chapter | 1 | ✓ Chương 1. Bệnh cơ xương khớp | ✓ PDF 4 |
| Viêm khớp dạng thấp | disease | 1 | ✓ Viêm khớp dạng thấp | ✓ PDF 4 |
| Thoái hóa khớp gối | disease | 3 | ✓ Thoái hóa khớp gối | ✓ PDF 6 |
| Chương 2. Bệnh tiêu hỏa | chapter | 5 | ✓ Chương 2. Bệnh tiêu hóa | ✓ PDF 8 |
| Viêm loét dạ dày tá tràng | disease | 5 | ✓ Viêm loét dạ dày tá tràng | ✓ PDF 8 |

Nút chương/bệnh trong cây nhưng **không có trong mục lục**: không có.

## 3. Ma trận bệnh × loại mục

| Bệnh | definition | cause | risk_factor | symptom | paraclinical | diagnosis | treatment | complication | prevention |
|---|---|---|---|---|---|---|---|---|---|
| Viêm khớp dạng thấp | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| Thoái hóa khớp gối | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | — | ✓ |
| Viêm loét dạ dày tá tràng | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | ✓ | ✓ |

- Loại mục **chỉ có ở một số bệnh** (P4 phải chấp nhận trường trống): `risk_factor`, `paraclinical`, `complication`
- Loại mục **không bệnh nào có**: `pathophysiology`, `differential_diagnosis`, `prognosis`

## 4. Cảnh báo cần người xem

✅ Không có cảnh báo: không nút rỗng, không cờ, không mục quá dài/ngắn, không ghi chú nào từ lần chạy.

## Chỉ tiêu (so với đáp án sách mẫu)

| Chỉ tiêu | Kết quả |
|---|---|
| G1 mục lục (số mục, tiêu đề, cấp, trang) | ✅ |
| G2 cấp tiêu đề | ✅ |
| G3 bệnh trong cây khớp mục lục + trang | ✅ |
| G4 nội dung đúng nút (≥ 99% dòng) | ✅ |
| G5 loại mục (≥ 95%, other < 5%) | ✅ |
| G6 bất biến cây | ✅ |
| G7 bộ câu hỏi chuẩn hợp lệ với cây | ✅ |

## 5. Cây

```
book01 · tr.in 1–6
├─ Chương 1. Bệnh cơ xương khớp · tr.in 1–4
│  ├─ Viêm khớp dạng thấp · tr.in 1–2
│  │  ├─ 1. Đại cương [definition] · 1 đoạn văn · tr.in 1
│  │  ├─ 2. Nguyên nhân [cause] · 1 đoạn văn · tr.in 1
│  │  │  └─ 2.1. Yếu tố nguy cơ [risk_factor] · 4 gạch đầu dòng · tr.in 1
│  │  ├─ 3. Triệu chứng [symptom] · (chỉ có mục con) · tr.in 1–2
│  │  │  ├─ 3.1. Lâm sàng [symptom] · 4 gạch đầu dòng · tr.in 1–2
│  │  │  └─ 3.2. Cận lâm sàng [paraclinical] · 3 gạch đầu dòng · tr.in 2
│  │  ├─ 4. Chẩn đoán [diagnosis] · 1 đoạn văn · tr.in 2
│  │  ├─ 5. Điều trị [treatment] · 5 gạch đầu dòng · tr.in 2
│  │  └─ 6. Phòng bệnh [prevention] · 3 gạch đầu dòng · tr.in 2
│  └─ Thoái hóa khớp gối · tr.in 3–4
│     ├─ 1. Đại cương [definition] · 1 đoạn văn · tr.in 3
│     ├─ 2. Nguyên nhân [cause] · 4 gạch đầu dòng · tr.in 3
│     ├─ 3. Triệu chung [symptom] · 5 gạch đầu dòng · tr.in 3
│     ├─ 4. Chẩn đoán [diagnosis] · 1 đoạn văn · tr.in 3
│     ├─ 5. Điều trị [treatment] · 5 gạch đầu dòng · tr.in 4
│     └─ 6. Phòng bệnh [prevention] · 2 gạch đầu dòng · tr.in 4
└─ Chương 2. Bệnh tiêu hóa · tr.in 5–6
   └─ Viêm loét dạ dày tá tràng · tr.in 5–6
      ├─ 1. Đại cương [definition] · 1 đoạn văn · tr.in 5
      ├─ 2. Nguyên nhân [cause] · 3 gạch đầu dòng · tr.in 5
      ├─ 3. Triệu chứng [symptom] · 3 gạch đầu dòng · tr.in 5
      ├─ 4. Biến chứng [complication] · 3 gạch đầu dòng · tr.in 5
      ├─ 5. Chẩn đoán [diagnosis] · 1 đoạn văn · tr.in 5
      ├─ 6. Điều trị [treatment] · 3 gạch đầu dòng, 1 chú thích, 1 bảng · tr.in 6
      └─ 7. Phòng bệnh [prevention] · 2 gạch đầu dòng · tr.in 6
```
