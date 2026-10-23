# Gate report P2: Dựng cấu trúc tài liệu

> ℹ️ **Đường dẫn trong báo cáo này là bố cục cũ** (trước 2026-10-23). Code đã được sắp xếp lại theo "phần dùng chung + luật riêng từng sách": `ingest/` → `pdf/`, `text/`, `ocrfix/`, `pipeline/`; luật sách mẫu → `books/book01/`; dữ liệu → `data/books/book01/`. Bảng chuyển đầy đủ: [docs/phases/P2R/architecture.md](../P2R/architecture.md) mục 5. Kết quả không đổi (dữ liệu sách mẫu giống hệt từng byte).


> Ngày: 2026-10-22 · Plan: [plan.md](plan.md) · Bằng chứng: [samples/P2.6/](../../../samples/P2.6/)
>
> **Kết luận: ✅ P2 QUA GATE trên pilot sách mẫu** (trang PDF 4–9: 2 chương, 3 bệnh, 22 mục và mục con, 85 block). **0 lời gọi LLM, $0.**
> Lưu ý lớn: sách mẫu do chính mình sinh và **rất đều**. Các đường xử lý mơ hồ (LLM, khớp gần, kế thừa, duyệt CSV) **chỉ được kiểm bằng dữ liệu tự dựng và LLM giả lập**. Xem mục 4.

## 0. P2 đã xây dựng những gì

### 0.1. Bức tranh chung

P2 biến **danh sách block phẳng** của P1 thành **cây tài liệu**: Sách → Chương → Bệnh → Mục → Mục con.
- Mỗi nút biết cấp của nó, **loại mục chuẩn** (`definition`, `cause`, `symptom`, `treatment`…), nội dung riêng của nó, phạm vi trang PDF và trang in.
- Mỗi nút có **ID ổn định** (hash của đường dẫn tiêu đề), dùng làm **khóa trích dẫn** cho mọi phase sau.

Kèm theo là **bộ 30 câu hỏi chuẩn** có nguồn trỏ tới nút. Đây là thước đo cho P3 (tìm kiếm), P5 (hỏi đáp) và P7 (chống rò rỉ dữ liệu huấn luyện).

| Phase sau | Dùng gì từ P2 |
|---|---|
| P3 tìm kiếm | Chia đoạn theo nút; metadata `disease`, `section_type`; golden để đo recall |
| P4 trích xuất | Lấy nguyên nhân / triệu chứng / điều trị theo `section_type`; ma trận cho biết trường nào có thể trống |
| P5 hỏi đáp | Trích dẫn `(Bệnh › Mục, tr.in X)` theo `node_id`; golden để chấm |
| P7 dữ liệu huấn luyện | Sinh câu hỏi theo loại mục; loại câu gần trùng golden |

### 0.2. Sơ đồ luồng dữ liệu

```
 data/raw/book01.pdf ──► P2.1 toc.py ──────────► toc.json
   (trang mục lục PDF 3,   tự tìm trang có chấm dẫn,    5 mục: 2 chương + 3 bệnh, tr.in → tr.PDF
    nằm ngoài pilot)       cấp theo "Chương n" + thụt lề  (giữ nguyên văn OCR: "Bệnh tiêu hỏa")
                                                │
 data/p1_clean/blocks.jsonl ── 85 block         │
        │                                       ▼
        ├─► P2.2 heading_levels.py ─────► heading_levels.jsonl   27 tiêu đề → cấp + lý do + tin cậy
        │     lớp 1 quy tắc (đánh số, IN HOA, cỡ chữ) → 22
        │     lớp 2 mục lục (khớp không dấu / khớp gần) → 5
        │     lớp 3 LLM (chỉ tiêu đề tin cậy thấp)    → 0
        ▼
     P2.3 tree_builder.py ──────────────► cây 28 nút (ngăn xếp; mỗi block thuộc ĐÚNG 1 nút;
        │                                  bất biến G6 kiểm ngay khi dựng, vi phạm → lỗi)
        ▼
     P2.4 section_mapper.py ────────────► section_type cho 22 mục
        │     từ điển configs/section_map.yaml → khớp gần → kế thừa mục cha → LLM
        │     (đề xuất → CSV → người duyệt → ghi thêm vào từ điển: lần sau không gọi LLM)
        ▼
 nodes.jsonl · tree.json · tree.md ──► P3 / P4 / P5 / P7
        │
        ├─► P2.5 golden.py ─────────────► eval/golden_qa_v1.jsonl   30 câu (commit, đã khóa)
        │
        └─► P2.6 dm p2 run / eval / report → manifest · eval.json (G1–G7) · tree_report.md
```

