# Plan I3: cấp tiêu đề + cây cho sách IASP (luật L5-L11)

> Thuộc [plan P2R](plan.md) (đã duyệt) · Ngày: 2026-10-23 · Đầu vào: `data/books/iasp/p1_clean/blocks.jsonl` (I2)

## 1. Mục tiêu

Từ các block tiêu đề của P1, dựng cây Part II:

```
Part II (sách)
└─ E. Local syndromes of the upper limbs and relatively generalized …     [part]    ← nhóm chữ cái
   └─ GROUP XI: Pain in the shoulder, arm, and hand                        [chapter] ← nhóm La Mã
      ├─ Tumors of the Brachial Plexus        mã XI-1 · iasp_codes 102.X4b, 202.X4b   [disease]
      │  ├─ Definition                                                     [section]
      │  ├─ Site …
      │  └─ Code                                                           [section]
      └─ Chemical Irritation of the Brachial Plexus   mã XI-2 …
```

## 2. Khảo sát trên đầu ra I2 (số thật)

2.888 block tiêu đề; 418 block cỡ lớn (≥ 12):

| Loại | Số | Ví dụ |
|---|---|---|
| Hội chứng có mã ở cuối | 309 | `Tumors of the Brachial Plexus (XI-1)` |
| `GROUP <La Mã>:` | 33 | `GROUP XXIV: DISEASES OF THE BLADDER, UTERUS, OVARIES, AND ADNEXA` |
| Chữ thường, không mã | ~45 | `Testicular Pain`; `Porphyria—Hepatic Porphyrias` (tên nhóm nhỏ) |
| IN HOA khác | 17 | `PART II`, `HEADACHE CROSSWALK`, nhóm chữ cái |

**Phát hiện: P1 tách đôi một số tiêu đề**, cần sửa trước khi dựng cây:

| Trường hợp | Hiện tại (2 block) | Đúng (1 block) |
|---|---|---|
| Mã xuống dòng riêng, IN HOA | `Upper Lumbar Spinal Pain of Unknown or Uncertain Origin` + `(XXVI-9.1)` | nối |
| Từ viết tắt trong ngoặc | `Complex Regional Pain Syndromes` + `(CRPS)` | nối |
| Chữ cái nhóm đứng riêng | `E.` + `LOCAL SYNDROMES OF THE UPPER LIMBS …` | nối |
| Tiêu đề căn giữa, dãn dòng rộng | `ITEMS USUALLY PROVIDED IN DESCRIPTIONS` + `OF PAIN SYNDROMES` | nối |

Nguyên nhân: luật nối tiêu đề dùng chung (của sách mẫu) đòi 2 dòng **cùng kiểu IN HOA** và không nối
dòng có số hiệu. Luật đó đúng với sách mẫu, sai với IASP → chuyển thành **luật riêng từng sách**.

**Mã hội chứng in không thống nhất** (L8): nhóm I-III in bằng chữ số `(1-4)`, `(11-13)`, `(111-2)`
(= I-4, II-13, III-2); chữ I thay số 1 `(XXV-I)`; có dấu cách `(XIX- 2)`; mã con `(1-16.1)`.
Một số ngoặc cuối không phải mã: `(CRPS)`, `(Chilblains)`, `(FMF)`.

**Mã IASP 5 trục** (L11) trong mục `Code` cũng có lỗi kiểu chữ: `203.XlcR` (l = 1), `X34.XOa`
(O = 0), `X4X.X l b` (có cách), `002.x2a`. Có khi nằm ngay trên dòng tiêu đề: `Code X32.X3a`.

## 3. Thiết kế

### 3.1 P1: nối tiêu đề nhiều dòng = luật riêng (`BookRules.heading_joins`)

- Phần chung (`text/blocks.py`) hỏi sách: "dòng tiêu đề mới có nối vào tiêu đề đang mở không?".
  Mặc định = luật cũ (sách mẫu **không đổi một byte**).
- Luật IASP: tên đã kết thúc bằng mã → dừng; dòng chỉ gồm `( … )` → nối; tiêu đề đang mở là
  chữ cái nhóm `E.` → nối dòng IN HOA; còn lại như luật cũ.
- Khoảng cách dòng tối đa của tiêu đề thành cấu hình `p1.blocks.heading_gap` (mặc định 1.3 như
  cũ; IASP 2.2 vì tiêu đề căn giữa dãn dòng ~2 lần).
- Nhóm chữ cái mở rộng A-G → **A-H** (khảo sát thấy `H. LOCAL SYNDROMES OF THE LOWER LIMBS`).
- Dòng đậm cỡ thường bắt đầu `Note:` = **nội dung** (ghi chú in đậm, vd. `Note: “b” coding used
  to allow the “a” coding to be em-`), không phải tên mục.
- Số hiệu (`numbering`) của tiêu đề: nhóm chữ cái → `E`; GROUP → `XI`; hội chứng → **mã đã
  chuẩn hóa** `XI-1`, `I-4`, `XXV-1`, `I-16.1`.

### 3.2 P2: cấp tiêu đề (`IaspRules.rule_level`)

