# Sắp xếp lại code trước P2R: tách "phần dùng chung" và "luật riêng từng sách"

> Trạng thái: `Đã duyệt` 2026-10-23 · IASP là **sách chính** · repo private · Ngày: 2026-10-23 · Đi kèm: [plan.md](plan.md)

## 1. Vấn đề của cách sắp xếp hiện tại

Code hiện chia theo **giai đoạn**: `ingest/` (P1), `structure/` (P2). Trong mỗi thư mục, **phần dùng chung** và **luật chỉ đúng với sách mẫu** nằm **lẫn trong cùng một file**:

| File hiện tại | Phần dùng chung (mọi sách) | Phần chỉ đúng với sách mẫu |
|---|---|---|
| `ingest/pdf_reader.py` | Đọc dòng, cỡ chữ, chữ đậm, vị trí | **Thứ tự đọc theo hàng ngang**: sai với sách 2 cột |
| `ingest/page_furniture.py` | Tìm dòng lặp lại ở lề, ánh xạ trang in | **Mẫu số trang** (`– 1 –`, `Trang 12`); không nhận `Page 41` |
| `ingest/blocks.py` | Định nghĩa `Block`; ghép dòng → đoạn; nhận bảng | **Luật "đâu là tiêu đề"** (IN HOA, có số `3.`); không xét chữ đậm |
| `structure/toc.py` | `TocEntry`, so khớp không dấu | **Cách đọc mục lục** (`Tên ..... 5`) |
| `structure/heading_levels.py` | `HeadingDecision`; đối chiếu mục lục; hỏi AI khi mơ hồ | **Luật cấp tiêu đề** (`CHƯƠNG n`, IN HOA + cỡ chữ = bệnh) |
| `structure/golden.py` | Kiểm tra bộ câu hỏi chuẩn | **Sinh câu hỏi từ đáp án sách mẫu**, mẫu câu tiếng Việt |
| `configs/section_map.yaml` | | Từ điển tên mục **tiếng Việt** |

Hệ quả: muốn thêm luật cho IASP thì phải chèn `if sách == "iasp"` vào giữa các file này. Code sẽ rối dần theo số sách, và dễ làm hỏng sách mẫu.

## 2. Nguyên tắc sắp xếp mới

1. **Mỗi sách = một thư mục luật** trong `src/dataminer/books/<tên sách>/`. Mọi thứ "chỉ đúng với cuốn này" nằm ở đây, kể cả cấu hình và từ điển.
2. **Phần dùng chung không biết sách nào đang chạy.** Nó chỉ nhận dữ liệu theo **"hợp đồng dữ liệu"** chung (`Line`, `Block`, `Node`…) và gọi luật qua **một giao diện duy nhất**.
3. **Chạy P1, P2 giống nhau cho mọi sách:** cùng lệnh, cùng file đầu ra, cùng báo cáo. Chỉ khác ở chỗ gọi luật của sách nào.
4. **Sắp xếp lại không được đổi kết quả:** dữ liệu sách mẫu sau khi sắp xếp phải **giống hệt từng byte** so với trước.

## 3. Cây thư mục đề xuất

