# Plan P2: Dựng cấu trúc tài liệu

> Trạng thái: `Đã duyệt`, đang triển khai (P2.1 ✅, P2.2 ✅, P2.3 ✅)
> Ngày tạo: 2026-10-21 · Tham chiếu: [plan.md](../../../plan.md) mục P2 · Đầu vào từ P1: [P1 gate_report](../P1/gate_report.md) · Hồ sơ sách: [book_profile.md](../../book_profile.md)

## 1. Mục tiêu

Biến **danh sách block phẳng** (đầu ra P1) thành **cây tài liệu**: Sách → Chương → Bệnh → Mục → Mục con. Mỗi nút biết:
- **cấp** của nó;
- **loại mục chuẩn** (`definition`, `cause`, `symptom`, `treatment`…);
- **nội dung** của nó (các block thuộc về nó);
- **phạm vi trang**, cả số trang PDF lẫn số trang in.

Cây này là xương sống của mọi phase sau:

| Phase | Dùng cây để |
|---|---|
| P3 | Chunk theo mục; metadata `disease`, `section_type` cho tìm kiếm |
| P4 | Trích xuất theo từng bệnh |
| P5 | Trích dẫn `(Bệnh – Mục, tr.X)` |
| P7 | Sinh dữ liệu huấn luyện theo mục |

**Ví dụ đích** (pilot sách mẫu):

```
Sách: Bệnh học nội khoa
├─ Chương 1. Bệnh cơ xương khớp                         tr.in 1–4
│  ├─ Bệnh: Viêm khớp dạng thấp                          tr.in 1–2
│  │  ├─ 1. ĐẠI CƯƠNG          [definition]   ← 1 đoạn văn
│  │  ├─ 2. NGUYÊN NHÂN        [cause]        ← 1 đoạn văn
│  │  │  └─ 2.1. Yếu tố nguy cơ [risk_factor] ← 4 gạch đầu dòng
│  │  ├─ 3. TRIỆU CHỨNG        [symptom]
│  │  │  ├─ 3.1. Lâm sàng       [symptom]      ← 4 gạch đầu dòng (1 cái nối qua trang)
│  │  │  └─ 3.2. Cận lâm sàng   [paraclinical]
│  │  ├─ 4. CHẨN ĐOÁN … 5. ĐIỀU TRỊ … 6. PHÒNG BỆNH
│  └─ Bệnh: Thoái hóa khớp gối …
└─ Chương 2. Bệnh tiêu hóa
   └─ Bệnh: Viêm loét dạ dày tá tràng
      ├─ … 4. BIẾN CHỨNG [complication] … 6. ĐIỀU TRỊ [treatment] ← có Bảng 2.1 …
```

## 2. Đầu vào / Đầu ra

| | Artifact | Vị trí |
|---|---|---|
| Vào | Block sạch (P1) | `data/p1_clean/blocks.jsonl` |
| Vào | PDF (để đọc **trang mục lục**, nằm ngoài pilot) | `data/raw/book01.pdf` |
| Vào | Từ điển tên mục → loại mục | `configs/section_map.yaml` (mới) |
| Ra | Mục lục đã phân tích | `data/p2_tree/toc.json` |
| Ra | **Cây (dạng phẳng, mỗi nút một dòng)**: đầu vào P3/P4 | `data/p2_tree/nodes.jsonl` |
| Ra | Cây lồng nhau để xem | `data/p2_tree/tree.json`, `tree.md` |
| Ra | Báo cáo cấu trúc + cảnh báo | `data/p2_tree/tree_report.md` |
| Ra | **Bộ câu hỏi chuẩn v1** (EV.1) | `eval/golden_qa_v1.jsonl` |

**Hợp đồng dữ liệu `Node` (SCHEMA_VERSION 1):**

```python
class Node(BaseRecord):
    level: Literal["book", "chapter", "disease", "section", "subsection", "front"]
    parent_id: str | None
    order: int                       # thứ tự trong cha
    title: str                       # tiêu đề đã sạch, vd. "3. TRIỆU CHỨNG"
    title_norm: str                  # bỏ dấu + chữ thường, để so khớp
    display_title: str               # dạng đọc được, vd. "Triệu chứng", "Viêm khớp dạng thấp"
    numbering: str | None            # "3", "3.1", "CHƯƠNG 1"
    section_type: str | None         # chỉ với section/subsection
    path: list[str]                  # ["Chương 1. …", "Viêm khớp dạng thấp", "Triệu chứng", "Lâm sàng"]
    heading_block_id: str | None
    block_ids: list[str]             # nội dung của RIÊNG nút này (không gồm con)
    text: str                        # nội dung riêng, nối các block (bảng ở dạng hàng | cột)
    page_start: int; page_end: int   # phạm vi trang PDF CẢ nhánh (gồm con)
    printed_start: int | None; printed_end: int | None
    flags: list[str]                 # missing_from_toc, numbering_gap, section_type_from_llm…
```

`id = stable_id(book_id, *path)`: ổn định qua các lần chạy, dùng làm khóa trích dẫn ở mọi phase sau.

## 3. Kiến trúc

