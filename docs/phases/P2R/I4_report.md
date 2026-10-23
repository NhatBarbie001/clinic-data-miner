# Báo cáo P2R · I4: loại mục + mục lục cho sách IASP

Ngày: 2026-10-23 · Plan: [I4_plan.md](I4_plan.md) (đã duyệt, chọn các mặc định ở mục 7) · Phạm vi: Part II

## 1. Tóm tắt

Mỗi mục của 334 hội chứng giờ có **loại chuẩn**, và cây đã được **đối chiếu với mục lục** của sách:

```
Tumors of the Brachial Plexus (mã XI-1) iasp_codes: 102.X4b, 202.X4b
├─ Definition                      [definition]
├─ Site                            [site]
├─ System                          [body_system]
├─ Tumors                          [cause]
├─ Main Features                   [symptom]
├─ Signs and Laboratory Findings   [paraclinical]
├─ Usual Course                    [prognosis]
├─ Social and Physical Disability  [disability]
├─ Diagnostic Criteria             [diagnosis]
├─ Differential Diagnosis          [differential_diagnosis]
└─ Code                            [code]
```

| # | Chỉ tiêu | Kết quả | Ngưỡng |
|---|---|---|---|
| A5 | Mục có loại `other` | **1.9%** (46/2.463: Remarks 44, 2 tên lạ) · **0** tên mục không tra được | < 5%, 0 |
| A6 | Mỗi GROUP + nhóm chữ cái của mục lục có đúng 1 nút, đúng trang | **41/41** | 100% |
| A6b | Số mục lục đọc được ↔ đếm độc lập trên PDF 5-6 | **43 = 43** | bằng nhau |
| A2-A4, A8 | Chỉ tiêu I3 chạy lại | đạt như cũ (0 nhảy mã · 331 = 331 · 96.7% · 0 vi phạm) | |

Chi phí: **$0** (từ điển viết tay đủ 110 tên mục, không hỏi AI). Sách mẫu: không đổi (mục 5).

## 2. Loại mục (L13)

- **Từ điển** `configs/books/iasp/section_map.yaml`: 110 tên mục → 16 loại, gồm 5 loại mới `site`,
  `body_system`, `code`, `disability`, `references`. Theo quyết định của bạn: Aggravating /
  Precipitating Factors → `symptom`; Remarks → `other`; Schedule of … → `cause`.
- **Luật riêng `section_key`**: 13 mục có mã dính sau tên (`Code X32.X3a`, `Code 602.X8`) tra như
  `code`. Không có luật này, 13 mục đó rơi vào `other`.
- 2 mục con (`1. History of Widespread Pain`, `2. Pain in 11 of 18 Tender Point Sites …`) kế thừa
  loại `diagnosis` của mục cha.

Phân bố (số mục): symptom 446 · code 295 · definition 243 · diagnosis 223 · pathophysiology 169 ·
site 147 · body_system 136 · differential_diagnosis 131 · prognosis 117 · complication 102 ·
paraclinical 102 · disability 91 · references 89 · treatment 83 · other 46 · cause 43.
Đầy đủ từng tên: `samples/P2R/I4/section_types.md`.

## 3. Mục lục (L12)

### 3.1 Sửa mô tả trong plan gốc

Plan gốc ghi "tên ↵ số trang dòng dưới". Thực tế số trang **cùng hàng**, căn phải. Bộ đọc mới
(`books/iasp/toc.py`):
- ghép tên với số cùng hàng; dòng không số và thụt vào → nối vào tên phía trên
  (`V. Primary Headache Syndromes, Vascular Disorders, and` ↵ `Cerebrospinal Fluid Syndromes`);
- chỉ lấy phần giữa `Part II` và `Part III` (mục lục Part I cũng có A.-H.);
- bỏ số trang La Mã ở chân trang mục lục (lần chạy đầu tên mục bị dính: `VIII. Visceral Pain in
  the Neck v`).

### 3.2 Kết quả: 43 mục, trang in + 16 = trang PDF

42/43 mục khớp với tiêu đề trong thân sách. Mục không khớp: `List of Items Usually Provided in
Detailed Descriptions of Pain Syndromes` - thân sách in tên khác hẳn (`ITEMS USUALLY PROVIDED IN
DESCRIPTIONS` ↵ `OF PAIN SYNDROMES`, độ giống 0.70). Đây là trang giải thích các mục, không phải
nhóm hội chứng, nên không tính vào A6.

