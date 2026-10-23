# Plan P2R: Bộ luật riêng cho sách IASP "Classification of Chronic Pain"

> Trạng thái: `Đã duyệt` 2026-10-23 · IASP là **sách chính** · repo private · Ngày: 2026-10-23
> Sách: `data/Classification-of-Chronic-Pain (2).pdf`: 238 trang, tiếng Anh, IASP Press 1994, xuất từ Word (chữ chuẩn, không lỗi OCR)

## 1. Mục tiêu

**Biến Part II của sách (PDF 53–222, khoảng 250–300 hội chứng đau) thành cây có cấu trúc**, để các phase sau tìm kiếm, hỏi đáp và trích xuất được.

Ví dụ kết quả mong muốn (mục pilot `GROUP XI`):

```
Part II › E. Local syndromes of the upper limbs and relatively generalized syndromes …
└─ GROUP XI: Pain in the shoulder, arm, and hand                          tr.in 121–127
   ├─ Tumors of the Brachial Plexus        mã XI-1 · mã IASP 102.X4b, 202.X4b
   │  ├─ Definition                [definition]   "Progressive aching, burning pain with paresthesias …"
   │  ├─ Site                      [site]         "Shoulder and upper limb."
   │  ├─ System                    [body_system]  "Nervous system."
   │  ├─ Tumors                    [other ⚑]      "Benign tumors: schwannoma, neurofibroma …"
   │  ├─ Main Features             [symptom]      "Incidence: the specific tumors of peripheral nerve …"
   │  ├─ Associated Symptoms       [symptom]
   │  ├─ Signs and Laboratory Findings  [paraclinical]
   │  └─ Code                      [code]         "102.X4b / 202.X4b"
   ├─ Carpal Tunnel Syndrome …             mã XI-…
   …
```

Đầu ra **cùng định dạng** với sách mẫu (`nodes.jsonl`, `tree.md`, `tree_report.md`), nên P3 trở đi dùng được ngay.

## 2. Cách tổ chức: mỗi sách một bộ luật riêng

```
                       ┌── luật sách mẫu tiếng Việt (code P1/P2 hiện có) ── book01
 dm --book <tên> ──────┤
                       └── luật sách IASP (MỚI: src/dataminer/books/iasp/) ── iasp
                                   │
                                   ▼
                     đầu ra chung: blocks.jsonl → nodes.jsonl → tree.md, tree_report.md
                     (dùng chung: dựng cây, kiểm bất biến, ID ổn định, báo cáo, duyệt CSV)
```

- **Luật riêng** nằm ở hai chỗ: `src/dataminer/books/iasp/` (code) và `configs/books/iasp.yaml` (các con số: trang, cỡ chữ, vị trí cột). Luật chỉ áp dụng khi chạy `--book iasp`.
- **Dữ liệu riêng** nằm ở `data/books/iasp/`, không đụng dữ liệu sách mẫu.
- Sách mẫu giữ nguyên luật cũ. Toàn bộ 509 test hiện có vẫn phải pass, như một lưới an toàn; ngoài ra không tốn công gì thêm cho sách mẫu.

## 3. Bộ luật của sách IASP (đã kiểm trên PDF thật)

