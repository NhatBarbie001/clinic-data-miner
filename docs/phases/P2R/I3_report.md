# Báo cáo P2R · I3: cấp tiêu đề + cây cho sách IASP

Ngày: 2026-10-23 · Plan: [I3_plan.md](I3_plan.md) · Phạm vi: Part II (PDF 53-222)

## 1. Tóm tắt

Part II giờ thành **một cây** đúng cấu trúc sách:

```
Part II
├─ A. Relatively generalized syndromes … H. Local syndromes of the lower limbs      8 nhóm chữ cái  [part]
│  └─ GROUP I … GROUP XXXIII                                                          35 chương      [chapter]
│     └─ Tumors of the Brachial Plexus (mã XI-1) iasp_codes: 102.X4b, 202.X4b       334 hội chứng   [disease]
│        └─ Definition, Site, System, Main Features, … Code, References          2.461 mục        [section]
```

Mọi chỉ tiêu của I3 **đạt**, đo bằng cách đếm độc lập trên PDF:

| # | Chỉ tiêu | Kết quả | Ngưỡng |
|---|---|---|---|
| A2 | Mã trong mỗi nhóm liên tiếp | **0 chỗ nhảy** trên 331 mã (2 chỗ do sách tự nhảy, đã soát, xem mục 4) | 0 |
| A3 | Số hội chứng: cây ↔ PDF | **331 = 331** (lệch 0%) | ≤ 1% |
| A4 | Hội chứng có `Definition` hoặc `Code` | **96.7%** (324/335) | ≥ 90% |
| A8 | Bất biến cây | **0 vi phạm** | 0 |
| (I2) | A1 trộn cột / A7 mất chữ (chạy lại sau khi sửa P1) | 0 / lệch 0 | 0 |

Chi phí: **$0** (không gọi AI). Sách mẫu: không đổi (mục 6).

## 2. Đã làm gì (bằng ví dụ)

### 2.1 Sửa P1: tiêu đề nhiều dòng bị tách đôi (38 chỗ)

Luật nối tiêu đề cũ (của sách mẫu) chỉ nối 2 dòng **cùng kiểu IN HOA**. Ở IASP, mã hội chứng
in hoa nằm riêng một dòng nên bị tách thành tiêu đề riêng:

| Trước (2 block) | Sau (1 block) |
|---|---|
| `Post-thoracotomy Pain Syndrome` ‖ `(XVII-13)` | `Post-thoracotomy Pain Syndrome (XVII-13)` |
| `E.` ‖ `LOCAL SYNDROMES OF THE UPPER LIMBS …` | `E. LOCAL SYNDROMES OF THE UPPER LIMBS …` |
| `Complex Regional Pain Syndromes` ‖ `(CRPS)` | `Complex Regional Pain Syndromes (CRPS)` |

Nếu không sửa, `(XVII-13)` sẽ thành một "chương" riêng và hội chứng mất mã. Cách sửa: luật nối
tiêu đề thành **luật riêng của từng sách** (`BookRules.heading_joins`). Luật IASP:
- tên hội chứng đã kết thúc bằng mã → dừng (tên hội chứng sau không dính vào);
- dòng chỉ gồm ngoặc `(…)` → nối; `E.` + dòng IN HOA → nối;
- dòng bắt đầu bằng `and`/`or` → nối: `Intermittent Claudication (XV-1)` ↵ `and Rest Pain (XV-2)`
  là một mục gộp 2 hội chứng.

Danh sách đủ 38 chỗ: `samples/P2R/I3/heading_merges.md`.

Thêm: ghi chú in đậm cỡ thường (`Note: “b” coding used to allow …`) trước bị nhận là tên mục,
nay là nội dung. Nhóm chữ cái mở rộng tới **H** (`H. LOCAL SYNDROMES OF THE LOWER LIMBS`).

### 2.2 Cấp tiêu đề

