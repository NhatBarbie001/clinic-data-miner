# Gate report P1: Trích xuất và làm sạch text

> ℹ️ **Đường dẫn trong báo cáo này là bố cục cũ** (trước 2026-10-23). Code đã được sắp xếp lại theo "phần dùng chung + luật riêng từng sách": `ingest/` → `pdf/`, `text/`, `ocrfix/`, `pipeline/`; luật sách mẫu → `books/book01/`; dữ liệu → `data/books/book01/`. Bảng chuyển đầy đủ: [docs/phases/P2R/architecture.md](../P2R/architecture.md) mục 5. Kết quả không đổi (dữ liệu sách mẫu giống hệt từng byte).


> Ngày: 2026-10-21 · Plan: [plan.md](plan.md) · Bằng chứng: [samples/P1.6/](../../../samples/P1.6/)
>
> **Kết luận: ✅ P1 QUA GATE trên pilot sách mẫu** (trang PDF 4–9, 85 block, khoảng 1.000 từ).
> Lưu ý lớn: sách mẫu do chính mình sinh. Xem mục 4 về những gì **phải kiểm lại khi có sách thật**.

## 0. P1 đã xây dựng những gì

### 0.1. Bức tranh chung

P1 biến **lớp chữ OCR thô** trong PDF scan thành **các đoạn văn bản sạch, có cấu trúc, truy vết được**:
- Thô nghĩa là còn header/footer, câu bị ngắt dòng, mất dấu, `5OO mg`.
- Đơn vị đầu ra là **block**: một tiêu đề, một đoạn văn, một gạch đầu dòng, hoặc một bảng.
- Mỗi block biết mình nằm ở trang nào và gồm những dòng PDF nào.
- Chữ đã được sửa lỗi OCR bằng LLM, nhưng **số liệu không bao giờ bị đổi nếu chưa qua người duyệt**.

Kết quả `data/p1_clean/blocks.jsonl` là đầu vào của P2 (dựng cây chương → bệnh → mục).

### 0.2. Sơ đồ luồng dữ liệu

```
 data/raw/book01.pdf  (ảnh scan + lớp chữ OCR ẩn)
        │
        │  P1.1  pdf_reader.read_lines()        đọc từng dòng, chuẩn hóa Unicode, sắp đúng thứ tự đọc
        ▼
 lines.jsonl ─────────── 147 dòng (trang 4–9)
        │
        │  P1.2  page_furniture.strip_furniture() bỏ header/footer/số trang, ghi số trang in
        ▼
 content_lines.jsonl ─── 137 dòng nội dung        furniture.json ── 10 dòng đã bỏ (kèm lý do) + bảng số trang
        │
        │  P1.3  blocks.build_blocks()           nối dòng → đoạn / gạch đầu dòng / tiêu đề / bảng
        ▼
 blocks_rules.jsonl ──── 85 block (chưa sửa chữ)
        │
        │  P1.4  ocr_fixer.OCRFixer  ──► DeepSeek (theo trang) ──► guards.apply_guarded_fix()
        │                                    đề xuất sửa             lọc TỪNG TỪ: chặn đổi số, tên thuốc,
        ▼                                                            dấu câu, thêm/bớt từ, viết lại câu
 blocks_fixed.jsonl ──── 36 sửa chấp nhận, 2 bị chặn (số liệu → chờ người duyệt)
        │
        │  P1.5  review: xuất CSV → người duyệt điền → nhập → apply_decisions()
        ▼                         └─ decisions.jsonl (bền: chạy lại tự áp lại)
 blocks.jsonl ────────── 85 block SẠCH  ──►  P2
        │
        └─ P1.6  dm p1 run / eval / report     chạy cả chuỗi, manifest, đánh giá G1–G9, báo cáo trước/sau
```

### 0.3. Một câu đi qua từng bước (dữ liệu thật của pilot)

**Ví dụ 1: số liệu bị OCR đọc sai** (trang PDF 7, trang in 4)

| Bước | Dữ liệu |
|---|---|
| PDF (lớp OCR) | `- Paracetamol 5OO mg mỗi lần, không quá 3 g mỗi ngày.`, dòng 3, toạ độ x=58, cỡ chữ 10.2 |
| P1.3 block | `list_item`, ký hiệu `-` tách riêng → `Paracetamol 5OO mg mỗi lần, …` |
| P1.4 LLM đề xuất | `5OO` → `500` |
| P1.4 guard | **⛔ chặn** (luật G-num: token có chữ số), giữ `5OO`, gắn cờ `dose_suspect`, lưu gợi ý `500` |
| P1.5 người duyệt | `accept` → `Paracetamol 500 mg mỗi lần, không quá 3 g mỗi ngày.`, cờ `reviewed` |

**Ví dụ 2: gạch đầu dòng bị ngắt qua trang**

