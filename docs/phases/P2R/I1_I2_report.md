# Báo cáo P2R · I1 + I2: hồ sơ sách IASP + luật đọc trang (P1)

Ngày: 2026-10-23 · Sách: IASP "Classification of Chronic Pain" · Phạm vi: Part II (PDF 53-222)

## 1. Tóm tắt một câu

P1 giờ đọc sách IASP **đúng thứ tự cột**, nhận **tiêu đề chữ đậm**, **bỏ gạch nối cuối dòng**,
và **không mất chữ nào** (đếm độc lập trên PDF: lệch 0). Sách mẫu vẫn cho kết quả **giống hệt từng byte**.

## 2. Đã làm gì (bằng ví dụ)

### 2.1 I1: hồ sơ sách `configs/books/iasp/book.yaml`

Mỗi sách có file cấu hình riêng. Với IASP:

| Thiết lập | Giá trị | Vì sao |
|---|---|---|
| `content_pages: [53, 222]` | chỉ Part II | phần mô tả hội chứng; trước/sau là lời nói đầu, phụ lục (luật L1) |
| `pilot: 137-143` | GROUP XI | chạy thử nhỏ trước khi chạy cả sách |
| `fix.enabled: false` | tắt sửa OCR | PDF xuất từ Word, chữ đã sạch, không cần LLM sửa (tiết kiệm tiền) |
| `detect_tables: false` | tắt dò bảng | 2 cột đặt cạnh nhau bị nhầm thành bảng (370 bảng giả) |
| `dehyphenate: true` | bỏ gạch nối | sách tiếng Anh ngắt từ cuối dòng: "dis-" ↵ "ease" |

Chạy: `uv run dm --book iasp p1 run --scope all`. Bộ luật riêng nằm ở `src/dataminer/books/iasp/`.

### 2.2 I2: luật đọc trang (`books/iasp/layout.py`, `books/iasp/lines.py`)

**a) Đọc theo cột (L4).** Trang có 2 cột. Trước đây chương trình đọc ngang qua 2 cột, ghép
nửa câu cột trái với nửa câu cột phải:

> **Trước:** "Definition The laboratory findings are those of the underlying dis-"
> ("Definition" ở cột trái, phần sau là cột phải bị dính vào)
>
> **Sau:** tiêu đề `Definition` → đoạn "Progressive aching, burning pain with paresthesias…"

Cách làm: dòng nào vắt ngang cả trang (như "GROUP XI: …") chia trang thành các khúc; trong mỗi
khúc đọc hết cột trái từ trên xuống rồi mới sang cột phải.

**b) Tiêu đề = chữ đậm (L7, L10).** Sách mẫu nhận tiêu đề bằng chữ IN HOA; IASP dùng chữ đậm:
- đậm + to hơn chữ thường ≥ 2pt → tên hội chứng: "Tumors of the Brachial Plexus (XI-1)"
- đậm, ngắn, không kết thúc bằng dấu chấm → tên mục: "Definition", "Site", "Main Features"
- câu đậm có dấu chấm ("Pain is severe.") → vẫn là nội dung

**c) Đoạn văn chảy sang cột kế (L4).** Câu chưa hết ở đáy cột trái thì nối tiếp lên đầu cột phải,
block được gắn cờ `joined_across_columns` để soát lại được.

**d) Bỏ gạch nối cuối dòng.** "underlying dis-" ↵ "ease." → "underlying disease.". Nhưng
"anti-" ↵ "inflammatory" phải **giữ** gạch. Quy tắc dựa vào **chính từ vựng của cuốn sách**:
1. sách có chỗ khác viết "anti-inflammatory" giữa dòng → giữ gạch;
2. sách có từ liền "present" → "pre-" + "sent" thành "present";
3. không có bằng chứng → giữ gạch nếu phần trước là tiền tố (anti, non, self, pre…), ngược lại bỏ.

**e) Số trang, rác.** "Page 121" → số trang (bỏ khỏi nội dung); "Page 120 is BLANK" → bỏ.