| Tiêu đề | Cấp |
|---|---|
| `E. LOCAL SYNDROMES …` (cỡ lớn, chữ cái) | **part** (cấp mới, xem 2.4) |
| `GROUP XI: PAIN IN THE SHOULDER, ARM, AND HAND` | chapter |
| `PART II`, `DETAILED DESCRIPTIONS …` (IN HOA cỡ ≥ 15) | → nút "Phần đầu" |
| `HEADACHE CROSSWALK`, `ITEMS USUALLY PROVIDED IN DESCRIPTIONS` (IN HOA, không GROUP) | chapter, cờ `unnumbered_chapter` |
| `Tumors of the Brachial Plexus (XI-1)`, `Gout (1-13)` | disease |
| `Testicular Pain` (không mã) | disease, cờ `no_code` |
| `Definition`, `Site`, … (cỡ thường) | section |

### 2.3 Mã hội chứng (L8) và mã IASP 5 trục (L11)

Sách in mã không thống nhất; tất cả được chuẩn hóa vào `numbering` của nút:

| Trong sách | Sau chuẩn hóa | Lý do |
|---|---|---|
| `(1-4)`, `(11-13)`, `(111-2)` | `I-4`, `II-13`, `III-2` | chữ I La Mã in thành số 1 |
| `(XXV-I)` | `XXV-1` | chữ I thay số 1 |
| `(XIX- 2)` | `XIX-2` | dấu cách |

Mã IASP 5 trục lấy từ mục `Code` → `attrs.iasp_codes` (293/335 hội chứng có):

| Trong sách | Sau chuẩn hóa |
|---|---|
| `203.XlcR` / `X34.XOa` | `203.X1cR` / `X34.X0a` (l→1, O→0) |
| `X4X.X l b`, `023 .X l b` | `X4X.X1b`, `023.X1b` (bỏ cách) |
| `006.X81`, `533.X11S` | `006.X8l`, `533.X1lS` (số 1 thay chữ l ở vị trí chữ cái) |
| `Code X32.X3a` (mã trên dòng tên mục) | `X32.X3a` |

42 hội chứng không có mục `Code` (đa số là mục ngắn chỉ 1-2 dòng, vd. PDF 73) → cờ `no_iasp_code`.

### 2.4 Cấp mới `part` (khác plan gốc - giải thích)

Plan gốc gọi nhóm chữ cái là "nhãn hiện trong đường dẫn". Không làm nhãn rời được vì **mỗi block
phải thuộc đúng 1 nút** (bất biến G6), mà tiêu đề `E. …` và đoạn giới thiệu ngay sau nó (vd. PDF
117: "For a discussion of spinal … please see pages 11-16.") cần chỗ ở. Nút `part` hiện trong đường
dẫn đúng như ví dụ của plan: `E. Local syndromes … › GROUP XI: … › Tumors of the Brachial Plexus`.
Sách mẫu không có cấp này.

### 2.5 Các trường hợp đặc biệt được gắn cờ (không im lặng)

| Cờ | Số | Ví dụ |
|---|---|---|
| `no_code` | 5 | `Complex Regional Pain Syndromes (CRPS)` (tên nhóm nhỏ), `Testicular Pain` |
| `chapter_is_syndrome` | 1 | `GROUP XVI: … LOWER LIMBS (XVI-1)`: nhóm chỉ có 1 hội chứng, mã nằm trên dòng GROUP |
| `missing_syndrome_title` | 1 | PDF 185, xem mục 4 |
| `unnumbered_chapter` | 2 | `Headache crosswalk`, `Items usually provided in descriptions` |

## 3. Kiểm chứng

- **Đếm độc lập** (`samples/P2R/scripts/check_p2_iasp.py`): đọc PDF bằng PyMuPDF, lấy chữ đậm cỡ
  ≥ 12, đếm mọi `(nhóm-số)` trên cả trang (mã có thể vắt dòng `(11-` ↵ `13)`). Không dùng code
  P1/P2/books.iasp. Kết quả trong `samples/P2R/I3/p2_checks.txt`.