| # | Luật | Ví dụ thật trong sách |
|---|---|---|
| **L1** | **Phạm vi:** chỉ xử lý **Part II** (PDF 53–222), phần mô tả các hội chứng. Bỏ qua phần đầu sách, Part I (danh sách mã), Part III (định nghĩa thuật ngữ), Index. Hai phần sau có thể làm ở plan riêng | `PART II · DETAILED DESCRIPTIONS OF PAIN SYNDROMES` ở PDF 53 |
| **L2** | **Số trang:** dòng đầu mỗi trang là `Page 121` (hoặc chỉ `1`), đứng ở góc phải. Đây là số trang in, không phải nội dung. Trang in = trang PDF − 16 | PDF 137 → `Page 121` |
| **L3** | **Dòng rác:** bỏ `Page 120 is BLANK` | PDF 136 |
| **L4** | **Thứ tự đọc 2 cột.** Cột trái bắt đầu ở x ≈ 65, cột phải ở x ≈ 319. Dòng **vắt ngang qua khe giữa** (tiêu đề nhóm dài) là dòng toàn trang. Thứ tự: dòng toàn trang → **hết cột trái** → **hết cột phải** | PDF 57: `Complex Regional Pain Syndrome… (1-4)` → `Definition` → … (cột trái) → `System` → `Main Features` → … (cột phải) |
| **L5** | **Nhóm chữ cái** (A.–G.): chữ đậm cỡ 13–14, IN HOA, có thể tách 2–3 dòng → **nhãn** của các chương bên dưới (hiện trong đường dẫn), không phải một cấp riêng | `E.` + `LOCAL SYNDROMES OF THE UPPER LIMBS AND RELATIVELY` + `GENERALIZED SYNDROMES …` |
| **L6** | **Nhóm La Mã** = **chương**: dòng đậm cỡ 13–13.5, IN HOA, bắt đầu bằng `GROUP <La Mã>:`, có thể 2 dòng | `GROUP XI:  PAIN IN THE SHOULDER, ARM, AND HAND`; `GROUP XXIV: DISEASES OF THE BLADDER, UTERUS, OVARIES,` + `AND ADNEXA` |
| **L7** | **Hội chứng** = **bệnh**: dòng đậm cỡ 12.5–15, chữ thường. Tên kéo dài nhiều dòng **cho tới khi gặp mã trong ngoặc**; mã có thể đứng riêng một dòng | `Trigeminal Neuralgia` + `(Tic Douloureux) (II-1)`; `Tumors of the Brachial Plexus` + `(XI-1)` |
| **L8** | **Chuẩn hóa mã hội chứng.** Nhóm I đôi khi in bằng chữ số Ả Rập hoặc chữ I: `(1-4)` ≡ `I-4`; `(XXIII-I)` ≡ `XXIII-1`. Mã được lưu thành **thuộc tính** của hội chứng | `Phantom Pain (1-3)` → mã `I-3` |
| **L9** | **Hội chứng không có mã:** vẫn nhận là hội chứng nếu đúng kiểu chữ ở L7, nhưng gắn cờ `no_code` để xem lại | `Testicular Pain` (PDF 188) |
| **L10** | **Mục** = dòng đậm, cỡ chữ thường (khoảng 10), ngắn, không kết thúc bằng dấu chấm. Tên mục bị ngắt dòng thì nối lại | `Definition`, `Site`, `Main Features`, `Tumors`; `Summary of Essential Features and Diagnostic` + `Criteria` |
| **L11** | **Mã IASP 5 trục** trong mục `Code` → tách thành **thuộc tính** `iasp_codes` của hội chứng (P4 sẽ dùng) | `Code` → `102.X4b`, `202.X4b` |
| **L12** | **Mục lục** (PDF 5–6) dạng "tên ↵ số trang dòng dưới". Dùng để đối chiếu nhóm La Mã: tên và trang | `XI. Pain in the Shoulder, Arm, and Hand` ↵ `121` ↔ cây `GROUP XI: …` bắt đầu tr.in 121 |
| **L13** | **Loại mục:** từ điển tiếng Anh (bảng dưới). Tên mục lạ (như `Tumors`) → `other` + vào CSV để duyệt (dùng lại cơ chế của P2.4) | |

**Từ điển tên mục → loại mục** (đếm thật số lần xuất hiện trong sách):

