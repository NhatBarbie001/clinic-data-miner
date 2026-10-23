# Bộ câu hỏi chuẩn (golden set)

Thước đo dùng xuyên suốt dự án (plan.md mục 5.3, docs/phases/P2/P2.5_plan.md):

| Phase | Dùng để |
|---|---|
| P3 tìm kiếm | Câu hỏi → top-k đoạn: có trúng nút nguồn (`sources[].node_id`) không |
| P5 hỏi đáp | Câu trả lời có đủ `answer_points`, trích dẫn đúng nút; câu `refusal` phải trả lời "sách không đề cập" |
| P7 dữ liệu huấn luyện | Loại mọi câu sinh ra gần trùng câu trong golden set (chống rò rỉ) |

## Quy tắc

1. **CÁCH LY: golden set KHÔNG BAO GIỜ được dùng để huấn luyện** - kể cả làm ví dụ few-shot trong
   prompt sinh dữ liệu. P7 có bước kiểm tra rò rỉ (so gần trùng với mọi file `golden_qa_v*.jsonl`).
2. **Version, không sửa câu cũ.** `golden_qa_v1.jsonl` đã khóa: chỉ được THÊM câu (bản mới) hoặc tạo
   `golden_qa_v2.jsonl`. `dm p2 golden` từ chối ghi đè v1 nếu nội dung khác.
3. **Tự kiểm được.** Mỗi câu có `check` (luật tính lại đáp án từ cây). `dm p2 golden --check` (G7):
   nút nguồn tồn tại, path khớp, trích dẫn có thật trong nút, số liệu trùng đúng, câu từ chối không
   có từ khóa nào trong sách, không có câu gần trùng.
4. **Người tạo / người duyệt.** v1 sinh tự động từ đáp án SÁCH MẪU (`created_by: "auto (sách mẫu)"`,
   `reviewed_by: "auto-check (sách mẫu)"`). **Với sách thật, câu hỏi phải do người có chuyên môn y
   khoa viết hoặc duyệt** - câu sinh theo mẫu dễ hơn câu hỏi thật của người dùng.
5. **Gắn với cây.** Nguồn trỏ tới `node_id` (= hash của path). Dựng lại cây mà tiêu đề đổi chữ
   (vd. sửa lỗi OCR) → ID đổi → `--check` báo "nút nguồn không tồn tại": cần cập nhật bằng version
   mới, không sửa im lặng.

## File

| File | Nội dung |
|---|---|
| `book01/golden_qa_v1.jsonl` | Sách mẫu: 30 câu: 20 cụ thể (gồm 2 câu số liệu/bảng), 5 liệt kê, 5 từ chối - pilot |

Mỗi sách một thư mục `eval/<book_id>/` (cấu hình `paths.eval_dir: eval/{book_id}`).
