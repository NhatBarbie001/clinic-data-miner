# Sách mẫu: văn bản sạch ↔ lớp OCR

Mỗi dòng có lỗi OCR đã cài được liệt kê; dòng ⚠️ là lỗi số liệu (nguy hiểm nhất).
Header/footer không bị cài lỗi (để P1 nhận ra và bỏ được). Trang 4 in đủ mọi dòng;
các trang khác chỉ in dòng có lỗi.

## Trang PDF 1 (không đánh số)
_(không có lỗi OCR trên trang này)_

## Trang PDF 2 (không đánh số)
_(trang trắng - không có lớp text)_

## Trang PDF 3 (không đánh số)

| vai trò | văn bản sạch | lớp OCR | lỗi đã cài |
|---|---|---|---|
| toc | Chương 2. Bệnh tiêu hóa ............................................................. 5 | Chương 2. Bệnh tiêu hỏa ............................................................. 5 | wrong_tone: `hóa` → `hỏa` |

## Trang PDF 4 (trang in 1)

| vai trò | văn bản sạch | lớp OCR | lỗi đã cài |
|---|---|---|---|
| heading | CHƯƠNG 1. BỆNH CƠ XƯƠNG KHỚP | CHƯƠNG 1. BỆNH CƠ XƯƠNG KHỚP |  |
| heading | VIÊM KHỚP DẠNG THẤP | VIÊM KHỚP DẠNG THẤP |  |
| heading | 1. ĐẠI CƯƠNG | 1. ĐẠI CƯƠNG |  |
| body | Viêm khớp dạng thấp là bệnh lý tự miễn mạn tính, đặc trưng bởi | Viêm khớp dạng thấp la bệnh lý tự miễn mạn tính, đặc trưng bởi | drop_diacritics: `là` → `la` |
| body | tình trạng viêm màng hoạt dịch ở nhiều khớp, có tính chất đối | tình trạng viêrn màng hoạt dịch ở nhiều khớp, có tính chất đối | char_confusion: `viêm` → `viêrn` |
| body | xứng. Bệnh gặp chủ yếu ở nữ giới, tuổi trung niên từ 30 đến 50. | xứng. Bệnh gặp chủ yếu ở nữ giới, tuổi trung niên từ 30 đến 50. |  |
| body | Nếu không được điều trị đúng, bệnh tiến triển gây hủy hoại sụn | Nếu không được điều trị đúng, bệnh tiến triển gây hủy hoại sụn |  |
| body | khớp, biến dạng khớp và tàn phế. | khớp, biến dạng khớp và tàn phế. |  |
| heading | 2. NGUYÊN NHÂN | 2. NGUYEN NHÂN | drop_diacritics: `NGUYÊN` → `NGUYEN` |
| body | Nguyên nhân chính xác của bệnh chưa được biết rõ. Bệnh được | Nguyên nhân chính xác của bệnh chưa được biết rõ. Bệnh được |  |
| body | cho là kết quả của sự tương tác giữa yếu tố di truyền và yếu tố | cho 1à kết quả của sự tương tác giữa yếu tố di truyền và yếu tố | char_confusion: `là` → `1à` |
| body | môi trường. | môi trường. |  |
| heading | 2.1. Yếu tố nguy cơ | 2.1. Yếu tố nguy cơ |  |
| body | - Yếu tố di truyền: người mang kháng nguyên HLA-DR4 có nguy | - Yếu tố di truyen: người mang kháng nguyên HLA-DR4 có nguy | drop_diacritics: `truyền` → `truyen` |
| body | cơ mắc bệnh cao hơn. | cơ mắc bệnh cao hơn. |  |
| body | - Giới tính nữ và các thay đổi nội tiết. | - Giới tính nữ và các thay đổi nội tiết. |  |
| body | - Hút thuốc lá là yếu tố môi trường quan trọng nhất. | - Hút tbuốc lá là yếu tố môi trường quan trọng nhất. | char_confusion: `thuốc` → `tbuốc` |
| body | - Nhiễm khuẩn, nhiễm virus có thể đóng vai trò khởi phát. | - Nhiễm khuẩn, nhiễm virus có thể đóng vai trò khởi phát. |  |
| heading | 3. TRIỆU CHỨNG | 3. TRIỆU CHỨNG |  |
| heading | 3.1. Lâm sàng | 3.1. Lâm sàng |  |
| body | - Viêm nhiều khớp nhỏ ở bàn tay như khớp cổ tay, khớp bàn | - Viêm nhiều khớp nhỏ ở bàn tay như khớp cổ tay, khớp bàn |  |
| body | ngón và khớp ngón gần, có tính chất đối xứng hai bên. | ngón và kbớp ngón gần, có tính chất đối xứng hai bên. | char_confusion: `khớp` → `kbớp` |
| body | - Cứng khớp buổi sáng kéo dài trên 1 giờ. | - Cứng khớp buổi sáng kéo dài trên 1 giờ. |  |
| body | - Khớp sưng, đau, nóng; về sau có thể biến dạng như bàn tay | - Khớp sưng, đau, nóng; về sau có thể biến dạng như bàn tay |  |
| footer | – 1 – | – 1 – |  |

