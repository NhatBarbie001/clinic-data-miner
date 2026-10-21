# Tình huống ngoài sách mẫu (cây tự dựng, chạy thật `map_sections`, LLM GIẢ LẬP)

Trên sách mẫu cả 22 tên mục đều trúng từ điển; các đường dưới đây chỉ thấy được ở đây.

| Tên mục | Chuẩn hóa | Tra từ điển | → Loại | Nguồn | Cờ |
|---|---|---|---|---|---|
| `2. NGUYÊN NHÂU` | `nguyen nhau` | gần 'nguyen nhan' (0.909) | **cause** | map_fuzzy | section_type_fuzzy |
| `3. TRIỆU CHỨNG` | `trieu chung` | trùng khóa | **symptom** | map |  |
| `3.3. Đặc điểm` | `dac diem` | không khớp | **symptom** | inherited |  |
| `5. ĐIỀU KHIỂN` | `dieu khien` | không khớp | **prevention** | llm | section_type_from_llm |
| `7. THEO DÕI SAU ĐIỀU TRỊ` | `theo doi sau dieu tri` | không khớp | **prevention** | llm | section_type_from_llm |

Ghi chú:
- `5. ĐIỀU KHIỂN` (`dieu khien`) chỉ giống `dieu tri` 0.667 → KHÔNG khớp gần (ngưỡng 0.9 đủ chặt), nên được hỏi LLM; LLM giả lập ở đây trả cùng một nhãn cho mọi câu hỏi - chỉ minh họa đường đi, không phải nhãn thật.
- Đề xuất cần duyệt (khớp gần + LLM) → [section_proposals_demo.csv](section_proposals_demo.csv) → người duyệt điền `decision` → `dm p2 sections import` ghi thêm vào từ điển.

Lời gọi LLM (giả lập): 2; đề xuất: 3.

```
demo · PDF 4–4
└─ Đái tháo đường · PDF 4–4
   ├─ 2. Nguyên nhâu [cause] · 1 đoạn văn · PDF 4–4 ⚑ section_type_fuzzy
   ├─ 3. Triệu chứng [symptom] · (chỉ có mục con) · PDF 4–4
   │  └─ 3.3. Đặc điểm [symptom] · 1 đoạn văn · PDF 4–4
   ├─ 5. Điều khiển [prevention] · 1 đoạn văn · PDF 4–4 ⚑ section_type_from_llm
   └─ 7. Theo dõi sau điều trị [prevention] · 1 đoạn văn · PDF 4–4 ⚑ section_type_from_llm
```