```
src/dataminer/
├─ core/             (giữ nguyên) cấu hình, gọi AI, cache, chi phí, manifest, đọc/ghi file, tiện ích tiếng Việt
│
├─ model/            MỚI: "hợp đồng dữ liệu" giữa các bước (chỉ định nghĩa kiểu dữ liệu, không có logic)
│   ├─ line.py         Line           một dòng chữ PDF: chữ, vị trí, cỡ chữ, đậm, trang
│   ├─ block.py        Block, Fix, Review   một đoạn / tiêu đề / gạch đầu dòng / bảng
│   ├─ toc.py          TocEntry, TocResult  một mục của mục lục
│   └─ tree.py         HeadingDecision, Node   cấp tiêu đề; nút của cây
│
├─ pdf/              MỚI (tách từ ingest/): công cụ PDF dùng chung
│   ├─ reader.py       đọc dòng (KHÔNG quyết định thứ tự đọc)
│   ├─ layout.py       thứ tự đọc: theo hàng (1 cột) | theo cột (2 cột); dò khe giữa cột
│   └─ furniture.py    bỏ đầu/chân trang lặp lại; ánh xạ trang in (mẫu số trang do luật sách cung cấp)
│
├─ text/             MỚI (tách từ ingest/blocks.py): ghép dòng → đoạn, nhận bảng
│   └─ blocks.py       build_blocks(lines, classify_line)   ← "dòng nào là tiêu đề" do luật sách truyền vào
│
├─ ocrfix/           (tách từ ingest/) sửa OCR bằng AI: bật/tắt theo sách (IASP: tắt)
│   ├─ fixer.py · guards.py · review.py
│
├─ structure/        dùng chung cho mọi sách
│   ├─ tree_builder.py   dựng cây từ block + cấp tiêu đề; ID ổn định; kiểm bất biến
│   ├─ toc_match.py      so khớp tiêu đề ↔ mục lục (không dấu, khớp gần)
│   ├─ sections.py       cơ chế gán loại mục (từ điển + duyệt CSV); danh sách loại mục chung
│   └─ report.py         tree.md, tree_report.md
│
├─ books/            MỚI: LUẬT RIÊNG TỪNG SÁCH
│   ├─ base.py           giao diện BookRules (mục 4) + bộ luật mặc định
│   ├─ registry.py       tên sách → bộ luật (book01 → Book01Rules, iasp → IaspRules)
│   ├─ book01/           sách mẫu tiếng Việt: CHUYỂN NGUYÊN luật hiện có vào đây
│   │   ├─ rules.py        phân loại dòng (IN HOA, số 3.), cấp tiêu đề (CHƯƠNG n…), mục lục chấm dẫn
│   │   └─ golden.py       sinh 30 câu hỏi từ đáp án sách mẫu (mẫu câu tiếng Việt)
│   └─ iasp/             sách IASP (viết trong P2R)
│       ├─ rules.py        ghép các luật bên dưới
│       ├─ layout.py       L4: 2 cột, dòng vắt ngang
│       ├─ headings.py     L5–L10: GROUP La Mã, hội chứng + mã, tên mục in đậm
│       ├─ toc.py          L12: mục lục "tên ↵ số trang"
│       └─ attrs.py        L8, L11: chuẩn hóa mã hội chứng, tách mã IASP
│
├─ pipeline/         MỚI (từ ingest/pipeline.py, structure/pipeline.py): chạy P1, P2 cho MỌI sách
│   ├─ p1.py           đọc → bỏ đầu/chân trang → block → (sửa OCR nếu sách bật) → blocks.jsonl
│   └─ p2.py           mục lục → cấp tiêu đề → cây → loại mục → nodes.jsonl (+ manifest)
│
├─ evaluation/
│   ├─ truth/          so với ĐÁP ÁN (chỉ sách mẫu có): p1_eval.py, p2_eval.py (G1–G9 hiện có)
│   ├─ checks.py       MỚI: kiểm tra KHÔNG cần đáp án cho sách thật (A1–A8 của plan P2R)
│   └─ golden.py       kiểm tra bộ câu hỏi chuẩn (dùng chung)
│
├─ survey/           (từ ingest/survey.py, pilot.py) khảo sát sách mới: dm survey
├─ cli/              (từ cli_*.py) main.py, p1.py, p2.py, llm.py, runs.py, survey.py
│                      + tùy chọn chung: dm --book <tên> …
└─ devtools/         (giữ) sinh sách mẫu, AI giả lập hoàn hảo, tự duyệt: chỉ dùng cho test

configs/
├─ default.yaml, models.yaml          chung
└─ books/
    ├─ book01/  book.yaml · section_map.yaml · glossary.yaml      (chuyển từ configs/)
    └─ iasp/    book.yaml · section_map.yaml                      (mới)

data/books/<tên sách>/   raw/ · p1_clean/ · p2_tree/        (git bỏ qua; mỗi sách một thư mục)
eval/<tên sách>/golden_qa_v1.jsonl                          (eval/golden_qa_v1.jsonl → eval/book01/)
prompts/                                                    (giữ nguyên)

tests/
├─ unit/          phần dùng chung: core, model, pdf, text, structure, pipeline
├─ books/book01/  test so với đáp án sách mẫu (chuyển các test hiện có)
└─ books/iasp/    test luật IASP bằng dòng tự dựng (không cần file sách)
                  + test trên PDF thật nếu máy có file (tự bỏ qua nếu không có)
```

