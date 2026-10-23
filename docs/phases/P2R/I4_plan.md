# Plan I4: loại mục + mục lục cho sách IASP (luật L12-L13)

> Thuộc [plan P2R](plan.md) (đã duyệt) · Trạng thái: `Đã duyệt` 2026-10-23 (mặc định mục 7) · Ngày: 2026-10-23
> Đầu vào: cây của I3 (`data/books/iasp/p2_tree/nodes.jsonl`): 334 hội chứng, 2.463 mục

## 1. Mục tiêu (1 câu)

Mỗi mục của mỗi hội chứng có **loại chuẩn** (định nghĩa / triệu chứng / điều trị / …) để P3-P4 hỏi
được "triệu chứng của bệnh X là gì?", và cây được **đối chiếu với mục lục** của sách để chắc không
sót / sai trang một nhóm nào.

## 2. Vì sao cần

Hiện tại (sau I3) mọi mục đều là `other`:

```
Tumors of the Brachial Plexus (mã XI-1)
├─ Definition   [other]   ← máy chưa biết đây là "định nghĩa"
├─ Main Features [other]  ← … "triệu chứng"
└─ Relief       [other]   ← … "điều trị"
```

Sau I4:

```
Tumors of the Brachial Plexus (mã XI-1)
├─ Definition                     [definition]
├─ Site                           [site]          ← loại mới
├─ System                         [body_system]   ← loại mới
├─ Main Features                  [symptom]
├─ Signs and Laboratory Findings  [paraclinical]
├─ Relief                         [treatment]
├─ Social and Physical Disability [disability]    ← loại mới
├─ Code                           [code]          ← loại mới
└─ References                     [references]    ← loại mới
```

## 3. Việc A - Loại mục (L13)

### 3.1 Khảo sát: 110 tên mục khác nhau, 2.463 lần xuất hiện

Tên mục dày đặc ở vài tên phổ biến; **khoảng 60 tên chỉ xuất hiện 1-2 lần** (biến thể: số ít/số
nhiều, ghép 2 mục, có mã dính vào tên `Code X32.X3a`).

### 3.2 Từ điển `configs/books/iasp/section_map.yaml` (viết tay, đủ 110 tên → $0, không cần AI)

| Loại | Tên mục trong sách (số lần) |
|---|---|
| definition | Definition (242) |
| **site** *(mới)* | Site (147) |
| **body_system** *(mới)* | System (130), Systems, System(s), System Involved |
| symptom | Main Features (160), Main Feature, Clinical Features (77), Associated Symptoms (79), Associated Symptom, Associated Symptoms and Signs (19), Associated Signs and Symptoms, Associated Features, Associated Symptoms and Modifying Factors, Signs (66), Other Features, Aggravating Factors (14), Aggravating Features, Aggravating and Relieving Features, Precipitating Factors (13), Precipitation, Precipitants and Exacerbating Factors, Prevalence |
| paraclinical | Laboratory Findings (34), Laboratory Finding, Signs and Laboratory Findings (50), Laboratory and Radiologic(al) Findings, Radiologic(al)/Radiographic Findings, Imaging, Laboratory Tests, Tests and Laboratory Findings, Associated Symptoms and Signs and Laboratory Findings |
| pathophysiology | Pathology (163), Pathogenesis, Pathophysiology, Pathology and Etiology, Pathology or Other Contribut(ing/ory) Factors |
| cause | Etiology (14), Main Causes, Tumors, Schedule of Neoplastic Diseases / Fractures / Arthritides / Metabolic Bone Diseases / Sites of Infection / Diseases / Trigger Point Sites |
| diagnosis | Diagnostic Criteria (68), Essential Features (54), Summary of Essential Features and Diagnostic Criteria (48), Diagnostic Features (41), Criteria, Summary of Essential Features, Essential Factors, Summary of Essential Findings and Diagnostic Criteria, Classification Criteria … Fibromyalgia, Diagnostic Criteria and Differential Diagnosis |
| differential_diagnosis | Differential Diagnosis (131) |
| treatment | Relief (70), Treatment (11), Relieving Agents, Diagnostic Criteria and Treatment |
| complication | Complications (98), Complication |
| prognosis | Usual Course (114), Course, Duration and Usual Course, Signs and Usual Course |
| **disability** *(mới)* | Social and Physical Disability (74), Social and Physical Disabilities, Social and Physical Impairment, Physical Disability |
| **code** *(mới)* | Code (272), Codes, Code(s), và 13 tên `Code <mã>` |
| **references** *(mới)* | References (65), Reference (24) |
| other | Remarks (44), Associated Disorders, Chronic aneurysm |