**f) Bảng đối chiếu mã PDF 106-108 (L14, luật mới).** 3 trang này là bảng thật (mã IASP ↔ mã IHS
"12.7.2"), cột mã IHS bắt đầu đúng khe giữa trang → đọc theo cột sẽ sai. Trang có ≥ 5 ô mã IHS
được đọc theo **hàng**; chữ đậm trong bảng không bị coi là tiêu đề.

### 2.3 Sửa ở phần dùng chung (`text/blocks.py`, ảnh hưởng mọi sách)

- **Lỗi gạch đứng riêng:** "end of sentence -" ↵ "next" từng bị nối thành "-next". Nay chỉ nối
  liền khi trước gạch là chữ cái. Sách mẫu không bị ảnh hưởng (kiểm byte giống hệt).
- **Mảnh sau dấu ngoặc:** "(rec-" ↵ "tal" trước đây không được nhận là mảnh từ → giữ "(rec-tal".
  Nay → "(rectal" (cùng loại: Minneapolis, Eagle, pernio, bilious).

## 3. Kiểm chứng (đếm độc lập trên PDF, không dùng code P1)

Script: `samples/P2R/scripts/check_p1_iasp.py` → `samples/P2R/I2/p1_checks.txt`

| Kiểm | Trước (nguyên trạng) | Sau | Ý nghĩa |
|---|---|---|---|
| Bảng giả | 370 | **0** | không còn ghép 2 cột thành bảng |
| A1 block trộn 2 cột (không có cờ nối) | (hầu hết trang) | **0** | mỗi block chỉ thuộc 1 cột |
| A7 mất chữ | - | **lệch 0** | PDF 450.800 ký tự chữ/số = block 450.698 + 102 ký hiệu đầu dòng |
| Dòng tiêu đề lớn (đậm ≥ 12.4pt) | - | **618 / 618** | mọi tên hội chứng/nhóm thành tiêu đề |
| Mục "Definition" | - | **242 / 242** | |
| Bỏ gạch nối | 0 | **1.838 chỗ bỏ, 31 chỗ giữ** | xem `dehyphenation.md` |

Kết quả P1 Part II: 14.643 dòng → 6.688 block (tiêu đề 2.888, đoạn 3.690, mục liệt kê 110).

Test: 554 test pass (`tests/unit` + `tests/books`, 29 test mới cho IASP, có 1 test chạy trên PDF
thật trang 137 nếu máy có file). ruff + mypy sạch. Sách mẫu: 12/12 file đầu ra giống hệt từng byte.

## 4. Mẫu để xem (`samples/P2R/I2/`)

| File | Nội dung |
|---|---|
| `page137_before_after.md` | trang 137: bảng block trước ↔ sau (nên xem file này đầu tiên) |
| `dehyphenation.md` | toàn bộ chỗ bỏ/giữ gạch nối - soát nhanh từ bị dính sai |
| `p1_checks.txt` | kết quả các phép đếm độc lập ở mục 3 |
| `p1_run.txt` | log chạy P1 |
| `baseline_page137_asis.jsonl` | block trang 137 của lần chạy nguyên trạng (để so) |

## 5. Hạn chế đã biết

- **3 chỗ giữ gạch sai:** "pre-dominance", "pre-pared", "Co-penhagen". Sách không có từ liền nào
  làm bằng chứng nên rơi vào luật tiền tố. Ít, chấp nhận; sẽ hiện trong spotcheck I5.
- **Một số từ ghép giữ gạch tranh luận được:** "sacro-gluteal", "cervico-thoracic" (sách có viết
  có gạch ở chỗ khác nên giữ là đúng theo sách).
- **Bảng đối chiếu PDF 106-108:** đọc theo hàng nhưng vẫn là đoạn văn (chưa thành bảng có cấu
  trúc). Bảng này là mã tham chiếu, không phải nội dung bệnh; để xử lý ở I4 nếu cần.
- `read_toc` và `rule_level` của IASP chưa có (làm ở I3/I4) → `dm --book iasp p2 run` chưa chạy được.

## 6. Bước tiếp: I3

Cấp tiêu đề + cây: GROUP La Mã = chương; nhóm chữ cái (E.) = nhãn; tên hội chứng có mã (XI-1)
= bệnh; mục "Definition", "Site"… = mục con.
