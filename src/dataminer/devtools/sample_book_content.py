"""Nội dung sách mẫu tổng hợp (tóm lược giáo khoa) - CHỈ dùng để kiểm thử phần mềm.

Cấu trúc mô phỏng giáo trình bệnh học Việt Nam: CHƯƠNG → TÊN BỆNH → mục đánh số → mục con.
Mỗi phần tử là một tuple:
    ("chapter", tiêu_đề_in_hoa, tiêu_đề_thường)
    ("disease", tên_in_hoa, tên_thường)
    ("section", "1. ĐẠI CƯƠNG", section_type)
    ("sub", "3.1. Lâm sàng", section_type)
    ("p", đoạn_văn)
    ("ul", [gạch_đầu_dòng, ...])
    ("table", chú_thích, [[ô, ...], ...])   # hàng đầu là tiêu đề cột
"""

from typing import Any

TITLE = "BỆNH HỌC NỘI KHOA"
RUNNING_TITLE = "Bệnh học nội khoa (sách mẫu)"

COVER = [
    ("cover_title", TITLE),
    ("cover_sub", "Tóm lược một số bệnh thường gặp"),
    ("cover_note", "SÁCH MẪU TỔNG HỢP - CHỈ DÙNG ĐỂ KIỂM THỬ PHẦN MỀM"),
    ("cover_note", "Nội dung tóm lược, không dùng để chẩn đoán hay điều trị."),
    ("cover_pub", "Nhà xuất bản Mẫu - 2026"),
]