- **Tên ghép 2 ý** (`Signs and Laboratory Findings`, `Diagnostic Criteria and Treatment`) chỉ nhận
  được 1 loại → chọn **ý chính** (bảng trên). Ghi chú cạnh từng dòng trong file từ điển.
- **Mục con** `1. History of Widespread Pain` → kế thừa loại của mục cha (`diagnosis`) - cơ chế
  sẵn có của P2.4.
- Dự kiến tỉ lệ `other` ≈ **2%** (Remarks là chính) → đạt A5 (< 5%).

### 3.3 Thay đổi code

| Thay đổi | Lý do | Sách mẫu |
|---|---|---|
| Thêm 5 loại `site, body_system, code, disability, references` vào danh sách loại mục chung | plan P2R mục 3 (đã duyệt) | không dùng → không đổi |
| Luật riêng `BookRules.section_key(title)` (mặc định = cách chuẩn hóa hiện có): IASP bỏ mã dính sau `Code` → `Code X32.X3a` tra như `code` | 13 tên có mã dính | không đổi |
| Báo cáo `tree_report.md`: ma trận bệnh × loại mục chỉ hiện **loại sách có dùng** | tránh thêm 5 cột trống vào báo cáo sách mẫu | không đổi |

## 4. Việc B - Mục lục (L12, **sửa lại mô tả**)

### 4.1 Khảo sát PDF 5-6: khác plan

Plan ghi "tên ↵ số trang dòng dưới". Thực tế: **số trang cùng hàng, căn phải** (x ≈ 490-507);
tên dài xuống dòng thì dòng sau **thụt vào** và không có số:

```
x=126  E.  Local Syndromes of the Upper Limbs and Relatively Generalized      x=488  23   ← Part I
x=140      Syndromes of the Upper and Lower Limbs
…
x=114  Part II   Detailed Descriptions of Pain Syndromes                        x=488  37
x=114  List of Items Usually Provided in Detailed Descriptions …                x=488  38
x=122  A. Relatively Generalized Syndromes                                      x=488  39
x=162      I. Relatively Generalized Syndromes                                  x=488  39
…
x=176      Headache Crosswalk                                                   x=488  90
…
x=184      XI. Pain in the Shoulder, Arm, and Hand                              x=507  121
```

### 4.2 Cách đọc (`books/iasp/toc.py`)

1. Ghép dòng tên với số trang **cùng hàng** (lệch dọc ≤ 3pt); dòng không số → nối vào tên phía trên.
2. Chỉ lấy phần **giữa** `Part II` và `Part III` (mục lục Part I cũng có A.-H. nhưng trỏ trang
   danh mục mã 6-36, không phải phần mô tả).
3. Cấp: `A.`-`H.` → **part**; `I.`-`XXXIII.` → **chapter**; `Headache Crosswalk`, `List of Items…`
   → chapter (không số).
4. Trang PDF = trang in + 16 (L2; kiểm: XI trang in 121 → PDF 137 ✓).

Kết quả dự kiến: 8 nhóm chữ cái + 33 GROUP + 2 chương không số = **43 mục**.

### 4.3 Đối chiếu tên mục lục ↔ tiêu đề trong thân sách

