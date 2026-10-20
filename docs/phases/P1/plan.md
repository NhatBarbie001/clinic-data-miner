# Plan P1: Trích xuất và làm sạch text

> Trạng thái: `Draft`, chờ duyệt
> Ngày tạo: 2026-10-20 · Tham chiếu: [plan.md](../../../plan.md) mục P1 · [problem.md](../../../problem.md) mục 4.1, 5 · Đầu vào từ P0: [gate_report.md](../P0/gate_report.md), [book_profile.md](../../book_profile.md)

## 1. Mục tiêu

Biến lớp text OCR của PDF thành **các block văn bản sạch, đúng thứ tự đọc, truy vết được về trang**, làm đầu vào cho P2 (dựng cấu trúc). Cụ thể:

1. **Không còn rác trang:** header, footer, số trang bị bỏ, nhưng **số trang in được giữ lại** làm metadata.
2. **Đúng đơn vị văn bản:** các dòng bị ngắt được nối thành **đoạn văn** hoặc **gạch đầu dòng**, kể cả khi đoạn bị ngắt qua trang. Tiêu đề đứng riêng. Ô bảng được gom thành **hàng và cột**.
3. **Chữ đúng:** chuẩn hóa Unicode (NFC) và sửa lỗi OCR (mất dấu, sai dấu, nhầm ký tự, dính từ) bằng LLM.
4. **An toàn số liệu:** **không bao giờ tự sửa số, liều, đơn vị.** Nghi ngờ thì gắn cờ và đưa vào hàng đợi cho người duyệt.
5. **Đo được bằng số:** mỗi bước có chỉ tiêu so với đáp án của sách mẫu (`book01.truth.json`).

## 2. Đầu vào / Đầu ra

| | Artifact | Schema | Vị trí |
|---|---|---|---|
| Vào | PDF sách | | `data/raw/book01.pdf` |
| Vào | Phạm vi pilot | `PilotCfg` | `configs/default.yaml` (trang PDF 4–9) |
| Ra | Dòng thô | `Line` (P1.1) | `data/p1_clean/lines.jsonl` |
| Ra | Block sau quy tắc (chưa LLM) | `Block` (P1.3) | `data/p1_clean/blocks_rules.jsonl` |
| Ra | **Block sạch (đầu vào P2)** | `Block` | `data/p1_clean/blocks.jsonl` |
| Ra | Hàng đợi duyệt tay | CSV | `data/p1_clean/review/review_queue.csv` |
| Ra | Đánh giá + báo cáo | JSON / MD | `data/p1_clean/eval.json`, `report.md` |

**Hợp đồng dữ liệu cho P2 (`Block`, SCHEMA_VERSION 1):**

```python
class Block(BaseRecord):
    kind: Literal["heading", "paragraph", "list_item", "table", "caption", "toc_entry", "other"]
    text: str                     # văn bản cuối cùng (sau LLM + duyệt tay)
    text_rules: str               # sau quy tắc, trước LLM (để so sánh, truy vết)
    page_start: int; page_end: int            # số trang PDF
    printed_start: int | None; printed_end: int | None   # số trang in
    line_ids: list[str]           # truy ngược về từng dòng PDF (N3)
    bbox: tuple[float, float, float, float]   # của dòng đầu
    x0: float                     # lề trái (thụt lề), dùng cho P2
    font_size: float              # trung bình theo ký tự
    is_upper: bool                # viết hoa toàn bộ
    numbering: str | None         # "3", "3.1", "CHƯƠNG 1" - đặc trưng tiêu đề cho P2
    rows: list[list[str]] | None  # chỉ với kind="table"
    flags: list[str]              # ocr_suspect, dose_suspect, fix_rejected, nfd_fixed, joined_across_pages...
    fixes: list[Fix]              # từng sửa đổi token: before, after, accepted, reason
    review: Review | None         # quyết định của người duyệt (P1.5)
```

## 3. Thay đổi so với plan tổng (plan.md mục P1)