| Bước | Dữ liệu |
|---|---|
| Trang 4, dòng 23 | `- Khớp sưng, đau, nóng; về sau có thể biến dạng như bàn tay` (x=58) |
| Trang 5 | Header `Bệnh học nội khoa (sách mẫu)` → P1.2 bỏ (lý do: lặp lại ở 3 trang) |
| Trang 5, dòng 1 | `gió thổi.` (x=64, thụt vào so với dấu `-`) |
| P1.3 block | **1 block** `Khớp sưng, đau, nóng; về sau có thể biến dạng như bàn tay gió thổi.`, trang 4–5, trang in 1–2, cờ `joined_across_pages` |

**Ví dụ 3: lỗi OCR thông thường** được LLM sửa và guard chấp nhận: `viêrn`→`viêm`, `NGUYEN`→`NGUYÊN`, `1à`→`là`, `phảnứng`→`phản ứng`, `Thuộc`→`Thuốc` (ô bảng). Xem [fix_diff.md](../../../samples/P1.4/fix_diff.md).

### 0.4. Mỗi block chứa gì (đầu vào của P2)

```json
{"id": "blk_28c4…", "kind": "list_item", "marker": "-",
 "text": "Paracetamol 500 mg mỗi lần, không quá 3 g mỗi ngày.",      // bản cuối
 "text_rules": "Paracetamol 5OO mg mỗi lần, không quá 3 g mỗi ngày.",// trước khi sửa
 "page_start": 7, "page_end": 7, "printed_start": 4, "printed_end": 4,
 "line_ids": ["ln_…"],                // truy ngược về dòng PDF
 "font_size": 10.2, "x0": 58.0, "is_upper": false, "numbering": null,  // đặc trưng cho P2
 "fixes": [{"before": "5OO", "after": "500", "accepted": false, "rule": "G-num", "suggestion": "500"},
           {"before": "5OO", "after": "500", "accepted": true,  "rule": "review"}],
 "reviews": [{"decision": "accept", "reviewer": "auto-truth (sách mẫu)", …}],
 "flags": ["reviewed"]}
```
Block bảng có thêm `rows` (hàng × cột). Block tiêu đề có `numbering` (`CHƯƠNG 1`, `3`, `3.1`).

### 0.5. File code và chức năng

| File | Task | Chức năng |
|---|---|---|
| [ingest/pdf_reader.py](../../../src/dataminer/ingest/pdf_reader.py) | P1.1 | `read_lines`: đọc lớp chữ PDF thành `Line` (văn bản NFC + bản gốc, toạ độ, cỡ chữ, vùng đầu/thân/chân trang). `reading_order`: gom dòng cùng hàng, sắp trái → phải. `detect_columns`: cảnh báo trang 2 cột. `body_font_size`: cỡ chữ thân bài |
| [ingest/page_furniture.py](../../../src/dataminer/ingest/page_furniture.py) | P1.2 | Tách header/footer/số trang khỏi nội dung (kèm lý do); ánh xạ trang PDF → số trang in (suy ra khi thiếu, phát hiện khi mâu thuẫn) |
| [ingest/blocks.py](../../../src/dataminer/ingest/blocks.py) | P1.3 | Định nghĩa `Block`, `Review`. `classify_line`: tiêu đề / gạch đầu dòng / danh sách số / chú thích / mục lục / thân bài. `build_blocks`: nối dòng (kể cả qua trang), gom bảng (kể cả ô thiếu), nối tiêu đề dài. `heading_signals`: dùng chung với khảo sát |
| [ingest/guards.py](../../../src/dataminer/ingest/guards.py) | P1.4 | **Lớp an toàn**, không dùng LLM: so từng từ giữa bản gốc và bản LLM, áp 6 luật (G-num, G-protect, G-punct, G-sim, G-insdel, G-ratio); ghi mỗi thay đổi thành `Fix` |
| [ingest/ocr_fixer.py](../../../src/dataminer/ingest/ocr_fixer.py) | P1.4 | Gom block theo trang (bảng gửi từng ô), gọi LLM qua `chat_json`, nhắc lại khi thiếu id, ghi tiến độ theo lô (chạy tiếp được), áp guard, gắn cờ phần nghi lỗi còn sót |
| [core/prompts.py](../../../src/dataminer/core/prompts.py) · [prompts/p1_fix_ocr.md](../../../prompts/p1_fix_ocr.md) | P1.4 | Nạp prompt có version (`p1_fix_ocr@v1`), version ghi vào manifest |
| [configs/glossary.yaml](../../../configs/glossary.yaml) | P1.4 | Thuật ngữ LLM không được đổi (thuốc, Latin, đơn vị) |
| [ingest/review.py](../../../src/dataminer/ingest/review.py) | P1.5 | Hàng đợi duyệt (3 mức ưu tiên + mẫu kiểm tra), xuất/nhập CSV cho Excel có kiểm tra, lưu quyết định bền, áp quyết định (phát hiện stale) |
| [ingest/pipeline.py](../../../src/dataminer/ingest/pipeline.py) | P1.6 | `run_p1`: chạy cả chuỗi, ghi 6 file + manifest, chạy tiếp và tái lập |
| [ingest/report.py](../../../src/dataminer/ingest/report.py) | P1.6 | `report.md`: tổng quan, chỉ tiêu, trước/sau theo trang (in đậm từ đã đổi), mục chờ duyệt |
| [cli_p1.py](../../../src/dataminer/cli_p1.py) | P1.6 | Lệnh `dm p1 run / eval / report / review export / review import` |
| [evaluation/p1_eval.py](../../../src/dataminer/evaluation/p1_eval.py) | P1.2–P1.6 | Đo G1–G9 so với đáp án sách mẫu (header/footer, số trang, block, bảng, WER, lỗi đã sửa / chưa sửa / sửa sai, số liệu, NFC). **Không đối chiếu được thì báo không đạt**, không bỏ qua im lặng |
| [devtools/oracle_fix.py](../../../src/dataminer/devtools/oracle_fix.py) | P1.4 | "LLM hoàn hảo" (trả đúng đáp án) làm **đối chứng dương**: tìm ra 3 lỗi của guard/đánh giá trước khi chạy thật |
| [devtools/auto_review.py](../../../src/dataminer/devtools/auto_review.py) | P1.5 | Điền quyết định duyệt từ đáp án, **chỉ cho sách mẫu** (người duyệt ghi `auto-truth`) |
| [core/text_vi.py](../../../src/dataminer/core/text_vi.py) | (P0.5) | Dùng trong P1: NFC, bỏ dấu, kiểm tra âm tiết tiếng Việt hợp lệ |