## 4. Giao diện "bộ luật sách" (`books/base.py`)

Mỗi sách cung cấp một bộ luật trả lời **6 câu hỏi**. Phần dùng chung chỉ hỏi qua đúng giao diện này:

| Câu hỏi | Hàm | Sách mẫu trả lời | IASP trả lời |
|---|---|---|---|
| 1. Đọc trang nào? | `scope(cfg)` | pilot PDF 4–9 | Part II, PDF 53–222 (pilot 137–143) |
| 2. Đọc theo thứ tự nào? | `order_lines(page_lines)` | theo hàng (1 cột) | theo cột (L4) |
| 3. Dòng nào là số trang / đầu trang? | `page_number(text)` | `– 1 –`, `Trang 12` | `Page 121`, `xvi` |
| 4. Dòng nào là tiêu đề, dòng nào là nội dung? | `classify_line(line)` | IN HOA, có số `3.` | chữ đậm (L7, L10) |
| 5. Mục lục ở đâu, đọc thế nào? | `read_toc(pdf)` | chấm dẫn `.....` | "tên ↵ số" (L12) |
| 6. Tiêu đề thuộc cấp nào? Có thuộc tính gì? | `heading_level(block, toc)` · `node_attrs(node)` | `CHƯƠNG n` / IN HOA to / `3.` / `3.1` | GROUP La Mã / hội chứng + mã / tên mục đậm; mã XI-1, mã IASP |

Kèm theo là các **thiết lập** trong `configs/books/<sách>/book.yaml`: file PDF, có sửa OCR không, từ điển tên mục, trang mục lục…

`base.py` có sẵn **bộ luật mặc định** (chính là luật hiện tại). Một sách mới chỉ cần viết lại những câu hỏi mà nó khác.

**Thay đổi nhỏ ở hợp đồng dữ liệu:** `Node` thêm trường `attrs` (thuộc tính tự do theo sách, ví dụ `{"code": "XI-1", "iasp_codes": "102.X4b; 202.X4b", "group": "E. Local syndromes…"}`). Sách mẫu để trống, nên **ID và nội dung không đổi**.

## 5. Bảng chuyển file (cũ → mới)

| Cũ | Mới |
|---|---|
| `ingest/pdf_reader.py` | `model/line.py` (Line) + `pdf/reader.py` + `pdf/layout.py` (thứ tự đọc theo hàng) |
| `ingest/page_furniture.py` | `pdf/furniture.py` (mẫu số trang lấy từ luật sách) |
| `ingest/blocks.py` | `model/block.py` (Block) + `text/blocks.py` (ghép đoạn, bảng) + `books/book01/rules.py` (`classify_line`) |
| `ingest/guards.py`, `ocr_fixer.py`, `review.py` | `ocrfix/guards.py`, `fixer.py`, `review.py` (Fix, Review → `model/block.py`) |
| `ingest/survey.py`, `pilot.py` | `survey/` |
| `ingest/pipeline.py`, `structure/pipeline.py` | `pipeline/p1.py`, `pipeline/p2.py` (gọi luật qua registry) |
| `ingest/report.py`, `structure/report.py` | `pipeline/p1_report.py`, `structure/report.py` |
| `structure/toc.py` | `model/toc.py` + `structure/toc_match.py` + `books/book01/rules.py` (đọc mục lục chấm dẫn) |
| `structure/heading_levels.py` | `model/tree.py` (HeadingDecision) + `structure/levels.py` (đối chiếu mục lục, kiểm đánh số, hỏi AI) + `books/book01/rules.py` (`rule_level`) |
| `structure/tree_builder.py` | `structure/tree_builder.py` (Node → `model/tree.py`) |
| `structure/section_mapper.py` | `structure/sections.py`; từ điển → `configs/books/<sách>/section_map.yaml` |
| `structure/golden.py` | `evaluation/golden.py` (kiểm tra) + `books/book01/golden.py` (sinh từ đáp án) |
| `evaluation/p1_eval.py`, `p2_eval.py` | `evaluation/truth/` |
| `cli.py`, `cli_*.py` | `cli/main.py`, `cli/p1.py`, … |
| `configs/section_map.yaml`, `glossary.yaml` | `configs/books/book01/` |
| `eval/golden_qa_v1.jsonl` | `eval/book01/golden_qa_v1.jsonl` |
| `data/raw/book01.pdf`, `data/p1_clean`, `data/p2_tree` | `data/books/book01/{raw, p1_clean, p2_tree}` |

