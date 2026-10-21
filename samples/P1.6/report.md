# Báo cáo P1: trích xuất và làm sạch text

## 1. Tổng quan

- Lần chạy: `p1_clean_20261021-121821-660_8837` · trạng thái **success** · 0.543s · git `0d0e404`
- Prompt: p1_fix_ocr@v1 · chi phí LLM: $0.000000 (0 lời gọi)
- phạm vi: trang PDF 4-9 (pilot)

| chỉ số | giá trị |
|---|---|
| pages | 6 |
| lines | 147 |
| furniture_removed | 10 |
| content_lines | 137 |
| blocks | 85 |
| blocks_heading | 27 |
| blocks_paragraph | 7 |
| blocks_list_item | 49 |
| blocks_caption | 1 |
| blocks_table | 1 |
| fixes_accepted | 36 |
| fixes_rejected | 2 |
| reviews_applied | 2 |
| pending_review | 0 |

## 2. Chỉ tiêu (so với đáp án)

| chỉ tiêu | kết quả | chi tiết |
|---|---|---|
| G1 header/footer bỏ đủ, không bỏ nhầm | ✅ | removed=10 |
| G2 số trang in | ✅ | pages=6 |
| G3 block đúng tập dòng (≥ 97%), không gộp nhầm | ✅ | recall=1.0 |
| G4 bảng hàng × cột | ✅ | found_tables=1 |
| G5 tỉ lệ từ sai ≤ 1% | ✅ | after=0.003 |
| G6 lỗi đã cài được sửa ≥ 80% | ✅ | rate=0.9211 |
| G7 từ đúng bị sửa sai ≤ 0.3% | ✅ | rate=0.0, tokens=0 |
| G8 số liệu không đổi nếu chưa qua duyệt | ✅ |  |
| G9 Unicode NFC | ✅ |  |

## 3. Trước / sau theo trang

Chỉ liệt kê block có thay đổi; **in đậm** = token đã đổi (LLM hoặc người duyệt).

### Trang PDF 4 (trang in 1)

- *paragraph*: Viêm khớp dạng thấp **là** bệnh lý tự miễn mạn tính, đặc trưng bởi tình trạng **viêm** màng hoạt dịch ở nhiều khớp, có tính chất đối xứng. Bệnh gặp chủ yếu ở nữ giới, tuổi trung niên từ 30 đến 50. Nếu không được điều trị đúng, bệnh tiến triển gây hủy hoại sụn khớp, biến dạng khớp và tàn phế.
- *heading*: 2. **NGUYÊN** NHÂN
- *paragraph*: Nguyên nhân chính xác của bệnh chưa được biết rõ. Bệnh được cho **là** kết quả của sự tương tác giữa yếu tố di truyền và yếu tố môi trường.
- *list_item*: Yếu tố di **truyền:** người mang kháng nguyên HLA-DR4 có nguy cơ mắc bệnh cao hơn.
- *list_item*: Hút **thuốc** lá là yếu tố môi trường quan trọng nhất.
- *list_item*: Viêm nhiều khớp nhỏ ở bàn tay như khớp cổ tay, khớp bàn ngón và **khớp** ngón gần, có tính chất đối xứng hai bên.

### Trang PDF 5 (trang in 2)

- *list_item*: Toàn thân: mệt mỏi, sốt nhẹ, gầy sút cân; có thể có hạt thấp **dưới** da.
- *list_item*: Tốc độ máu lắng **và** protein phản ứng C (CRP) tăng.
- *list_item*: Thuốc chống thấp khớp làm thay đổi bệnh (DMARD): methotrexat 7,5-15 mg **mỗi** tuần, kết hợp acid folic.
- *list_item*: Thuốc sinh học được chỉ định khi đáp ứng kém với DMARD kinh **diễn.**
- *list_item*: Phục hồi chức năng, vật lý trị liệu, tập **vận** động khớp.
- *list_item*: Phát hiện sớm, điều trị sớm để **hạn** chế biến dạng khớp.

### Trang PDF 6 (trang in 3)

- *heading*: 1. **ĐẠI** CƯƠNG
- *paragraph*: Thoái hóa khớp gối là bệnh lý mạn tính của khớp, đặc trưng bởi tổn thương sụn khớp, kèm theo **phản** **ứng** của xương dưới sụn và màng hoạt dịch. Bệnh thường gặp ở người trên 50 tuổi và là nguyên nhân hàng đầu gây đau khớp gối ở người cao tuổi.
- *list_item*: Béo phì làm tăng tải **trọng** lên khớp gối.
- *list_item*: Nghề nghiệp phải đứng **lâu,** mang vác nặng.
- *list_item*: **Cứng** khớp buổi sáng dưới 30 phút.
- *list_item*: Hạn chế vận động, có thể **có** tràn dịch khớp gối.
- *list_item*: X quang: hẹp khe khớp, **đặc** xương dưới sụn, gai xương ở rìa khớp.
- *paragraph*: Chẩn đoán theo tiêu chuẩn ACR 1991: đau khớp gối **kèm** gai xương trên X quang và có ít nhất một trong các yếu tố: tuổi trên 50, cứng khớp buổi **sáng** dưới 30 phút, có tiếng lục khục khi cử **động.**

### Trang PDF 7 (trang in 4)

- *list_item*: Giảm **cân,** tập luyện tăng sức mạnh cơ đùi.
- *list_item*: Paracetamol **500** mg mỗi lần, không quá 3 g mỗi ngày.
- *list_item*: Thuốc chống viêm không steroid dạng bôi hoặc uống trong **đợt** đau.

### Trang PDF 8 (trang in 5)

- *paragraph*: Viêm loét dạ dày tá tràng là tình trạng tổn thương niêm mạc dạ dày **hoặc** tá tràng, có thể lan sâu tới lớp cơ niêm. Bệnh có tính chất mạn tính, hay **tái** phát.
- *heading*: 4. **BIẾN** CHỨNG
- *list_item*: Xuất huyết **tiêu** hóa: nôn ra máu, đi ngoài phân đen.
- *paragraph*: Nội soi dạ dày tá tràng là phương pháp chẩn đoán xác định. Xét nghiệm tìm Helicobacter pylori bằng test urease nhanh khi nội soi **hoặc** test hơi thở.

### Trang PDF 9 (trang in 6)

- *heading*: 6. ĐIỀU **TRỊ**
- *list_item*: Thuốc ức chế bơm proton: omeprazol 20 mg uống 2 lần mỗi **ngày.**
- *bảng*: **Thuốc** | Liều mỗi lần | Số lần/ngày | Thời gian
- *bảng*: Omeprazol | 20 mg | 2 | 14 **ngày**
- *bảng*: Amoxicilin | **1** g | 2 | 14 ngày
- *list_item*: Ăn uống điều độ, đúng giờ; hạn chế rượu bia, **không** hút thuốc.
- *list_item*: Không tự ý dùng thuốc chống viêm không steroid **kéo** dài.

Tổng: 32/85 block có thay đổi.

## 4. Mục chờ duyệt (0)

Không còn mục chờ duyệt (6 quyết định đã áp).