### 0.3. Một bệnh đi qua từng bước (dữ liệu thật của pilot)

| Bước | Dữ liệu |
|---|---|
| Mục lục (PDF 3) | `Viêm khớp dạng thấp ........ 1` (x0 = 62, thụt vào) → **disease**, tr.in 1 → PDF 4 |
| Block tiêu đề (P1) | `VIÊM KHỚP DẠNG THẤP`, cỡ 13.4, IN HOA, không đánh số |
| P2.2 lớp 1 | ứng viên **disease** (medium): "IN HOA, không đánh số, cỡ 13.4 ≥ thân bài 10.5 + 1.5" |
| P2.2 lớp 2 | khớp mục lục `viem khop dang thap` → **disease (high)** |
| P2.3 cây | `Chương 1. Bệnh cơ xương khớp › Viêm khớp dạng thấp`: 9 mục và mục con, 32 block, PDF 4–5, tr.in 1–2 |
| P2.4 loại mục | `3. TRIỆU CHỨNG` → `trieu chung` → **symptom**; `3.2. Cận lâm sàng` → **paraclinical**; `2.1. Yếu tố nguy cơ` → **risk_factor** |
| P2.5 câu hỏi | "Triệu chứng lâm sàng của viêm khớp dạng thấp là gì?" → nguồn `… › Triệu chứng › Lâm sàng`, 4 ý bắt buộc |

**Một nút trong `nodes.jsonl`:**

```json
{"id": "nd_7ec35cbe6c91f45a", "level": "subsection", "parent_id": "nd_d2d9…", "order": 0,
 "title": "3.1. Lâm sàng", "display_title": "Lâm sàng", "numbering": "3.1",
 "section_type": "symptom", "section_source": "map",
 "path": ["Chương 1. Bệnh cơ xương khớp", "Viêm khớp dạng thấp", "Triệu chứng", "Lâm sàng"],
 "block_ids": ["blk_…", "blk_…", "blk_…", "blk_…"],
 "text": "- Viêm nhiều khớp nhỏ ở bàn tay …\n- Cứng khớp buổi sáng kéo dài trên 1 giờ.\n- Khớp sưng, đau, nóng; về sau có thể biến dạng như bàn tay gió thổi.\n- Toàn thân: …",
 "page_start": 4, "page_end": 5, "printed_start": 1, "printed_end": 2, "flags": []}
```

### 0.4. File code và chức năng

| File | Task | Chức năng |
|---|---|---|
| [structure/toc.py](../../../src/dataminer/structure/toc.py) | P2.1 | Tự tìm trang mục lục, tách dòng (nhiều kiểu chấm dẫn, tiêu đề ngắt 2 dòng), cấp theo mẫu chữ + thụt lề, đổi tr.in → PDF; `norm_title`, `match_key` (không dấu, chịu dính từ) |
| [structure/heading_levels.py](../../../src/dataminer/structure/heading_levels.py) | P2.2 | 3 lớp: quy tắc → mục lục (kể cả khớp gần) → LLM; kiểm tra đánh số (`numbering_gap`); mỗi quyết định kèm lý do |
| [structure/tree_builder.py](../../../src/dataminer/structure/tree_builder.py) | P2.3 | `Node`; dựng cây bằng ngăn xếp (phần đầu, sách không chia chương, mục con mồ côi, tiêu đề "other"); ID ổn định; `check_invariants` (G6); `tree.json`, `tree.md` |
| [structure/section_mapper.py](../../../src/dataminer/structure/section_mapper.py) · [configs/section_map.yaml](../../../configs/section_map.yaml) | P2.4 | 13 loại mục; tra từ điển → khớp gần → kế thừa → LLM (mỗi tên lạ hỏi 1 lần); vòng duyệt CSV ghi thêm vào từ điển |
| [structure/golden.py](../../../src/dataminer/structure/golden.py) · [eval/](../../../eval/) | P2.5 | Sinh 30 câu từ văn bản sạch; mỗi câu có luật `check` để máy tính lại đáp án; `validate_golden` (G7); quy tắc cách ly và version |
| [structure/pipeline.py](../../../src/dataminer/structure/pipeline.py) · [structure/report.py](../../../src/dataminer/structure/report.py) | P2.6 | `run_p2` có manifest; `tree_report.md` gồm 5 phần |
| [evaluation/p2_eval.py](../../../src/dataminer/evaluation/p2_eval.py) | P2.1–P2.6 | Đo G1–G7 so với đáp án sách mẫu; **không đối chiếu được thì báo không đạt** |
| [cli_p2.py](../../../src/dataminer/cli_p2.py) | P2.1–P2.6 | `dm p2 run / eval / report`, và các lệnh lẻ `toc / headings / tree / sections map·export·import / golden [--check]` |
| [prompts/p2_classify_heading.md](../../../prompts/p2_classify_heading.md) · [prompts/p2_classify_section.md](../../../prompts/p2_classify_section.md) | P2.2, P2.4 | Prompt nhãn đóng (chỉ dùng khi mơ hồ; pilot: 0 lần) |