## Trang PDF 5 (trang in 2)

| vai trò | văn bản sạch | lớp OCR | lỗi đã cài |
|---|---|---|---|
| body | dưới da. | duoi da. | drop_diacritics: `dưới` → `duoi` |
| body | - Tốc độ máu lắng và protein phản ứng C (CRP) tăng. | - Tốc độ máu lắng vá protein phản ứng C (CRP) tăng. _(NFD)_ | wrong_tone: `và` → `vá`<br>nfd_line: `- Tốc độ máu lắng và protein phản ứng C (CRP) tăng.` → `(cả dòng ở dạng NFD)` |
| body | methotrexat 7,5-15 mg mỗi tuần, kết hợp acid folic. | methotrexat 7,5-15 mg rnỗi tuần, kết hợp acid folic. | char_confusion: `mỗi` → `rnỗi` |
| body | kinh điển. | kinh dien. | drop_diacritics: `điển` → `dien` |
| body | - Phục hồi chức năng, vật lý trị liệu, tập vận động khớp. | - Phục hồi chức năng, vật lý trị liệu, tập van động khớp. | drop_diacritics: `vận` → `van` |
| body | - Phát hiện sớm, điều trị sớm để hạn chế biến dạng khớp. | - Phát hiện sớm, điều trị sớm để bạn chế biến dạng khớp. | char_confusion: `hạn` → `bạn` |

## Trang PDF 6 (trang in 3)

| vai trò | văn bản sạch | lớp OCR | lỗi đã cài |
|---|---|---|---|
| heading | 1. ĐẠI CƯƠNG | 1. DAI CƯƠNG | drop_diacritics: `ĐẠI` → `DAI` |
| body | tổn thương sụn khớp, kèm theo phản ứng của xương dưới sụn và | tổn thương sụn khớp, kèm theo phảnứng của xương dưới sụn và | merge_words: `phản ứng` → `phảnứng` |
| body | - Béo phì làm tăng tải trọng lên khớp gối. | - Béo phì làm tăng tải trong lên khớp gối. | drop_diacritics: `trọng` → `trong` |
| body | - Nghề nghiệp phải đứng lâu, mang vác nặng. | - Nghề nghiệp phải đứng lau, mang vác nặng. | drop_diacritics: `lâu` → `lau` |
| heading | 3. TRIỆU CHỨNG | 3. TRIỆU CHUNG | drop_diacritics: `CHỨNG` → `CHUNG` |
| body | - Cứng khớp buổi sáng dưới 30 phút. | - Cung khớp buổi sáng dưới 30 phút. | drop_diacritics: `Cứng` → `Cung` |
| body | - Hạn chế vận động, có thể có tràn dịch khớp gối. | - Hạn chế vận động, có thể co tràn dịch khớp gối. | drop_diacritics: `có` → `co` |
| body | - X quang: hẹp khe khớp, đặc xương dưới sụn, gai xương ở rìa | - X quang: hẹp khe khớp, đắc xương dưới sụn, gai xương ở rìa | wrong_tone: `đặc` → `đắc` |
| body | Chẩn đoán theo tiêu chuẩn ACR 1991: đau khớp gối kèm gai | Chẩn đoán theo tiêu chuẩn ACR 1991: đau khớp gối kem gai | drop_diacritics: `kèm` → `kem` |
| body | 50, cứng khớp buổi sáng dưới 30 phút, có tiếng lục khục khi cử | 50, cứng khớp buổi sang dưới 30 phút, có tiếng lục khục khi cử | drop_diacritics: `sáng` → `sang` |
| body | động. | dong. | drop_diacritics: `động` → `dong` |