| Điều kiện (block tiêu đề) | Cấp | Tin cậy |
|---|---|---|
| cỡ lớn, số hiệu là chữ cái (`E. LOCAL SYNDROMES …`) | **part** (mới) | high |
| cỡ lớn, `GROUP <La Mã>:` | chapter | high |
| cỡ lớn ≥ 15 (`PART II`, `DETAILED DESCRIPTIONS …`) | other → vào nút "Phần đầu" | high |
| cỡ lớn, IN HOA khác (`HEADACHE CROSSWALK`, `ITEMS USUALLY PROVIDED …`) | chapter, cờ `unnumbered_chapter` | medium |
| cỡ lớn, chữ thường, có mã | disease | high |
| cỡ lớn, chữ thường, không mã | disease, cờ `no_code` (L9) | medium |
| cỡ thường, bắt đầu `1. ` | subsection | high |
| cỡ thường còn lại | section | high |

**Cấp mới `part`** (nhóm chữ cái): plan gọi là "nhãn hiện trong đường dẫn". Không làm nhãn rời
được vì **mỗi block phải thuộc đúng 1 nút** (bất biến G6), mà tiêu đề `E. …` và đoạn giới thiệu
ngay sau nó cần chỗ ở. Nút `part` nằm giữa sách và chương, hiện trong đường dẫn đúng như ví dụ
plan; sách mẫu không có cấp này → không ảnh hưởng.

### 3.3 Tên hiển thị (`display_title`)

- part: `E. Local syndromes of the upper limbs and …` (giữ chữ cái, phần sau viết thường)
- chapter: `GROUP XI: Pain in the shoulder, arm, and hand`
- disease: bỏ mã ở cuối → `Tumors of the Brachial Plexus` (mã ở `numbering`)

### 3.4 Thuộc tính sau khi dựng cây (`BookRules.annotate_tree`, mới, mặc định không làm gì)

- `Node.attrs` (trường mới, mặc định rỗng): `iasp_codes` của hội chứng, lấy từ mục `Code`
  (cả tiêu đề `Code X32.X3a` và nội dung) → chuẩn hóa `l→1`, `O→0`, bỏ cách, `x→X`.
- Cờ: `no_code` (hội chứng không mã), `code_group_mismatch` (mã `XII-3` nằm trong GROUP XI),
  `no_iasp_code` (hội chứng không tìm thấy mã IASP nào).

### 3.5 Mục lục: tạm trả rỗng (đọc thật ở I4), không lỗi.

## 4. Kiểm tra (đạt khi)

| # | Kiểm | Cách đo | Ngưỡng |
|---|---|---|---|
| A2 | Không sót hội chứng | mã trong mỗi GROUP liên tiếp 1, 2, 3… (mã con 7.1, 7.2 được) | 0 chỗ nhảy, hoặc liệt kê chỗ sách tự nhảy |
| A3 | Số hội chứng | số mã hội chứng đếm **độc lập** trên PDF (PyMuPDF, chữ đậm cỡ ≥ 12, không qua code P1/P2) ↔ số nút disease có mã | lệch ≤ 1% |
| A4 | Đủ mục chính | % hội chứng có mục `Definition` hoặc `Code` | ≥ 90% |
| A8 | Bất biến cây | `check_invariants` (chạy sẵn trong build_tree) | 100% |
| - | Sách mẫu | 12 file đầu ra giống hệt từng byte, trừ trường mới `attrs: {}` trong nodes.jsonl / tree.json (kiểm bằng cách bỏ trường đó rồi so sha256) | 12/12 |

Kiểm A2-A4 viết ở `evaluation/checks.py` (dùng lại ở I4-I6); đếm độc lập ở
`samples/P2R/scripts/check_p2_iasp.py`.

## 5. Mẫu + báo cáo

`samples/P2R/I3/`: `tree_group_xi.md` (cây GROUP XI), `syndromes_all.md` (mọi hội chứng: mã, tên,
trang, số mục, mã IASP), `p2_checks.txt`, `p2_run.txt`, `heading_merges.md` (tiêu đề được nối
lại ở P1: trước ↔ sau). Báo cáo `docs/phases/P2R/I3_report.md`.

## 6. Ngoài phạm vi I3

Loại mục (`section_type`, 5 loại mới) và mục lục: I4. Spotcheck HTML, syndromes.csv: I5.

## 7. Thay đổi khi triển khai (2026-10-23)

- **Bỏ `p1.blocks.heading_gap`** (mục 3.1): cho tiêu đề dãn dòng rộng thì cũng nối nhầm 2 tên mục
  liền nhau (`Code X32.X3a` ↵ `References`). Thay bằng: dòng IN HOA bắt đầu bằng từ nối (`OF …`)
  → cấp `other` (chỉ 1 chỗ: PDF 54).
- **Thêm:** dòng `and …` / `or …` nối vào tiêu đề kể cả sau mã (mục gộp `Intermittent Claudication
  (XV-1) and Rest Pain (XV-2)`); tên mục cỡ ≥ 15 chỉ là "tên phần sách" khi IN HOA (`Gout (1-13)`
  in cỡ 15); GROUP mang mã hội chứng (`GROUP XVI: … (XVI-1)`) → cờ `chapter_is_syndrome`; bộ dò
  `missing_syndrome_title` (sách thiếu tên hội chứng ở PDF 185).
- Kết quả: [I3_report.md](I3_report.md).