## 6. Làm theo bước nhỏ, bước nào cũng giữ nguyên kết quả

Đây là **sắp xếp lại, không thêm tính năng**. Sau **mỗi bước** phải đạt cả 4 điều sau rồi mới commit:
- ✅ toàn bộ 509 test pass;
- ✅ chạy lại sách mẫu, `blocks.jsonl` và `nodes.jsonl` **cùng sha256 như trước**: `nodes.jsonl` = `e11ff132…`;
- ✅ `dm p2 eval` đạt G1–G7, `dm p2 golden --check` đạt;
- ✅ ruff, mypy, pre-commit sạch.

| Bước | Nội dung |
|---|---|
| **S1** | Tạo `model/`: chuyển các kiểu dữ liệu (Line, Block, Fix, Review, TocEntry, HeadingDecision, Node) vào, sửa import |
| **S2** | Tách `ingest/` thành `pdf/`, `text/`, `ocrfix/`, `survey/` |
| **S3** | Tạo `books/` (giao diện + registry + `book01/`); chuyển các luật riêng của sách mẫu vào `book01/` |
| **S4** | `pipeline/` gọi luật qua registry; `cli/` + tùy chọn `--book`; `configs/books/`, `data/books/`, `eval/book01/` (+ sửa lỗi đường dẫn từ điển) |
| **S5** | Tách `evaluation/` thành `truth/` (có đáp án) và `checks.py` (không cần đáp án) |

Sau S1–S5, plan P2R gọn lại: **I1** chỉ còn "tạo `books/iasp/` + `configs/books/iasp/`". I2–I6 viết luật **chỉ trong `books/iasp/`**, cùng phần mới trong `pdf/layout.py` (đọc theo cột, dùng được cho mọi sách 2 cột) và `evaluation/checks.py`.

## 7. Những điều cần biết

- **Lệnh cũ vẫn chạy:** `dm p1 run`, `dm p2 run`… không có `--book` thì mặc định là `book01`.
- **Dữ liệu cục bộ của bạn trong `data/`** (git bỏ qua) sẽ được chuyển vào `data/books/book01/` bằng một lệnh chuyển. Lệnh này in ra mọi thứ nó di chuyển.
- **Các báo cáo cũ** (P1, P2) vẫn nhắc đường dẫn file cũ. Tôi **không sửa lịch sử**, mà thêm một ghi chú "đường dẫn đã đổi, xem architecture.md" ở đầu `docs/phases/P1/gate_report.md` và `docs/phases/P2/gate_report.md`.
- **Rủi ro:** đổi đường dẫn nhiều file dễ sót import. Lưới an toàn là 509 test cộng với phép so sha256 dữ liệu sách mẫu trước/sau. Mỗi bước có commit riêng nên dễ quay lại.

## 8. Nhật ký thực hiện

| Bước | Commit | Kết quả |
|---|---|---|
| S1 `model/` | `a328b61` | Gom 6 nhóm kiểu dữ liệu; sửa import ở 36 file (bằng script dựa trên AST). 510 test pass; 12/12 file dữ liệu sách mẫu **giống hệt từng byte** |
| S2 tách `ingest/` | `1881762` | `pdf/` (reader, layout, furniture), `text/blocks`, `ocrfix/` (fixer, guards, review), `survey/`, `pipeline/` (p1, p1_report, p2). Logger đổi tên theo module mới. 514 test; 12/12 byte |
| S3 `books/` | `43d2a1c` | Xem bên dưới |
| S4 hồ sơ sách, `--book`, `cli/` | *(commit kèm theo)* | Xem cuối mục |