### 3.3 Sách tự viết khác nhau giữa mục lục và thân sách

| Mục lục | Thân sách |
|---|---|
| `IX. Cervical Spinal or Radicular Pain Syndromes` | `GROUP IX: CERVICAL OR RADICULAR SPINAL PAIN SYNDROMES` |
| `XXVI. Lumbar Spinal or Radicular Pain Syndromes` | `GROUP XXVI: LUMBAR OR RADICULAR SPINAL PAIN SYNDROMES` |
| `V. Primary Headache …` | `GROUP V: RIMARY HEADACHE …` (PDF thiếu chữ P - đã soát lớp chữ gốc, giữ nguyên) |

Hai tên đảo từ có độ giống 0.83-0.84 → hạ ngưỡng khớp của IASP từ 0.85 xuống **0.80**
(`p2.headings.toc_match_min`). Để chắc ngưỡng thấp không ghép nhầm nhóm, **A6 so bằng số La Mã /
chữ cái**, không dựa vào tên: cả 41 mục khớp đúng số.

### 3.4 Mục lục không liệt kê hội chứng

Code cũ coi "bệnh vắng mặt trong mục lục" là đáng ngờ (đúng với sách mẫu). Với IASP điều đó sẽ hạ
tin cậy cả 334 hội chứng. Thêm cấu hình `p2.headings.toc_lists_diseases` (mặc định `true` - giữ
hành vi cũ), IASP đặt `false`.

## 4. Kiểm chứng

- `samples/P2R/scripts/check_p2_iasp.py samples/P2R/I4`: A2-A6b, A8 → `p2_checks.txt`. A6b đếm
  độc lập các con số căn phải giữa hàng `Part II` và `Part III` trên PDF 5-6 (PyMuPDF trực tiếp).
- Test: **650 pass** (tests/unit + tests/books; 33 test mới ở `tests/books/test_iasp_i4.py`, có
  1 test đọc mục lục PDF thật).
- Đột biến: phá 12 luật mới, test bắt được **12/12** (`mutations.txt`). Lần đầu 3 đột biến sống
  (ghép mục lục cấp part, A5 với tên lạ khi tỉ lệ thấp, dòng "không bệnh nào có" của báo cáo) →
  đã thêm test.
- ruff + mypy sạch. `dm --book iasp p2 report` chạy được → `tree_report.md`.

## 5. Ảnh hưởng phần dùng chung / sách mẫu

| Thay đổi | Sách mẫu |
|---|---|
| 5 loại mục mới trong danh sách chung | không dùng |
| `BookRules.section_key` (mặc định = chuẩn hóa cũ) | không đổi |
| Cấp mục lục `part`; so khớp mục lục xét cả tiêu đề `part` | không có part |
| `p2.headings.toc_lists_diseases` (mặc định `true`) | hành vi cũ |
| Báo cáo: "không bệnh nào có" bỏ qua loại mới nếu sách không dùng | dòng này giữ nguyên (có test) |

Kiểm byte sách mẫu: 10/12 file giống hệt; `nodes.jsonl`, `tree.json` giống hệt sau khi bỏ trường
`"attrs": {}` (như sau I3).

## 6. Mẫu để xem (`samples/P2R/I4/`)

| File | Nội dung |
|---|---|
| `tree_group_xi.md` | cây GROUP XI có loại mục - **nên xem đầu tiên** |
| `section_types.md` | 110 tên mục → loại, số lần |
| `toc.md` | 43 mục lục ↔ nút trong cây, trang |
| `tree_report.md` | báo cáo cấu trúc của IASP (mục 1-4: tổng quan, mục lục, ma trận hội chứng × loại mục, cảnh báo) |
| `p2_checks.txt`, `p2_run.txt`, `mutations.txt` | kiểm, log, đột biến |
| `syndromes_all.md` | 335 hội chứng (như I3) |

## 7. Việc tiếp: I5

Công cụ soát cho bạn: `dm --book iasp p2 spotcheck --n 10` → trang HTML đặt **ảnh trang PDF gốc
cạnh nội dung đã tách** cho 10 hội chứng ngẫu nhiên, và `syndromes.csv` (mở bằng Excel).