```
 data/raw/book01.pdf ──► P2.1 toc.py ──► toc.json  (chương/bệnh + số trang in)
                          (tự tìm trang mục lục, đọc bằng hàm P1)
                                             │
 data/p1_clean/blocks.jsonl                  │
        │                                    ▼
        ├──► P2.2 heading_levels.py  ──► cấp của mỗi tiêu đề (chapter/disease/section/subsection/other)
        │       quy tắc (numbering, IN HOA, cỡ chữ)  +  đối chiếu mục lục  +  (LLM nếu còn mơ hồ)
        ▼
     P2.3 tree_builder.py ──► nodes.jsonl, tree.json   (gắn block nội dung vào nút gần nhất)
        │
        ├──► P2.4 section_mapper.py ──► section_type   (từ điển configs/section_map.yaml, so KHÔNG DẤU;
        │                                              tên lạ → LLM đề xuất → người duyệt → ghi vào từ điển)
        ▼
     P2.5 EV.1 golden set ──► eval/golden_qa_v1.jsonl  (30 câu, nguồn = node_id + trích dẫn)
        │
     P2.6 dm p2 run / eval / report, kiểm tra bất biến, tree_report.md, gate P2
```

**Module mới** `src/dataminer/structure/`: `toc.py`, `heading_levels.py`, `tree_builder.py`, `section_mapper.py`, `golden.py`, `pipeline.py`, `report.py`. Thêm `evaluation/p2_eval.py` và `cli_p2.py`.

**Dùng lại từ P0/P1:**

| Thành phần | Dùng để |
|---|---|
| `pdf_reader.read_lines` + `blocks.classify_line` | Đọc trang mục lục |
| `Block.numbering`, `is_upper`, `font_size` | Đặc trưng tiêu đề |
| `text_vi.strip_diacritics` | So khớp không dấu |
| `RunRecorder` | Manifest |
| `LLMClient.chat_json` | Chỉ cho trường hợp mơ hồ |
| `review` (CSV) | Duyệt các ánh xạ do LLM đề xuất |

## 4. Danh sách task

| Task | Nội dung | Plan chi tiết | LLM? |
|---|---|---|---|
| **P2.1** | Mục lục: tự tìm trang mục lục, đọc, phân tích (tiêu đề, cấp, số trang in) | [P2.1_plan.md](P2.1_plan.md) | Không |
| **P2.2** | Phân cấp tiêu đề: chương / bệnh / mục / mục con / khác; đối chiếu mục lục | [P2.2_plan.md](P2.2_plan.md) | Chỉ khi mơ hồ |
| **P2.3** | Dựng cây: gắn nội dung vào nút, phạm vi trang, ID ổn định, bất biến | [P2.3_plan.md](P2.3_plan.md) | Không |
| **P2.4** | Ánh xạ loại mục (`section_type`) qua từ điển; tên lạ → LLM đề xuất → duyệt | [P2.4_plan.md](P2.4_plan.md) | Chỉ tên lạ |
| **P2.5** | EV.1: bộ câu hỏi chuẩn v1 (30 câu, có nguồn) | [P2.5_plan.md](P2.5_plan.md) | Không |
| **P2.6** | `dm p2 run/eval/report`, báo cáo cấu trúc, tái lập, gate P2 | [P2.6_plan.md](P2.6_plan.md) | Không |

Thứ tự tuyến tính. Mỗi task thêm phần đánh giá của mình vào `evaluation/p2_eval.py`.

**Bài học từ P1 được áp dụng ngay từ đầu:**
- **Mỗi quy tắc có ít nhất một test không dựa trên sách mẫu.** Sách mẫu chỉ có 3 bệnh và khuôn rất đều, có thể "quá ngoan".
- **Đối chứng dương / âm** cho phần đánh giá: đánh giá phải biết nói "không đạt".
- **Mutation check có xác nhận đột biến đã áp dụng.**
- **Không bỏ qua im lặng:** nút hoặc block không đối chiếu được thì chỉ tiêu không đạt.

## 5. Cấu hình mới

```yaml
p2:
  toc:
    pages: auto            # auto = tự tìm trong toc_search_pages trang đầu; hoặc [3, 3]
    search_pages: 15
    min_entries: 2         # trang có ≥ 2 dòng chấm dẫn → trang mục lục
  headings:
    disease_size_delta: 1.5   # tiêu đề IN HOA, không đánh số, cỡ ≥ thân bài + 1.5 → ứng viên bệnh
    use_toc: true             # dùng mục lục để xác nhận/sửa cấp
    llm_fallback: true        # tiêu đề còn mơ hồ → hỏi LLM (tác vụ `classify`)
  sections:
    map: configs/section_map.yaml
    llm_fallback: true        # tên mục lạ → LLM đề xuất section_type → hàng đợi duyệt
```

## 6. Ước tính chi phí LLM

| Phạm vi | Lời gọi | Chi phí |
|---|---|---|
| Pilot sách mẫu | **0** (mọi tiêu đề và tên mục đều xử lý được bằng quy tắc + từ điển) | **$0** |
| Sách thật | Vài chục lời gọi cho tiêu đề mơ hồ và tên mục lạ (lần đầu); sau khi duyệt, chúng nằm trong từ điển | **dưới $0.05** |