**S3: phần dùng chung nhận luật qua tham số** (các tham số này bắt buộc truyền, không có mặc định mang luật sách mẫu):

| Hàm dùng chung | Tham số luật | Sách mẫu truyền |
|---|---|---|
| `pdf.reader.read_lines` | `order` (mặc định chung: theo hàng) | mặc định |
| `pdf.furniture.strip_furniture` | `page_number` (mặc định chung) | mặc định |
| `text.blocks.build_blocks` | `classify`, `numbering` (**bắt buộc**) | `books/book01/lines.py` |
| `structure.heading_levels.classify_headings` | `rule_level` (**bắt buộc**), `chapter_prefix` | `books/book01/headings.py` |
| `structure.tree_builder.build_tree` | `display_title` (mặc định chung: bỏ số, chữ thường đầu câu) | thêm viết hoa sau "Chương n." |
| mục lục | `BookRules.read_toc` | `books/book01/toc.py` (chấm dẫn) |

`pipeline/p1.py`, `pipeline/p2.py` và CLI lấy luật qua `books.registry.rules_for(settings)`, theo `project.book_id`.

**Hai ngoại lệ có chủ ý** (module ngoài `books/` vẫn dùng luật sách mẫu):
- `cli_p2.py`, lệnh `dm p2 golden`: sinh câu hỏi tự động **chỉ có ý nghĩa với sách mẫu** (cần đáp án).
- `survey/survey.py`: công cụ khảo sát viết cho sách scan tiếng Việt (tín hiệu tiêu đề và lỗi OCR kiểu tiếng Việt).

**Script mutation check P2.1–P2.6:** đã cập nhật đường dẫn. Khi kiểm lại, phát hiện 2 đột biến (P2.1 M10, P2.2 H11) đã **không chạy được từ P2.4**, vì chuỗi đích bị trùng sau khi thêm `eval_sections`. Script đã từ chối chạy ("KHÔNG ÁP DỤNG ĐƯỢC") đúng như thiết kế, nhưng tôi không chạy lại script P2.1/P2.2 sau P2.4 nên không thấy. Đã sửa chuỗi đích. Toàn bộ 96 đích hiện tìm thấy đúng 1 lần.

**S4: mỗi sách một hồ sơ cấu hình và thư mục dữ liệu riêng**
- Lớp cấu hình mới `configs/books/<sách>/book.yaml`, nằm giữa `models.yaml` và `local.yaml`. Sách mẫu: `book_file`, `pilot`, cùng `glossary.yaml` và `section_map.yaml` chuyển vào `configs/books/book01/`.
- `{book_id}` trong cấu hình: `paths.raw_dir: data/books/{book_id}/raw`, `data_dir: data/books/{book_id}`, `eval_dir: eval/{book_id}`; `cache_dir: data/cache` dùng chung.
- **Chọn sách:** `dm --book <id>` > `DM__PROJECT__BOOK_ID` > `local.yaml` > `default.yaml` (`book01`).
- **Sửa 3 lỗi cùng loại** "lấy gốc dự án = thư mục cha của `data`": `core/run.py` (đường dẫn trong manifest), `ocrfix/fixer.py` (từ điển thuật ngữ), `pipeline/p2.py` + `cli/p2.py` (từ điển tên mục). Giờ cấu hình nhớ gốc dự án khi nạp (`settings.root`, `settings.from_root(...)`).
- `cli.py`, `cli_*.py` → gói `cli/`. Lệnh `dm` vẫn như cũ (`dataminer.cli:main`).
- Dữ liệu cục bộ của sách mẫu đã chuyển: `data/raw/` + `data/p0_*`, `p1_clean`, `p2_tree` → `data/books/book01/`. `eval/golden_qa_v1.jsonl` → `eval/book01/`.
- **Lỗi thiết kế tìm được khi test:** bản đầu lưu `--book` vào một biến toàn cục của `core/config`, nên một lần gọi `--book demo` **rò sang các lần nạp cấu hình sau** (2 test cấu hình hỏng). Đã sửa: chỉ CLI giữ lựa chọn và đặt lại ở mỗi lần gọi; `load_settings` nhận `book=` tường minh, không có trạng thái ẩn. Có test chống tái phát.