## Trang PDF 7 (trang in 4)

| vai trò | văn bản sạch | lớp OCR | lỗi đã cài |
|---|---|---|---|
| body | - Giảm cân, tập luyện tăng sức mạnh cơ đùi. | - Giảm can, tập luyện tăng sức mạnh cơ đùi. | drop_diacritics: `cân` → `can` |
| body | - Paracetamol 500 mg mỗi lần, không quá 3 g mỗi ngày. | ⚠️ - Paracetamol 5OO mg mỗi lần, không quá 3 g mỗi ngày. | digit_confusion: `Paracetamol 500 mg` → `Paracetamol 5OO mg` |
| body | đợt đau. | dot đau. | drop_diacritics: `đợt` → `dot` |

## Trang PDF 8 (trang in 5)

| vai trò | văn bản sạch | lớp OCR | lỗi đã cài |
|---|---|---|---|
| body | dày hoặc tá tràng, có thể lan sâu tới lớp cơ niêm. Bệnh có tính | dày boặc tá tràng, có thể lan sâu tới lớp cơ niêm. Bệnh có tính | char_confusion: `hoặc` → `boặc` |
| body | chất mạn tính, hay tái phát. | chất mạn tính, hay tai phát. | drop_diacritics: `tái` → `tai` |
| heading | 4. BIẾN CHỨNG | 4. BIEN CHỨNG | drop_diacritics: `BIẾN` → `BIEN` |
| body | - Xuất huyết tiêu hóa: nôn ra máu, đi ngoài phân đen. | - Xuất huyết tieu hóa: nôn ra máu, đi ngoài phân đen. | drop_diacritics: `tiêu` → `tieu` |
| body | soi hoặc test hơi thở. | soi hoac test hơi thở. | drop_diacritics: `hoặc` → `hoac` |

## Trang PDF 9 (trang in 6)

| vai trò | văn bản sạch | lớp OCR | lỗi đã cài |
|---|---|---|---|
| heading | 6. ĐIỀU TRỊ | 6. ĐIỀU TRI | drop_diacritics: `TRỊ` → `TRI` |
| body | - Thuốc ức chế bơm proton: omeprazol 20 mg uống 2 lần mỗi | - Thuốc ức chế bơm proton: omeprazol 20 mg uống 2 lần mỗi _(NFD)_ | nfd_line: `- Thuốc ức chế bơm proton: omeprazol 20 mg uống 2 lần mỗi` → `(cả dòng ở dạng NFD)` |
| body | ngày. | ngay. | drop_diacritics: `ngày` → `ngay` |
| caption | Bảng 2.1. Phác đồ diệt Helicobacter pylori 3 thuốc | Bảng 2.1. Phác độ diệt Helicobacter pylori 3 thuốc | wrong_tone: `đồ` → `độ` |
| table | Thuốc | Thuộc | wrong_tone: `Thuốc` → `Thuộc` |
| table | 14 ngày | 14 ngảy | wrong_tone: `ngày` → `ngảy` |
| table | 1 g | ⚠️ l g | digit_confusion: `1 g` → `l g` |
| table | 14 ngày | 14 ngày | wrong_tone: `ngày` → `ngảy` |
| table | 14 ngày | 14 ngày | wrong_tone: `ngày` → `ngảy` |
| body | - Ăn uống điều độ, đúng giờ; hạn chế rượu bia, không hút | - Ăn uống điều độ, đúng giờ; hạn chế rượu bia, khong hút | drop_diacritics: `không` → `khong` |
| body | - Không tự ý dùng thuốc chống viêm không steroid kéo dài. | - Không tự ý dùng thuốc chống viêm không steroid kẻo dài. | wrong_tone: `kéo` → `kẻo` |