Cấu hình nằm trong `configs/default.yaml`, nhóm `p2:` (`toc`, `headings`, `sections`), và `budget.per_task_usd.classify`.

## 1. Đối chiếu từng chỉ tiêu (plan P2, mục 7)

| # | Chỉ tiêu | Ngưỡng | Kết quả | Bằng chứng |
|---|---|---|---|---|
| G1 | Mục lục: số mục, tiêu đề, cấp, số trang in | 100% (5/5) | ✅ **5/5**; quét **30/30 seed** (kể cả `Cbương 2` nhận ra bằng thụt lề) | [p2_eval.txt](../../../samples/P2.6/p2_eval.txt), [P2.1](P2.1_report.md) |
| G2 | Cấp tiêu đề | 100% (27/27) | ✅ **27/27** (quy tắc 22, mục lục 5, LLM 0); **30/30 seed** với tiêu đề chưa sửa OCR | như trên, [P2.2](P2.2_report.md) |
| G3 | Số bệnh khớp mục lục + trang bắt đầu | 100% (3/3) | ✅ **3/3**, 0 thừa / thiếu | [P2.3](P2.3_report.md) |
| G4 | Nội dung gắn đúng nút; 0 block mồ côi | ≥ 99% dòng | ✅ **110/110 dòng (100%)**, 0 mồ côi; **30/30 seed** | như trên |
| G5 | `section_type` đúng; `other` < 5% | ≥ 95% | ✅ **22/22 (100%)**, `other` 0%; **30/30 seed** | [P2.4](P2.4_report.md) |
| G6 | Bất biến cây | 100% | ✅ 0 vi phạm. Kiểm **ngay khi dựng** (block thuộc đúng 1 nút, ID duy nhất, cha ⊇ con, thứ tự đọc, nút rỗng có cờ) | [P2.3](P2.3_report.md) |
| G7 | Golden set v1 | 30 câu (20/5/5); 100% nguồn và trích dẫn hợp lệ | ✅ **30 câu**, 0 lỗi, **0 cảnh báo** (mọi trích dẫn khớp nguyên văn) | [golden_validation.txt](../../../samples/P2.5/golden_validation.txt), [P2.5](P2.5_report.md) |
| G8 | Tái lập | Chạy lại giống hệt từng byte; $0 | ✅ **6/6 file ra cùng sha256**; `nodes.jsonl` trùng cả kết quả chạy từng bước ở P2.4 | [p2_run_again.txt](../../../samples/P2.6/p2_run_again.txt) |
| G9 | Kỹ thuật | ruff, mypy, pre-commit, mọi test pass; mỗi task có báo cáo + samples | ✅ ruff, mypy strict (53 file), pre-commit; **509 test + 3 live**; 6/6 task có báo cáo và samples | [quality_checks.txt](../../../samples/P2.6/quality_checks.txt) |

> Plan tổng có chỉ tiêu "duyệt tay 10 bệnh". Pilot chỉ có 3 bệnh và có đáp án, nên G2–G5 được đo tự động 100%. **Với sách thật phải duyệt tay `tree_report.md` khoảng 10 bệnh.**

## 2. Tổng kết P2

| Hạng mục | Số liệu |
|---|---|
| Task | 6/6 hoàn thành (P2.1–P2.6), mỗi task có plan (kèm ví dụ trực quan), báo cáo, samples, commit |
| Test | **509 offline + 3 live**. Mới trong P2: P2.1: 30 · P2.2: 21 · P2.3: 23 · P2.4: 21 · P2.5: 13 · P2.6: 8 (tổng **116**) |
| Mutation check | **96 đột biến**, tất cả bị bắt. Lần chạy đầu có 3 đột biến sống sót (P2.1 M11, P2.3 T17, P2.4 E2), cả 3 đều dẫn tới siết test |
| Quét nhiều seed | Mỗi task P2.1–P2.5 quét **30 seed** sách mẫu: **30/30** ở mọi task |
| Lỗi thật tìm thấy và sửa | **8**. `CHUONG` (mất dấu) không được nhận là chương; đệ quy vô hạn khi ID trùng; CLI in "85/85" bằng phép chia số cho chính nó; đếm lời gọi LLM theo chi phí; luật số liệu để lọt `5OO` (vì `"5" in "500"`); code chết trong `quote_status`; báo cáo dùng kết quả ghép mục lục cũ; script mẫu P2.1 lọt lint (repo chưa cài git hook) |
| **Chi phí LLM P2** | **$0**: không có lời gọi nào. Ngân sách `classify`: $0.5 |
| Đầu ra cho P3/P4 | `data/p2_tree/nodes.jsonl` (28 nút) · `eval/golden_qa_v1.jsonl` (30 câu) · [tree_report.md](../../../samples/P2.6/tree_report.md) |