`XI. Pain in the Shoulder, Arm, and Hand` ↔ `GROUP XI: PAIN IN THE SHOULDER, ARM, AND HAND`: bỏ
tiền tố `GROUP XI:` / `XI.` trước khi so (`chapter_prefix` của IASP), so không phân biệt hoa/thường.

### 4.4 Thay đổi code chung (sách mẫu không đổi)

| Thay đổi | Lý do |
|---|---|
| Cấp mục lục thêm `part` | mục lục IASP có nhóm chữ cái |
| So khớp mục lục xét cả tiêu đề cấp `part` | như trên |
| Cấu hình `p2.headings.toc_lists_diseases` (mặc định `true`) - IASP đặt `false` | Mục lục IASP **không liệt kê hội chứng**. Code hiện tại coi "bệnh không có trong mục lục" là đáng ngờ → sẽ hạ tin cậy cả 334 hội chứng và gắn cờ `missing_from_toc` sai |

## 5. Chỉ tiêu đạt

| # | Kiểm | Cách đo | Ngưỡng |
|---|---|---|---|
| A5 | Loại mục | tỉ lệ mục `other` / tổng số mục | < 5% |
| A5b | Từ điển đủ | số tên mục không tra được (`section_type_unknown`) | 0 |
| A6 | Mục lục | mọi GROUP (I-XXXIII) và nhóm chữ cái (A-H) của mục lục có **đúng 1 nút** trong cây, **đúng trang** | 41/41 |
| A6b | Đọc mục lục độc lập | số mục đọc được ↔ đếm tay trên PDF 5-6 (Part II) | 43 = 43 |
| - | Không hỏng I1-I3 | A1, A2, A3, A4, A7, A8 chạy lại | như cũ |
| - | Sách mẫu | 12 file đầu ra như sau I3 (giống hệt trừ `attrs: {}`) | 12/12 |

A5, A6 thêm vào `evaluation/checks.py`; script kiểm `samples/P2R/scripts/check_p2_iasp.py` chạy
thêm 2 chỉ tiêu. `dm --book iasp p2 report` phải chạy được và sinh `tree_report.md` cho IASP.

## 6. Mẫu + báo cáo

`samples/P2R/I4/`: `section_types.md` (110 tên → loại, số lần), `toc.md` (43 mục đọc được, trang
in/PDF, nút khớp trong cây), `tree_group_xi.md` (cây GROUP XI có loại mục), `p2_checks.txt`,
`tree_report.md` (bản cho IASP), `mutations.txt`. Báo cáo `docs/phases/P2R/I4_report.md`.

## 7. Cần bạn quyết (mặc định của tôi in đậm)

1. **Aggravating / Precipitating Factors** (yếu tố làm đau nặng hơn / khởi phát cơn, ~30 lần):
   **`symptom`** (là đặc điểm lâm sàng của cơn đau) hay `risk_factor`?
2. **Remarks** (44 lần, ghi chú tự do): **`other`** hay tạo loại mới `note`?
3. **Schedule of …** (danh sách bệnh gây đau ở các hội chứng cột sống, ~27 lần): **`cause`**?

## 8. Ngoài phạm vi I4

Spotcheck HTML + `syndromes.csv` (I5). Pilot → bạn soát → cả Part II → báo cáo cuối (I6).

## 9. Thay đổi khi triển khai (2026-10-23)

- Ngưỡng khớp mục lục của IASP hạ 0.85 → **0.80**: sách đảo từ giữa mục lục và thân sách
  (`IX. Cervical Spinal or Radicular …` ↔ `GROUP IX: CERVICAL OR RADICULAR SPINAL …`, 0.84). A6 so
  bằng số La Mã / chữ cái để chắc không ghép nhầm.
- Bộ đọc mục lục bỏ số trang La Mã ở chân trang (`v`, `vi`).
- A6: 41 mục có số (8 chữ cái + 33 GROUP); 2 mục không số (`Headache Crosswalk` khớp theo tên;
  `List of Items …` không khớp - tên khác hẳn thân sách) không tính.
- Kết quả: [I4_report.md](I4_report.md).