| Plan tổng | Plan này | Lý do (bằng chứng từ P0) |
|---|---|---|
| P1.3 phát hiện đoạn lỗi → **P1.4 chỉ sửa đoạn bị đánh dấu** | **Gửi mọi block văn bản qua LLM**; phát hiện lỗi dùng để gắn cờ và cho guard | **72% lỗi OCR (mất dấu, sai dấu) không phát hiện được bằng quy tắc** (P0.5). Chỉ sửa đoạn bị đánh dấu sẽ bỏ sót đa số lỗi. Chi phí sửa toàn bộ rất nhỏ: pilot **dưới $0.01**, sách 300 trang **khoảng $0.2–0.5** |
| Guard "số, tên thuốc phải giữ nguyên" ở mức block | Guard **theo từng token**: chấp nhận từng sửa đổi đúng, chỉ từ chối sửa đổi vi phạm | Một block có thể vừa có lỗi dấu cần sửa vừa có liều thuốc; từ chối cả block sẽ mất phần sửa đúng |
| Không có | **Số nghi sai (`5OO mg`) → gắn cờ + gợi ý, không tự sửa**; có **hàng đợi duyệt tay** (P1.5) | Quyết định ở gate P0 và nguyên tắc N10; lỗi liều là rủi ro y khoa |
| "Nối dòng ngắt giữa câu" | **Dựng block** (P1.3): đoạn văn, gạch đầu dòng, tiêu đề, bảng, mục lục | P2 cần biết loại block; bảng cần gom ô thành hàng (book_profile mục 7) |
| `report.html` | `report.md` + `eval.json` (so với đáp án) | Đọc được trên GitHub; có số đo khách quan |
| Duyệt tay 30 block | Duyệt tay **toàn bộ** hàng đợi + đối chiếu tự động với đáp án | Sách mẫu có đáp án nên đo được 100% |

## 4. Kiến trúc

```
data/raw/book01.pdf
   │  P1.1 pdf_reader.read_lines()        - PyMuPDF → Line (NFC, vùng, toạ độ, cỡ chữ)
   ▼
lines.jsonl
   │  P1.2 page_furniture.classify()       - header/footer/số trang → bỏ; số trang in → metadata
   │  P1.3 blocks.build_blocks()           - tiêu đề | đoạn | gạch đầu dòng | bảng | mục lục
   ▼
blocks_rules.jsonl  ── evaluation: so khối với đáp án
   │  P1.4 ocr_fixer.fix_blocks()          - LLM sửa (theo trang) → guard theo token → flags
   ▼
blocks.jsonl ── P1.5 review export/import (CSV) ── P1.6 dm p1 run/eval/report
```

**Module mới trong `src/dataminer/ingest/`:** `pdf_reader.py`, `page_furniture.py`, `blocks.py`, `ocr_fixer.py`, `guards.py`, `review.py`.
**Dùng chung:**
- `core/prompts.py`: nạp prompt có version, theo nguyên tắc N6.
- `evaluation/p1_eval.py`: so với đáp án.

**Refactor:** phần trích dòng và nhận diện header/footer/tiêu đề trong `ingest/survey.py` (P0.5) được **chuyển sang** các module trên. `survey.py` gọi lại các module đó, nên mọi test P0.5 phải vẫn pass mà không sửa test.

## 5. Danh sách task

| Task | Nội dung | Plan chi tiết | Phụ thuộc |
|---|---|---|---|
| **P1.1** | Đọc PDF thành `Line` (NFC, vùng, số trang, lọc pilot) | [P1.1_plan.md](P1.1_plan.md) | P0 |
| **P1.2** | Bỏ header/footer/số trang, ánh xạ số trang in | [P1.2_plan.md](P1.2_plan.md) | P1.1 |
| **P1.3** | Dựng block: tiêu đề, đoạn, gạch đầu dòng, bảng, mục lục; nối qua trang | [P1.3_plan.md](P1.3_plan.md) | P1.2 |
| **P1.4** | Sửa lỗi OCR bằng LLM + guard số liệu theo token | [P1.4_plan.md](P1.4_plan.md) | P1.3 |
| **P1.5** | Hàng đợi duyệt tay (xuất/nhập CSV) | [P1.5_plan.md](P1.5_plan.md) | P1.4 |
| **P1.6** | `dm p1 run/eval`, báo cáo trước/sau, chạy lại xác định, gate P1 | [P1.6_plan.md](P1.6_plan.md) | P1.1–P1.5 |

Thứ tự tuyến tính. Mỗi task tự thêm phần đánh giá của mình vào `evaluation/p1_eval.py`, nên mỗi task có số đo riêng ngay khi xong.

## 6. Cấu hình và prompt mới

```yaml
# configs/default.yaml
p1:
  furniture: {top_zone: 0.09, bottom_zone: 0.09, min_repeat_pages: 2}
  blocks:   {para_gap_ratio: 0.6, bullet_markers: ["-", "•", "–"], join_across_pages: true}
  fix:      {enabled: true, blocks_per_call: 25, max_changed_ratio: 0.35, min_similarity: 0.6}
budget:
  per_task_usd: {fix_ocr: 2.0}    # P1 tối đa $2 (dự kiến pilot dưới $0.01)
```