Cấu hình liên quan nằm trong `configs/default.yaml`, nhóm `p1:` (`furniture`, `blocks`, `fix`) và `budget.per_task_usd.fix_ocr`.

## 1. Đối chiếu từng chỉ tiêu (plan P1, mục 8)

| # | Chỉ tiêu | Ngưỡng | Kết quả | Bằng chứng |
|---|---|---|---|---|
| G1 | Header/footer/số trang bị bỏ | 100%, 0 bỏ nhầm | ✅ **10/10, 0 bỏ nhầm** (cả 3 seed toàn sách) | [p1_eval.txt](../../../samples/P1.6/p1_eval.txt), [P1.2](P1.2_report.md) |
| G2 | Số trang in | 100% | ✅ **6/6**; có suy ra khi thiếu, phát hiện khi mâu thuẫn | như trên |
| G3 | Block đúng tập dòng; 0 gộp nhầm | ≥ 97% | ✅ **85/85 (100%)**, 0 gộp nhầm; **24/24 sách** đều 100% | [P1.3](P1.3_report.md) |
| G4 | Bảng | 4×4 đúng | ✅ **4×4**, ô lỗi liều đúng vị trí | như trên |
| G5 | WER | ≤ 1% | ✅ **4.08% → 0.50%** (LLM) **→ 0.30%** (sau duyệt) | [P1.4](P1.4_report.md), [P1.5](P1.5_report.md) |
| G6 | Lỗi đã cài được sửa | ≥ 80% | ✅ **35/38 = 92%**. Chưa sửa: `dien`, `CHUNG`, `độ` (đều là từ có nghĩa); **1 sửa sai** (`kinh diễn`) | [ocr_eval.txt](../../../samples/P1.4/ocr_eval.txt) |
| G7 | Từ đúng bị sửa sai | ≤ 0.3% | ✅ **0** | như trên |
| G8 | Số liệu | 0 đổi khi chưa duyệt; 2/2 gắn cờ | ✅ Trước duyệt: **giữ nguyên + gắn cờ + gợi ý**. Sau duyệt: **sửa đúng qua người duyệt** (`500`, `1`) | [review_applied.md](../../../samples/P1.5/review_applied.md) |
| G9 | NFC | 100% | ✅ | [p1_eval.txt](../../../samples/P1.6/p1_eval.txt) |
| G10 | Tái lập | $0, giống hệt | ✅ Chạy lại, và replay + `--force`: **cùng sha256**, 0 lời gọi API | [p1_run_again.txt](../../../samples/P1.6/p1_run_again.txt) |
| G11 | Kỹ thuật | Mọi kiểm tra pass; báo cáo + samples | ✅ ruff, mypy strict (44 file), pre-commit; **393 test + 3 live**; 6/6 task có báo cáo và samples | [quality_checks.txt](../../../samples/P1.6/quality_checks.txt) |
| G12 | Duyệt tay | 100% hàng đợi có quyết định | ✅ 2/2 mục số liệu + 4/4 mục kiểm tra mẫu. ⚠️ Người duyệt là **auto-truth (sách mẫu)** | [review_cli.txt](../../../samples/P1.6/review_cli.txt) |

