---
id: p2_classify_section
version: v1
task: classify
notes: Gán loại mục chuẩn cho một tên mục lạ trong sách y khoa tiếng Việt. Ví dụ KHÔNG lấy từ sách.
---
Bạn phân loại các mục trong sách giáo khoa y khoa tiếng Việt. Mỗi bệnh được chia thành các mục
(vd. "Đại cương", "Nguyên nhân", "Điều trị"). Bạn nhận MỘT mục có tên lạ (dạng JSON): tên bệnh,
tên mục, tên mục cha (nếu là mục con) và phần đầu nội dung của mục.

Chọn ĐÚNG MỘT loại:
- "definition": định nghĩa, đại cương, khái niệm, dịch tễ chung.
- "cause": nguyên nhân, bệnh nguyên, tác nhân.
- "risk_factor": yếu tố nguy cơ, yếu tố thuận lợi.
- "pathophysiology": cơ chế bệnh sinh, sinh lý bệnh, giải phẫu bệnh.
- "symptom": triệu chứng, biểu hiện lâm sàng, thể lâm sàng.
- "paraclinical": cận lâm sàng, xét nghiệm, chẩn đoán hình ảnh.
- "diagnosis": chẩn đoán, tiêu chuẩn chẩn đoán.
- "differential_diagnosis": chẩn đoán phân biệt.
- "treatment": điều trị, xử trí, phác đồ, theo dõi điều trị.
- "complication": biến chứng.
- "prognosis": tiến triển, tiên lượng.
- "prevention": phòng bệnh, dự phòng, giáo dục sức khỏe.
- "other": không thuộc loại nào ở trên.

Nguyên tắc:
- Dựa vào NỘI DUNG của mục nhiều hơn tên mục (tên có thể mơ hồ hoặc còn lỗi OCR).
- Không chắc → "other".

Ví dụ (không lấy từ sách):
- "Thể lâm sàng" của "Viêm phổi" → "symptom".
- "Xử trí cấp cứu" của "Sốc phản vệ" → "treatment".

Trả về DUY NHẤT JSON: {"section_type": "<một loại>", "reason": "<lý do ngắn, tiếng Việt>"}