| Tên mục | Số lần | Loại |
|---|---|---|
| Definition | 242 | definition |
| Main Features (160) · Clinical Features (77) · Associated Symptoms (79) · Signs (66) | | symptom |
| Laboratory Findings (34) · Signs and Laboratory Findings (50) | | paraclinical |
| Pathology | 163 | pathophysiology |
| Essential Features · Diagnostic Criteria · Diagnostic Features · Criteria · Summary of Essential Features and Diagnostic Criteria | 54 + 68 + 41 + 26 + 25 | diagnosis |
| Differential Diagnosis | 131 | differential_diagnosis |
| Relief | 70 | treatment |
| Complications | 98 | complication |
| Usual Course | 114 | prognosis |
| Site | 147 | **site** *(loại mới)* |
| System | 130 | **body_system** *(loại mới)* |
| Code | 275 | **code** *(loại mới)* |
| Social and Physical Disability | 74 | **disability** *(loại mới)* |
| References · Reference | 65 + 24 | **references** *(loại mới)* |
| Remarks | 44 | other |

> 5 loại mới (`site`, `body_system`, `code`, `disability`, `references`) chỉ thêm vào danh sách loại mục, không ảnh hưởng sách mẫu. Nếu không thêm, các mục này rơi vào `other`, khoảng 30% số mục.

## 4. Các việc (I1–I6)

> **Làm trước I1:** sắp xếp lại code theo [architecture.md](architecture.md), gồm các bước S1–S5. Đây là sắp xếp lại, không đổi kết quả: dữ liệu sách mẫu phải giống hệt từng byte. Sau đó I1 chỉ còn là tạo `books/iasp/` + `configs/books/iasp/`; mọi luật IASP chỉ nằm trong `books/iasp/`.

| Việc | Làm gì | Xong khi |
|---|---|---|
| **I1** Khung luật riêng | Tùy chọn `dm --book iasp`; `configs/books/iasp.yaml`; thư mục `data/books/iasp/`; sửa lỗi đường dẫn từ điển tên mục (phát hiện khi chạy thử) | Chạy IASP xong, dữ liệu sách mẫu **không đổi một byte**; 509 test cũ pass |
| **I2** Đọc trang (L1–L4) | Đọc Part II, bỏ số trang và dòng rác, **sắp thứ tự 2 cột**, ghép dòng thành đoạn → `blocks.jsonl` (giữ thông tin chữ đậm và cỡ chữ cho I3) | Trang 57 và 137 đọc đúng thứ tự (so tay); 0 "bảng giả" (trước: 370); không đoạn nào chứa dòng của cả 2 cột |
| **I3** Cấp tiêu đề + cây (L5–L11) | Nhận nhóm chữ cái / nhóm La Mã / hội chứng / mục; nối tên nhiều dòng; chuẩn hóa mã; tách mã IASP → dựng cây bằng bộ dựng cây chung | Kiểm tự động mục 5 (A2–A5) đạt |
| **I4** Loại mục + mục lục (L12–L13) | Từ điển tiếng Anh + 5 loại mới; đọc mục lục 2 trang, đối chiếu nhóm La Mã | A5, A6 đạt |
| **I5** Công cụ soi cho bạn | `dm --book iasp p2 spotcheck --n 10` → trang HTML: **ảnh trang PDF gốc ↔ nội dung tách ra** cho 10 hội chứng ngẫu nhiên; `syndromes.csv`: mỗi hội chứng một dòng (mã, tên, trang, có / thiếu mục nào), mở bằng Excel | Bạn mở được, chấm được |
| **I6** Pilot → cả Part II → báo cáo | Pilot `GROUP XI` (PDF 137–143) → bạn soi → chạy cả Part II → `docs/phases/P2R/report.md` viết bằng ngôn ngữ thường, có ví dụ trước/sau | Mục 5 đạt trên cả Part II |

## 5. Chỉ tiêu "đạt"

Sách không có đáp án, nên dùng các phép **đếm độc lập** (đếm thẳng trên PDF bằng code riêng, không qua bộ luật) cộng với người xem:

| # | Chỉ tiêu | Cách đo | Ngưỡng |
|---|---|---|---|
| A1 | Đọc đúng 2 cột | Không đoạn nào chứa dòng của cả 2 cột; số "bảng" trong Part II | 0 vi phạm; 0 bảng giả |
| A2 | **Không sót hội chứng** | Mã trong mỗi nhóm phải **liên tiếp**: XI-1, XI-2, …, XI-n. Thiếu số = sót hoặc đọc sai | 0 chỗ nhảy số (trừ chỗ sách tự nhảy, phải liệt kê ra) |
| A3 | Số hội chứng | Số nút hội chứng ↔ số mã `(…-n)` đếm độc lập trên PDF | Lệch ≤ 1% |
| A4 | Hội chứng có đủ mục chính | % hội chứng có `Definition` hoặc `Code` | ≥ 90% |
| A5 | Loại mục | Tỉ lệ `other` | < 5% |
| A6 | Mục lục | Mọi nhóm La Mã trong mục lục có trong cây, đúng trang | 100% |
| A7 | **Không mất chữ** | Tổng số từ của Part II trên PDF ↔ tổng số từ trong cây (sau khi bỏ số trang) | ≥ 99% |
| A8 | Bất biến cây | G6 hiện có | 100% |
| A9 | **Bạn soi** | 10 hội chứng ngẫu nhiên: đúng tên, đúng ranh giới, đủ mục, không lẫn cột | **≥ 9/10** |

**Chi phí:** $0. Chữ đã chuẩn nên không cần AI sửa chính tả; mọi luật là quy tắc cố định. AI chỉ được dùng nếu bạn muốn nó đề xuất loại cho các tên mục lạ trong CSV duyệt (dưới $0.01).

## 6. Bạn test như thế nào

```bash
# Pilot: GROUP XI (khoảng 7 trang), mất vài giây, $0
uv run dm --book iasp p1 run --scope pilot
uv run dm --book iasp p2 run
uv run dm --book iasp p2 report
uv run dm --book iasp p2 spotcheck --n 10

# Mở xem:
#   data/books/iasp/p2_tree/tree.md                 cây
#   data/books/iasp/p2_tree/syndromes.csv           (Excel) mỗi hội chứng một dòng
#   data/books/iasp/p2_tree/spotcheck/index.html    ảnh trang gốc ↔ nội dung tách ra
#   data/books/iasp/p2_tree/tree_report.md          đối chiếu mục lục, cảnh báo, chỉ tiêu A1–A8

# Cả Part II
uv run dm --book iasp p1 run --scope all && uv run dm --book iasp p2 run && uv run dm --book iasp p2 report
```

## 7. Ngoài phạm vi plan này

- Part I (danh sách mã), Part III (định nghĩa thuật ngữ), Index.
- Bộ câu hỏi chuẩn cho sách này: sẽ do bạn hoặc người chuyên môn viết, ở P3.
- Sửa chính tả bằng AI: không cần với sách này.

## 8. Quyết định đã chốt (2026-10-23)

- IASP là **sách chính**.
- Repo private, nên **được commit kết quả trích từ sách vào `samples/`** để xem. File PDF gốc vẫn để ngoài git (`data/`).

### (Câu hỏi cũ, đã trả lời)

**Bản quyền:** sách © IASP. Repo GitHub của bạn có công khai không?

Mặc định của tôi: **không commit nội dung sách**. Toàn bộ kết quả nằm trong `data/books/iasp/`, thư mục mà git bỏ qua. `samples/` chỉ commit **số liệu** (số hội chứng, tỉ lệ…) và vài trích đoạn ngắn vài dòng để minh họa trong báo cáo.

*(Các câu Q1, Q2, Q4 ở bản plan trước đã được chốt theo đề xuất: nhóm La Mã = chương, nhóm chữ cái = nhãn (L5–L6); thêm 5 loại mục mới (L13); luật riêng cho từng sách.)*