**Chạy thật với DeepSeek: 4 lần độc lập** (P1.4 chạy chính, 2 test live sửa OCR, 1 test live trọn P1), lần nào cũng đạt.

## 2. Tổng kết P1

| Hạng mục | Số liệu |
|---|---|
| Task | 6/6 hoàn thành (P1.1–P1.6), mỗi task có plan, báo cáo, samples, commit |
| Test | **393 offline + 3 live**. Mới trong P1: P1.1: 12 · P1.2: 23 · P1.3: 36 · P1.4: 37 · P1.5: 18 · P1.6: 13 |
| Mutation check | **37 đột biến**, tất cả bị bắt. 4 đột biến ban đầu sống sót đã dẫn tới thêm test |
| Lỗi thật tìm thấy và sửa | **22** (liệt kê ở mục 7 các báo cáo task). Nổi bật: guard từ chối nhầm ô bảng làm mất cờ lỗi liều; `mg`→`g` lọt guard; đánh giá lặng lẽ báo "đạt" khi không đối chiếu được |
| **Chi phí LLM P1** | Sổ chính: **$0.0028**. Cộng 4 lần chạy thật trong sổ tạm của test live: **tổng khoảng $0.015**. Ngân sách `fix_ocr`: $2 |
| Đầu ra cho P2 | `data/p1_clean/blocks.jsonl`: 85 block (27 tiêu đề, 7 đoạn, 49 gạch đầu dòng, 1 chú thích, 1 bảng) có `numbering`, `is_upper`, `font_size`, `x0`, truy vết về dòng và trang |

**Lệnh mới:** `dm p1 run | eval | report | review export [--audit] | review import`.

## 3. Phát hiện quan trọng mang sang P2

1. **Block đã có đủ đặc trưng tiêu đề** (`numbering`, `is_upper`, `font_size`). P2 chỉ cần quyết định cấp: chương / bệnh / mục / mục con, và ánh xạ `section_type`.
2. **Tiêu đề có thể vẫn còn lỗi OCR** sau P1 (`3. TRIỆU CHUNG`: LLM không sửa vì "CHUNG" là từ có nghĩa). P2 khi ánh xạ tên mục **phải so không dấu** (đúng như book_profile mục 2).
3. **Bảng đã có `rows`.** P2/P4 dùng trực tiếp, không cần phân tích lại.
4. **Số trang in** có sẵn trong mỗi block, phục vụ trích dẫn ở P5.

## 4. ⚠️ Rủi ro và tồn đọng

| Mục | Mức | Hành động |
|---|---|---|
| **Chưa có sách thật**: mọi chỉ tiêu đo trên sách mẫu tự sinh | **Cao** | Khi có sách: `dm survey` → cập nhật `book_profile.md` → `dm p1 run` → **duyệt tay khoảng 10 trang** `report.md` (không có đáp án tự động) → `dm p1 review export --audit 0.05` để ước lượng tỉ lệ sửa sai |
| Lỗi tạo ra **từ có nghĩa** (khoảng 8% lỗi đã cài) và **sửa sai** không có tín hiệu nào | Trung bình | Mẫu kiểm tra `--audit` chỉ ước lượng. Nếu tỉ lệ cao: prompt v2, hoặc gửi kèm ngữ cảnh rộng hơn |
| Duyệt tay hiện là auto-truth | Trung bình | Sách thật cần người có chuyên môn y khoa cho hàng đợi `1-SỐ LIỆU` |
| Bảng có ô nhiều dòng, bảng qua 2 trang, sách 2 cột: chưa xử lý | Trung bình | Kiểm khi có sách thật (`dm survey` cảnh báo trang 2 cột) |
| `judge` cùng model với `qa`/`datagen` (từ P0.2) | Trung bình | Quyết định trước P5 |
| Thời gian test khoảng 69 giây | Thấp | Theo dõi |

## 5. Đề xuất bước tiếp theo

**P2: Dựng cấu trúc tài liệu** (plan.md mục P2). Đầu vào: `blocks.jsonl` đã sạch. Đầu ra: cây Chương → Bệnh → Mục → Mục con, kèm `section_type`.

Đáp án sách mẫu đã có sẵn `headings` với `level` và `section_type`, nên P2 cũng đo được bằng số. Chỉ tiêu gate P2 (plan.md): số bệnh khớp mục lục 100%, mục ánh xạ đúng ≥ 95%, `other` < 5%.

Bước đầu tiên: viết `docs/phases/P2/plan.md` để chủ dự án duyệt.