- **Test:** 617 test pass (tests/unit + tests/books; 61 test mới ở `tests/books/test_iasp_p2.py`, có 1 test chạy trên PDF
  thật: GROUP XI đủ XI-1 … XI-n liên tiếp, mã IASP của XI-1 đúng `102.X4b, 202.X4b`).
- **Đột biến:** cố ý phá 12 luật mới, test bắt được **12/12** (`samples/P2R/I3/mutations.txt`).
- ruff + mypy sạch.

## 4. Lỗi của chính cuốn sách (đã soát trên PDF)

| Chỗ | Hiện tượng | Xử lý |
|---|---|---|
| PDF 185 | **Thiếu dòng tên** `Retroversion of the Uterus (XXIV-7)`: sau References của XXIV-6 là ngay `Definition`. File PDF không có dòng này (đã soát cả lớp chữ lẫn hình) | Nội dung XXIV-7 bị gộp vào `Tuberculous Salpingitis (XXIV-6)` → gắn cờ `missing_syndrome_title` + cảnh báo. A2 liệt kê `XXIV-6→XXIV-8` là chỗ sách tự nhảy |
| PDF 209 | Sách chỉ mô tả `XXIX-4.2` (Ankylosing Spondylitis); 4.1, 4.3, 4.4 chỉ có trong danh mục | A2 liệt kê `XXIX-4→XXIX-4.2` là chỗ sách tự nhảy |

Bộ dò `missing_syndrome_title`: `Definition` lại xuất hiện **sau** `Code`/`References` trong cùng
một hội chứng. Cả Part II chỉ có 1 chỗ (Fibromyalgia có 3 `Definition` nhưng hợp lệ - là định nghĩa
các tiêu chí, nằm trước `Code` - nên không bị cờ).

## 5. Mẫu để xem (`samples/P2R/I3/`)

| File | Nội dung |
|---|---|
| `tree_group_xi.md` | cây GROUP XI (pilot) - **nên xem đầu tiên** |
| `syndromes_all.md` | 335 hội chứng: mã, tên, GROUP, trang, số mục, mã IASP, cờ |
| `heading_merges.md` | 38 tiêu đề được nối lại ở P1 (trước ↔ sau) |
| `p2_checks.txt` | A2, A3, A4, A8 |
| `p1_checks.txt` | A1, A7 chạy lại sau khi sửa P1 |
| `p2_run.txt`, `p1_run.txt` | log chạy (gồm mọi cảnh báo) |
| `mutations.txt` | kết quả kiểm đột biến |

## 6. Ảnh hưởng tới phần dùng chung và sách mẫu

| Thay đổi | Sách mẫu |
|---|---|
| `BookRules.heading_joins` (mặc định = luật cũ) | không đổi |
| `BookRules.annotate_tree` (mặc định không làm gì) | không đổi |
| cấp `part` (RANK dời 1 nhưng thứ tự giữ nguyên) | không có nút part |
| `Node.attrs` (trường mới, mặc định `{}`) | `nodes.jsonl`, `tree.json` có thêm `"attrs": {}`; bỏ trường này đi thì **giống hệt từng byte**; 10 file còn lại giống hệt từng byte |
| `tree.md` hiện mã hội chứng + attrs | sách mẫu không có mã bệnh / attrs → giống hệt |

## 7. Hạn chế, việc tiếp

- **Loại mục** (`section_type`) toàn bộ là `other` - đúng dự kiến, làm ở **I4** (từ điển tiếng Anh
  + 5 loại mới). Mục lục chưa đọc (I4); cảnh báo "Không có mục lục" là bình thường lúc này.
- Trang PDF 54 (giải thích các mục) là chương `Items usually provided in descriptions` với 16 mục
  "mồ côi" (không thuộc hội chứng nào) - đúng nội dung trang, chỉ sinh cảnh báo.
- `Headache crosswalk` (bảng đối chiếu, PDF 106-108) là chương riêng với 193 đoạn văn hàng bảng.