**Prompt:** `prompts/p1_fix_ocr.md` (version `v1`). Đầu file có front matter: `id`, `version`, `task`, `notes`. Version được ghi vào manifest.

## 7. Ước tính chi phí LLM

| Phạm vi | Lời gọi | Token (vào / ra) | Chi phí |
|---|---|---|---|
| Pilot (6 trang, khoảng 1.050 từ) | khoảng 6 | khoảng 12k / 6k | **dưới $0.01** |
| Sách thật 300 trang (ước tính) | khoảng 300 | khoảng 600k / 300k | **khoảng $0.3** (khoảng $0.6 nếu chạy giờ cao điểm ×2) |

Chạy lại dùng cache nên $0. Chế độ `replay` cho phép tái lập mà không cần API.

## 8. Gate P1 (trên pilot của sách mẫu, đo tự động với đáp án)

| # | Chỉ tiêu | Ngưỡng |
|---|---|---|
| G1 | Header/footer/số trang bị bỏ | **100%**, và **0** dòng thân bài bị bỏ nhầm |
| G2 | Ánh xạ số trang in | đúng **100%** trang |
| G3 | Block dựng lại khớp đáp án (đúng tập dòng) | **≥ 97%** block; **0** block gộp nhầm hai mục/bệnh |
| G4 | Bảng | 1/1 bảng, 4×4 ô đúng vị trí |
| G5 | Tỉ lệ lỗi từ (WER) so với văn bản sạch | trước khoảng 3.8% → **sau ≤ 1.0%** |
| G6 | Lỗi OCR đã cài được sửa | **≥ 80%** (trừ lỗi số liệu, vốn phải được gắn cờ) |
| G7 | Lỗi do LLM **tạo thêm** (từ đúng bị sửa sai) | **≤ 0.3%** số từ |
| G8 | **Số liệu** | **0** số/liều/đơn vị bị thay đổi mà không qua duyệt; **100%** lỗi liều đã cài được gắn cờ `dose_suspect` |
| G9 | Unicode | 100% block ở dạng NFC |
| G10 | Tái lập | Chạy lại: $0, `blocks.jsonl` giống hệt từng byte |
| G11 | Kỹ thuật | ruff, mypy strict, pre-commit, toàn bộ test pass; mỗi task có báo cáo và samples |
| G12 | Duyệt tay | Toàn bộ hàng đợi review đã có quyết định; ghi trong `gate_report.md` |

> Sau khi có **sách thật**: chạy lại P1 trên pilot của sách thật. Các chỉ tiêu G1–G9 lúc đó đo bằng **duyệt tay mẫu** (khoảng 10 trang), vì không có đáp án tự động.

## 9. Rủi ro và câu hỏi cần chủ dự án quyết định

| # | Rủi ro / câu hỏi | Đề xuất |
|---|---|---|
| R1 | LLM "sửa quá tay", viết lại câu hoặc thêm bớt từ | Guard theo token (độ tương đồng, tỉ lệ thay đổi), temperature 0, prompt cấm diễn giải; chỉ tiêu G7 |
| R2 | LLM đổi tên thuốc hoặc thuật ngữ Latin (`Helicobacter`) | Guard bảo vệ token có chữ số, chữ hoa giữa từ, gạch nối, cộng danh sách thuật ngữ cấu hình (`configs/glossary.yaml`) |
| R3 | Sửa dấu sai ngữ cảnh (`hạn`→`bạn` là lỗi nhầm ký tự tạo ra từ có nghĩa) | Gửi theo trang để có ngữ cảnh; đo G6/G7 |
| R4 | Pipeline khớp quá mức với sách mẫu | Ngưỡng nằm trong config; test với nhiều seed; checklist kiểm lại khi có sách thật |
| Q1 | **Quyết định:** gửi mọi block qua LLM (khác plan tổng) | Đề xuất **đồng ý** (mục 3) |
| Q2 | **Quyết định:** lỗi số liệu **không tự sửa**, chỉ gắn cờ kèm gợi ý cho người duyệt | Đề xuất **đồng ý** |
| Q3 | Ai duyệt hàng đợi review ở pilot sách mẫu? | Với sách mẫu, mình duyệt dựa trên đáp án và ghi rõ trong báo cáo. Với sách thật, cần người có chuyên môn |

## 10. Lịch sử thay đổi plan

| Ngày | Thay đổi | Lý do |
|---|---|---|
| 2026-10-20 | Tạo plan | — |