BOOK: list[tuple[Any, ...]] = [
    ("chapter", "CHƯƠNG 1. BỆNH CƠ XƯƠNG KHỚP", "Chương 1. Bệnh cơ xương khớp"),
    # ------------------------------------------------------------------ bệnh 1
    ("disease", "VIÊM KHỚP DẠNG THẤP", "Viêm khớp dạng thấp"),
    ("section", "1. ĐẠI CƯƠNG", "definition"),
    (
        "p",
        "Viêm khớp dạng thấp là bệnh lý tự miễn mạn tính, đặc trưng bởi tình trạng viêm "
        "màng hoạt dịch ở nhiều khớp, có tính chất đối xứng. Bệnh gặp chủ yếu ở nữ giới, "
        "tuổi trung niên từ 30 đến 50. Nếu không được điều trị đúng, bệnh tiến triển gây "
        "hủy hoại sụn khớp, biến dạng khớp và tàn phế.",
    ),
    ("section", "2. NGUYÊN NHÂN", "cause"),
    (
        "p",
        "Nguyên nhân chính xác của bệnh chưa được biết rõ. Bệnh được cho là kết quả của sự "
        "tương tác giữa yếu tố di truyền và yếu tố môi trường.",
    ),
    ("sub", "2.1. Yếu tố nguy cơ", "risk_factor"),
    (
        "ul",
        [
            "Yếu tố di truyền: người mang kháng nguyên HLA-DR4 có nguy cơ mắc bệnh cao hơn.",
            "Giới tính nữ và các thay đổi nội tiết.",
            "Hút thuốc lá là yếu tố môi trường quan trọng nhất.",
            "Nhiễm khuẩn, nhiễm virus có thể đóng vai trò khởi phát.",
        ],
    ),
    ("section", "3. TRIỆU CHỨNG", "symptom"),
    ("sub", "3.1. Lâm sàng", "symptom"),
    (
        "ul",
        [
            "Viêm nhiều khớp nhỏ ở bàn tay như khớp cổ tay, khớp bàn ngón và khớp ngón gần, "
            "có tính chất đối xứng hai bên.",
            "Cứng khớp buổi sáng kéo dài trên 1 giờ.",
            "Khớp sưng, đau, nóng; về sau có thể biến dạng như bàn tay gió thổi.",
            "Toàn thân: mệt mỏi, sốt nhẹ, gầy sút cân; có thể có hạt thấp dưới da.",
        ],
    ),
    ("sub", "3.2. Cận lâm sàng", "paraclinical"),
    (
        "ul",
        [
            "Tốc độ máu lắng và protein phản ứng C (CRP) tăng.",
            "Yếu tố dạng thấp (RF) dương tính ở khoảng 70% bệnh nhân; kháng thể anti-CCP "
            "có độ đặc hiệu cao.",
            "X quang bàn tay: mất chất khoáng đầu xương, hẹp khe khớp, hình bào mòn xương.",
        ],
    ),
    ("section", "4. CHẨN ĐOÁN", "diagnosis"),
    (
        "p",
        "Chẩn đoán dựa trên tiêu chuẩn ACR/EULAR 2010. Bệnh nhân được chẩn đoán xác định khi "
        "đạt từ 6/10 điểm trở lên, dựa vào số lượng khớp tổn thương, xét nghiệm huyết thanh, "
        "chỉ số viêm và thời gian có triệu chứng.",
    ),
    ("section", "5. ĐIỀU TRỊ", "treatment"),
    (
        "ul",
        [
            "Thuốc chống viêm không steroid để giảm đau, chống viêm.",
            "Corticoid liều thấp, ví dụ prednisolon 5-10 mg mỗi ngày, dùng trong thời gian ngắn.",
            "Thuốc chống thấp khớp làm thay đổi bệnh (DMARD): methotrexat 7,5-15 mg mỗi tuần, "
            "kết hợp acid folic.",
            "Thuốc sinh học được chỉ định khi đáp ứng kém với DMARD kinh điển.",
            "Phục hồi chức năng, vật lý trị liệu, tập vận động khớp.",
        ],
    ),
    ("section", "6. PHÒNG BỆNH", "prevention"),
    (
        "ul",
        [
            "Không hút thuốc lá.",
            "Phát hiện sớm, điều trị sớm để hạn chế biến dạng khớp.",
            "Duy trì vận động và cân nặng hợp lý.",
        ],
    ),
    # ------------------------------------------------------------------ bệnh 2
    ("disease", "THOÁI HÓA KHỚP GỐI", "Thoái hóa khớp gối"),
    ("section", "1. ĐẠI CƯƠNG", "definition"),
    (
        "p",
        "Thoái hóa khớp gối là bệnh lý mạn tính của khớp, đặc trưng bởi tổn thương sụn khớp, "
        "kèm theo phản ứng của xương dưới sụn và màng hoạt dịch. Bệnh thường gặp ở người trên "
        "50 tuổi và là nguyên nhân hàng đầu gây đau khớp gối ở người cao tuổi.",
    ),
    ("section", "2. NGUYÊN NHÂN", "cause"),
    (
        "ul",
        [
            "Tuổi cao làm sụn khớp lão hóa, giảm khả năng chịu lực.",
            "Béo phì làm tăng tải trọng lên khớp gối.",
            "Chấn thương khớp gối, lệch trục chân như chân vòng kiềng.",
            "Nghề nghiệp phải đứng lâu, mang vác nặng.",
        ],
    ),
    ("section", "3. TRIỆU CHỨNG", "symptom"),
    (
        "ul",
        [
            "Đau khớp gối kiểu cơ học: đau tăng khi vận động, giảm khi nghỉ ngơi.",
            "Cứng khớp buổi sáng dưới 30 phút.",
            "Tiếng lục khục khi cử động khớp.",
            "Hạn chế vận động, có thể có tràn dịch khớp gối.",
            "X quang: hẹp khe khớp, đặc xương dưới sụn, gai xương ở rìa khớp.",
        ],
    ),
    ("section", "4. CHẨN ĐOÁN", "diagnosis"),
    (
        "p",
        "Chẩn đoán theo tiêu chuẩn ACR 1991: đau khớp gối kèm gai xương trên X quang và có ít "
        "nhất một trong các yếu tố: tuổi trên 50, cứng khớp buổi sáng dưới 30 phút, có tiếng "
        "lục khục khi cử động.",
    ),
    ("section", "5. ĐIỀU TRỊ", "treatment"),
    (
        "ul",
        [
            "Giảm cân, tập luyện tăng sức mạnh cơ đùi.",
            "Paracetamol 500 mg mỗi lần, không quá 3 g mỗi ngày.",
            "Thuốc chống viêm không steroid dạng bôi hoặc uống trong đợt đau.",
            "Tiêm corticoid nội khớp khi có tràn dịch, không quá 3 lần mỗi năm.",
            "Phẫu thuật thay khớp gối khi điều trị nội khoa thất bại.",
        ],
    ),
    ("section", "6. PHÒNG BỆNH", "prevention"),
    (
        "ul",
        [
            "Duy trì cân nặng hợp lý, tránh mang vác nặng.",
            "Tập thể dục đều đặn, đúng tư thế.",
        ],
    ),
    # ------------------------------------------------------------------ chương 2
    ("chapter", "CHƯƠNG 2. BỆNH TIÊU HÓA", "Chương 2. Bệnh tiêu hóa"),
    ("disease", "VIÊM LOÉT DẠ DÀY TÁ TRÀNG", "Viêm loét dạ dày tá tràng"),
    ("section", "1. ĐẠI CƯƠNG", "definition"),
    (
        "p",
        "Viêm loét dạ dày tá tràng là tình trạng tổn thương niêm mạc dạ dày hoặc tá tràng, có "
        "thể lan sâu tới lớp cơ niêm. Bệnh có tính chất mạn tính, hay tái phát.",
    ),
    ("section", "2. NGUYÊN NHÂN", "cause"),
    (
        "ul",
        [
            "Nhiễm vi khuẩn Helicobacter pylori là nguyên nhân thường gặp nhất.",
            "Dùng thuốc chống viêm không steroid, aspirin kéo dài.",
            "Các yếu tố thuận lợi: hút thuốc lá, rượu bia, căng thẳng kéo dài.",
        ],
    ),
    ("section", "3. TRIỆU CHỨNG", "symptom"),
    (
        "ul",
        [
            "Đau vùng thượng vị, đau có tính chu kỳ, liên quan đến bữa ăn.",
            "Ợ hơi, ợ chua, buồn nôn, đầy bụng, khó tiêu.",
            "Có thể không có triệu chứng cho tới khi xuất hiện biến chứng.",
        ],
    ),
    ("section", "4. BIẾN CHỨNG", "complication"),
    (
        "ul",
        [
            "Xuất huyết tiêu hóa: nôn ra máu, đi ngoài phân đen.",
            "Thủng ổ loét gây đau bụng dữ dội đột ngột.",
            "Hẹp môn vị: nôn ra thức ăn cũ.",
        ],
    ),
    ("section", "5. CHẨN ĐOÁN", "diagnosis"),
    (
        "p",
        "Nội soi dạ dày tá tràng là phương pháp chẩn đoán xác định. Xét nghiệm tìm "
        "Helicobacter pylori bằng test urease nhanh khi nội soi hoặc test hơi thở.",
    ),
    ("section", "6. ĐIỀU TRỊ", "treatment"),
    (
        "ul",
        [
            "Ngừng các thuốc gây loét nếu có thể.",
            "Thuốc ức chế bơm proton: omeprazol 20 mg uống 2 lần mỗi ngày.",
            "Nếu có Helicobacter pylori: dùng phác đồ diệt vi khuẩn trong 14 ngày (Bảng 2.1).",
        ],
    ),
    (
        "table",
        "Bảng 2.1. Phác đồ diệt Helicobacter pylori 3 thuốc",
        [
            ["Thuốc", "Liều mỗi lần", "Số lần/ngày", "Thời gian"],
            ["Omeprazol", "20 mg", "2", "14 ngày"],
            ["Amoxicilin", "1 g", "2", "14 ngày"],
            ["Clarithromycin", "500 mg", "2", "14 ngày"],
        ],
    ),
    ("section", "7. PHÒNG BỆNH", "prevention"),
    (
        "ul",
        [
            "Ăn uống điều độ, đúng giờ; hạn chế rượu bia, không hút thuốc.",
            "Không tự ý dùng thuốc chống viêm không steroid kéo dài.",
        ],
    ),
]
