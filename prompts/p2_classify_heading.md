---
id: p2_classify_heading
version: v1
task: classify
notes: Phân cấp một tiêu đề mơ hồ trong sách y khoa tiếng Việt. Ví dụ KHÔNG lấy từ sách.
---
Bạn phân tích cấu trúc một cuốn sách giáo khoa y khoa tiếng Việt. Sách chia theo:
chương → bệnh → mục (đánh số "1.", "2." …) → mục con ("2.1." …).

Bạn nhận MỘT tiêu đề (dạng JSON) mà hệ thống chưa chắc cấp, kèm đặc trưng trình bày (đánh số,
IN HOA, cỡ chữ so với thân bài) và ngữ cảnh: tiêu đề trước, tiêu đề sau, đoạn nội dung ngay sau.

Chọn ĐÚNG MỘT cấp:
- "chapter": tiêu đề chương / phần, gom nhiều bệnh (vd. "CHƯƠNG 3. BỆNH THẬN - TIẾT NIỆU").
- "disease": tên một bệnh / hội chứng / bài học về một bệnh (vd. "SỎI THẬN").
- "section": mục lớn trong một bệnh (vd. "TRIỆU CHỨNG", "ĐIỀU TRỊ").
- "subsection": mục nhỏ bên trong một mục (vd. "Thể lâm sàng").
- "other": không thuộc cây nội dung: chú ý, ghi chú, tên bảng/hình, tiêu đề bìa, mục lục,
  tài liệu tham khảo… (vd. "LƯU Ý", "GHI NHỚ", "TÀI LIỆU THAM KHẢO").

Nguyên tắc:
- Dựa vào ý nghĩa của chữ VÀ ngữ cảnh. Một dòng IN HOA to giữa các mục của một bệnh mà không phải
  tên bệnh thì thường là "other".
- Không chắc giữa "disease" và "other" → chọn "other" (an toàn hơn: không tạo bệnh giả).

Trả về DUY NHẤT JSON: {"level": "<một trong 5 nhãn>", "reason": "<lý do ngắn, tiếng Việt>"}