## 7. Gate P2 (trên pilot sách mẫu, đo tự động với đáp án)

| # | Chỉ tiêu | Ngưỡng |
|---|---|---|
| G1 | Mục lục: số mục, tiêu đề (so không dấu), cấp, số trang in | **100%** (5/5) |
| G2 | Cấp tiêu đề (chương / bệnh / mục / mục con) | **100%** (27/27 tiêu đề pilot) |
| G3 | **Số bệnh trong cây khớp mục lục** (trong phạm vi pilot), và trang bắt đầu khớp | **100%** (3/3); 0 bệnh thừa hoặc thiếu |
| G4 | Nội dung gắn đúng nút: mọi dòng nội dung thuộc đúng bệnh và đúng mục như đáp án | **≥ 99%** dòng; **0** block mồ côi |
| G5 | `section_type` đúng | **≥ 95%**; tỉ lệ `other` **< 5%** |
| G6 | Bất biến cây | 100%: mỗi block thuộc đúng 1 nút; cha chứa phạm vi trang của con; không có nút rỗng mà không có cờ; ID duy nhất |
| G7 | Golden set v1 | 30 câu (≥ 20 cụ thể, ≥ 5 liệt kê, ≥ 5 từ chối); 100% nguồn trỏ tới nút tồn tại và trích dẫn có thật trong nút |
| G8 | Tái lập | Chạy lại → `nodes.jsonl` giống hệt từng byte; $0 |
| G9 | Kỹ thuật | ruff, mypy, pre-commit, toàn bộ test pass; mỗi task có báo cáo + samples |

> Plan tổng (plan.md) có chỉ tiêu "duyệt tay 10 bệnh". Pilot sách mẫu chỉ có 3 bệnh, và có đáp án nên đo tự động 100% (G2–G5). Với sách thật: **duyệt tay `tree.md` của 10 bệnh** (không có đáp án), cộng `dm survey` để đối chiếu.

## 8. Rủi ro và câu hỏi cần chủ dự án quyết định

| # | Rủi ro / câu hỏi | Đề xuất |
|---|---|---|
| R1 | **Sách mẫu quá đều** (mọi bệnh cùng khuôn); sách thật có thể có tiêu đề không đánh số, đánh số kiểu `I.`, `A.`, `a)`, hoặc bệnh không có trong mục lục | Mẫu đánh số nằm trong cấu hình; test tổng hợp cho nhiều kiểu đánh số; cờ `missing_from_toc` thay vì bỏ qua |
| R2 | Tiêu đề còn lỗi OCR sau P1 (`3. TRIỆU CHUNG`) | So khớp **không dấu** với từ điển; kiểm tra bằng test |
| R3 | Cấp tiêu đề mơ hồ (chữ IN HOA không đánh số giữa mục, vd. `LƯU Ý`) | Đối chiếu mục lục trước; còn mơ hồ → LLM (`classify`) với nhãn đóng; ghi cờ để duyệt |
| R4 | Golden set do mình sinh từ đáp án, có thể "dễ" hơn câu hỏi thật | Ghi rõ người tạo `auto (sách mẫu)`; với sách thật cần người chuyên môn viết hoặc duyệt; **golden set không bao giờ được dùng để huấn luyện** (P7) |
| Q1 | ✅ **Đã duyệt 2026-10-21.** **Quyết định:** mục lục nằm ngoài pilot. P2.1 tự tìm và đọc trang mục lục (chỉ bằng quy tắc, không LLM) | Đề xuất **đồng ý** |
| Q2 | ✅ **Đã duyệt 2026-10-21.** **Quyết định:** đơn vị trích dẫn ở các phase sau là `node_id` của mục/mục con (không phải block) | Đề xuất **đồng ý**: ổn định, có nghĩa với người đọc |

## 9. Lịch sử thay đổi plan

| Ngày | Thay đổi | Lý do |
|---|---|---|
| 2026-10-21 | P2.3 xong. `display_title` lấy từ thân sách (mục lục không được sửa OCR); ID phụ thuộc chữ tiêu đề → chốt cây trước P3, P2.6 ghi sha256 `nodes.jsonl` | Báo cáo P2.3 |
| 2026-10-21 | P2.2 xong. LLM chạy cho mọi tiêu đề tin cậy low (kể cả bệnh ngoài mục lục) để tránh "bệnh giả" như `LƯU Ý`; chương nhận cả dạng mất dấu `CHUONG n` | Báo cáo P2.2 |
| 2026-10-21 | P2.1 xong. Phát hiện: tiêu đề mục lục có thể còn lỗi nhầm ký tự (`Viêrn`, `Cbương`; 9/30 seed) → P2.2 phải so khớp gần đúng, không chỉ so `match_key` | Báo cáo P2.1 |
| 2026-10-21 | Tạo plan. So với plan tổng: tách thêm P2.5 (EV.1) và P2.6 (CLI/gate); P2.2 thêm đối chiếu mục lục; chỉ tiêu đo tự động bằng đáp án | Áp dụng cấu trúc đã hiệu quả ở P1 |