**Lệnh mới:** `dm p2 run | eval | report | toc | headings | tree | sections map·export·import | golden [--check]`.

## 3. Phát hiện quan trọng mang sang P3/P4

1. **Đơn vị trích dẫn là `node_id`** (quyết định Q2). ID = hash của `path` tiêu đề, nên ổn định khi nội dung đổi, **nhưng đổi khi chữ của tiêu đề đổi**. Ví dụ thật: `Thoái hóa khớp gối › Triệu chung` (lỗi OCR mà P1 chưa sửa). → **Chốt cây trước P3**; mọi lần chạy lại P1 hoặc duyệt thêm phải chạy lại P2 và `dm p2 golden --check`.
2. **Ma trận bệnh × loại mục:** `risk_factor`, `paraclinical`, `complication` chỉ có ở một số bệnh; `pathophysiology`, `differential_diagnosis`, `prognosis` không bệnh nào có. Schema P4 phải cho phép các trường này **trống**, không được bịa.
3. **Một nút có thể chứa bảng** (`6. Điều trị` của bệnh 3: gạch đầu dòng + chú thích + `Bảng 2.1`). Khi chia đoạn ở P3, không được cắt rời bảng khỏi chú thích của nó.
4. **Câu hỏi bẫy loại mục** trong golden ("bệnh nào điều trị bằng NSAID"): P3/P5 tìm theo từ khóa trơn sẽ trả cả viêm loét dạ dày, và trả lời sai. Đây là phép thử cho bộ lọc `section_type`.
5. **Số liệu chưa duyệt chặn cả chuỗi**: nút còn `5OO mg` thì golden không sinh được (test đầu-cuối P2.6). Đây là hành vi mong muốn, phải giữ.

## 4. ⚠️ Rủi ro và tồn đọng

| Mục | Mức | Hành động |
|---|---|---|
| **Chưa có sách thật.** Sách mẫu rất đều: mọi bệnh cùng khuôn, mọi tên mục có trong từ điển, mọi bệnh có trong mục lục | **Cao** | Khi có sách: `dm p2 run` → đọc `tree_report.md` (phần 2 và 4) → duyệt tay khoảng 10 bệnh → `dm p2 sections export` |
| **Đường LLM của P2 chưa từng chạy thật** (chỉ LLM giả lập) | Trung bình | Lần đầu chạy sách thật, xem kỹ các nút có cờ `level_from_llm` / `section_type_from_llm` |
| Đánh số `I.`, `A.`, `a)`; mục lục 3 tầng (Phần → Chương → Bài); tên bệnh viết chữ thường | Trung bình | Thêm mẫu vào quy tắc khi gặp (đã ghi ở báo cáo P2.1, P2.2) |
| ID phụ thuộc chữ của tiêu đề (mục 3.1) | Trung bình | Chốt cây; nếu ID đổi thì tạo golden v2, không sửa im lặng |
| Golden v1 sinh theo mẫu, dễ hơn câu hỏi thật | Trung bình | Golden v2 cần người chuyên môn viết, trước khi chạy toàn sách |
| `judge` cùng model với `qa`/`datagen` (từ P0.2) | Trung bình | Quyết định trước P5 |
| Repo chưa cài git hook pre-commit (một lần lint lọt vào commit P2.1) | Thấp | Chạy `pre-commit run --all-files` trước mỗi commit; có thể `pre-commit install` |

## 5. Đề xuất bước tiếp theo

**P3: Chỉ mục và tìm kiếm** (plan.md mục P3).
- Đầu vào: `nodes.jsonl` (28 nút, có `section_type`) và `eval/golden_qa_v1.jsonl`.
- Chỉ tiêu có sẵn để đo ngay: **recall@k của nút nguồn** trên 25 câu có nguồn, cộng 5 câu từ chối (không được trả đoạn nào có điểm cao).

Bước đầu tiên: viết `docs/phases/P3/plan.md` để chủ dự án duyệt.
