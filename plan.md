# Kế hoạch triển khai: Data-miner

> Tài liệu yêu cầu: [problem.md](problem.md). File này mô tả **làm gì, theo thứ tự nào, chia module ra sao, và thế nào là "xong"** cho từng task.

---

## ⭐ Quy trình làm việc bắt buộc cho mỗi phase/task

**Quy tắc 1: Lên plan trước, triển khai sau.**
Trước khi bắt đầu một phase, viết `docs/phases/<P>/plan.md` theo mẫu [docs/templates/phase_plan.md](docs/templates/phase_plan.md). Plan được trình cho chủ dự án xem và **chỉ triển khai sau khi được xác nhận**. Nếu trong lúc làm phát hiện cần đổi hướng, cập nhật plan (ghi rõ thay đổi) trước khi code tiếp.

**Quy tắc 2: Mỗi task xong phải có code, test và data để xem và kiểm tra.**
Mỗi task hoàn thành phải có `docs/phases/<P>/<task-id>_report.md` theo mẫu [docs/templates/task_report.md](docs/templates/task_report.md), gồm:

| Thành phần | Nội dung bắt buộc |
|---|---|
| **Code** | Danh sách file đã tạo hoặc sửa, kèm link |
| **Test** | File test, lệnh chạy, **kết quả chạy thật** (output pytest), số test pass/fail |
| **Data** | Mẫu đầu vào/đầu ra **nhỏ, mở ra đọc được** trong `samples/<task-id>/` (vài bản ghi JSONL/CSV/MD), cùng đường dẫn đến artifact đầy đủ trong `data/` |
| **Cách tự kiểm tra** | Lệnh để chạy lại và những gì cần nhìn để xác nhận là đúng |
| **DoD** | Checklist DoD của task, đánh dấu từng mục đạt hay chưa đạt; mục chưa đạt ghi lý do |
| **Vấn đề / ghi chú** | Hạn chế đã biết, quyết định đã đưa ra, việc còn tồn đọng |

Khi xong cả phase: viết `docs/phases/<P>/gate_report.md` đối chiếu từng mục trong Gate, kèm số liệu eval và kết quả duyệt tay.

```
docs/
├─ templates/        phase_plan.md · task_report.md
└─ phases/
   └─ P1/            plan.md · P1.1_report.md · P1.2_report.md · … · gate_report.md
samples/
└─ P1.1/             input_sample.* · output_sample.jsonl   ← dữ liệu nhỏ để xem trực tiếp
```

`samples/` **được commit** vào git (mỗi file nhỏ, dưới khoảng 200 KB), còn `data/` thì không. Nhờ vậy luôn xem lại được kết quả của từng task.

---

## 0. Nguyên tắc thiết kế

Các nguyên tắc dưới đây áp dụng cho mọi phase. Chúng giúp hệ thống dễ bảo trì và dễ kiểm soát chất lượng.

| # | Nguyên tắc | Cách áp dụng |
|---|---|---|
| N1 | **Pipeline gồm các bước độc lập, giao tiếp qua file** | Mỗi phase đọc artifact của phase trước (JSONL/JSON/DB) và ghi artifact của mình. Chạy lại một bước không cần chạy lại toàn bộ. |
| N2 | **Hợp đồng dữ liệu bằng Pydantic** | Mọi artifact đều có schema trong `core/schemas.py`. Đầu vào và đầu ra của mỗi bước đều được validate. Đổi schema phải tăng `schema_version`. |
| N3 | **Truy vết nguồn (lineage)** | Mọi bản ghi (block, node, chunk, fact, mẫu train) đều mang `id` ổn định và con trỏ về nguồn (`page`, `node_id`, `chunk_id`). Từ một câu trả lời hay một mẫu train phải lần ngược được về trang sách. |
| N4 | **Idempotent và tiếp tục được** | Chạy lại cùng đầu vào và cấu hình phải ra cùng kết quả. Bước gọi LLM ghi kết quả theo từng bản ghi, nên khi lỗi giữa chừng có thể chạy tiếp từ chỗ dừng. |
| N5 | **Mọi lời gọi LLM đi qua một cửa** | `core/llm_client.py` lo cache (SQLite), retry, giới hạn tốc độ, ghi log chi phí và validate JSON. Không module nào gọi thẳng HTTP. |
| N6 | **Prompt là code** | Prompt nằm trong `prompts/*.md`, có `version` ở đầu file. Kết quả LLM lưu kèm `prompt_id@version` và `model`. |
| N7 | **Cấu hình tách khỏi code** | `configs/*.yaml`: model cho từng tác vụ, tham số chunking, ngưỡng lọc... Không hard-code. |
| N8 | **Mỗi lần chạy có manifest** | Mỗi lần chạy một phase sinh `manifest.json` gồm thời gian, git commit, hash cấu hình, phiên bản prompt, model, số bản ghi vào/ra và chi phí. |
| N9 | **Có cổng chất lượng (quality gate) giữa các phase** | Một phase chỉ được coi là xong khi qua gate của nó (xem từng phase). Gate gồm cả kiểm tra tự động lẫn duyệt tay. |
| N10 | **Người duyệt nằm trong vòng lặp** | Những chỗ cần duyệt tay đều xuất ra file CSV/Excel có cột `review_status` và `comment`, sau đó đọc ngược kết quả duyệt vào pipeline. |

---

## 1. Cấu trúc module

```
Data-miner/
├─ problem.md · plan.md · README.md
├─ pyproject.toml              # deps, ruff, mypy, pytest
├─ .env.example                # OPENROUTER_API_KEY=...
├─ configs/
│  ├─ default.yaml             # đường dẫn, tham số từng phase
│  └─ models.yaml              # model OpenRouter cho từng tác vụ
├─ prompts/                    # prompt có version (N6)
│  ├─ p1_fix_ocr.md
│  ├─ p2_classify_heading.md
│  ├─ p4_extract_disease.md
│  ├─ p5_agent_system.md
│  └─ p7_*.md
├─ src/dataminer/
│  ├─ core/                    # dùng chung, KHÔNG phụ thuộc module khác
│  │  ├─ config.py             # load YAML + env
│  │  ├─ schemas.py            # Pydantic: Block, Node, Chunk, Disease, Sample...
│  │  ├─ llm_client.py         # OpenRouter: cache, retry, rate limit, cost, JSON mode
│  │  ├─ io.py                 # đọc/ghi JSONL có validate, ghi manifest
│  │  ├─ text_vi.py            # chuẩn hóa NFC, tách từ, bỏ dấu...
│  │  └─ logging.py
│  ├─ ingest/        (P1)      # pdf_reader, cleaner, ocr_fixer
│  ├─ structure/     (P2)      # heading_detector, tree_builder, section_mapper
│  ├─ index/         (P3)      # chunker, embedder, bm25, vector_store, retriever, reranker
│  ├─ kb/            (P4)      # extractor, normalizer, classifier, db
│  ├─ qa/            (P5)      # tools, agent, formatter
│  ├─ batch/         (P6)      # runner, exporter
│  ├─ datagen/       (P7)      # generators/, filters/, splitter, exporter
│  ├─ evaluation/    (xuyên suốt) # metrics, judges, runners
│  └─ cli.py                   # `dm p1 run`, `dm p3 eval`, ...
├─ app/                        # Streamlit UI (P5)
├─ eval/                       # bộ câu hỏi chuẩn + nhãn tay (có version)
├─ tests/
│  ├─ unit/                    # test từng hàm, không gọi LLM thật
│  ├─ integration/             # chạy pipeline trên fixture nhỏ
│  └─ fixtures/                # 5–10 trang mẫu + kết quả mong đợi
└─ data/                       # KHÔNG commit (gitignore)
   ├─ raw/                     # PDF gốc
   ├─ p1_clean/ p2_tree/ p3_index/ p4_kb/ p6_batch/ p7_datagen/
   └─ cache/                   # cache LLM
```

**Quy tắc phụ thuộc:** `core` ← `ingest` ← `structure` ← `index` / `kb` ← `qa` ← `batch`, còn `datagen` dùng `index` + `kb` + `structure`. Một module chỉ được import từ module ở phía trước nó và từ `core`, không import ngược chiều.

---

## 2. Quy ước kỹ thuật

- **Python 3.11+**, quản lý môi trường bằng `uv` hoặc `poetry`.
- **Chất lượng code:** `ruff` (lint + format), `mypy` (type check), `pytest`, cùng `pre-commit` để chạy cả ba trước mỗi commit.
- **Git:** khởi tạo repo ngay ở P0. Mỗi task làm trên một nhánh `feat/<task-id>`, commit message có mã task (ví dụ `P2.3: map section types`).
- **Test không gọi LLM thật:** `llm_client` có chế độ `replay` đọc từ cache/fixture, giúp test nhanh, miễn phí và cho kết quả ổn định.
- **ID ổn định:** tạo từ nội dung và vị trí, ví dụ `node_id = hash(book_id, path tiêu đề)`, để chạy lại không làm đổi ID.
- **Theo dõi chi phí:** `llm_client` ghi log token và chi phí theo phase. Mỗi phase có ngân sách trong config, vượt ngân sách thì dừng.

---

## 3. Tổng quan phase và phụ thuộc

```
P0 Setup & khảo sát
 └─► P1 Trích xuất & làm sạch
      └─► P2 Dựng cấu trúc ──────────────┬─────────────────┐
           ├─► P3 Index & Retrieval      │                 │
           │    └──────────┬─────────────┘                 │
           └─► P4 Knowledge Base ──┐                       │
                           ▼       ▼                       ▼
                     P5 Hỏi đáp (agent + UI)        P7 Sinh dữ liệu huấn luyện (mẫu)
                           └─► P6 Batch & Export           └─► P8 Huấn luyện (giai đoạn sau)

EV  Bộ đánh giá: bắt đầu từ P2, mở rộng dần, dùng làm gate cho P3–P8
```

- P3 và P4 có thể **làm song song** sau khi P2 qua gate.
- P7 bắt đầu được khi P3 và P4 đã có kết quả trên **một chương mẫu**, không cần đợi xong toàn bộ sách.
- **Chiến lược "lát mỏng":** mỗi phase chạy trước trên **1 chương mẫu** (khoảng 5–10 bệnh), qua gate rồi mới chạy cho toàn bộ sách. Nhờ đó phát hiện lỗi sớm và tốn ít chi phí.

---

## 4. Chi tiết từng phase

Ký hiệu mỗi task: **Đầu vào → Đầu ra**, **DoD** (Definition of Done: điều kiện để coi là xong), **Test** (cách kiểm tra).

---

### P0: Setup và khảo sát sách

**Mục tiêu:** có khung dự án chạy được, và hiểu sách được viết theo khuôn nào.

| Task | Nội dung | DoD |
|---|---|---|
| **P0.1** Khởi tạo repo | `git init`, `pyproject.toml`, cấu trúc thư mục, pre-commit, `.env.example`, README | `pytest` chạy được (0 test), pre-commit pass |
| **P0.2** `core/config.py` + `configs/*.yaml` | Load YAML + biến môi trường, validate bằng Pydantic | Unit test: load config hợp lệ; báo lỗi rõ ràng khi thiếu key |
| **P0.3** `core/llm_client.py` | Client OpenRouter (OpenAI SDK + `base_url`). Có cache SQLite theo hash(model, prompt, params), retry/backoff, giới hạn tốc độ, JSON mode + validate Pydantic + tự retry khi JSON sai, ghi log chi phí, chế độ `replay` | Unit test với mock: cache hit không gọi API, retry khi lỗi 429/5xx, JSON sai thì retry rồi mới báo lỗi. Gọi thật 1 lần thành công. |
| **P0.4** `core/io.py`, `core/schemas.py` (khung) | Đọc/ghi JSONL có validate, ghi manifest | Unit test: ghi rồi đọc lại khớp nhau; bản ghi sai schema thì báo lỗi |
| **P0.5** Khảo sát sách | Script trích 10–15 trang mẫu (text + font size + bold + bbox). Ghi lại: cách nhận diện tiêu đề, các mục chuẩn của một bệnh, kiểu lỗi OCR hay gặp, header/footer, bảng | File `docs/book_profile.md` + bộ fixture `tests/fixtures/pages/` (5–10 trang đại diện) |
| **P0.6** Chọn chương mẫu | Chọn 1 chương có khoảng 5–10 bệnh, đủ đa dạng (có bảng, có danh sách thuốc) | Ghi lại trong `configs/default.yaml` (`pilot_pages`) |

**🚦 Gate P0:**
- [ ] CI cục bộ (ruff, mypy, pytest) pass.
- [ ] Gọi được OpenRouter qua `llm_client`, cache hoạt động.
- [ ] `book_profile.md` mô tả được bằng quy tắc: "đầu bệnh mới trông thế nào" và "mục Triệu chứng trông thế nào".

---

### P1: Trích xuất và làm sạch text (`ingest/`)

**Mục tiêu:** từ PDF có được text sạch, đúng thứ tự đọc, giữ nguyên vị trí nguồn.
**Artifact:** `data/p1_clean/blocks.jsonl`. Mỗi bản ghi: `Block{block_id, page, bbox, text_raw, text, font_size, bold, flags[]}`.

| Task | Nội dung | DoD | Test |
|---|---|---|---|
| **P1.1** `pdf_reader.py` | PyMuPDF `get_text("dict")` → các Block theo thứ tự đọc, có font/bbox | Trích đủ mọi trang có text, giữ đúng thứ tự đọc (kể cả trang 2 cột nếu có) | Unit test trên fixture: số block, thứ tự và nội dung khớp file mong đợi |
| **P1.2** `cleaner.py`: quy tắc | Chuẩn hóa NFC; bỏ header/footer và số trang (dòng lặp lại ở cùng vị trí trên nhiều trang); nối dòng ngắt giữa câu; nối từ gạch nối; chuẩn hóa bullet và khoảng trắng | Mỗi quy tắc là một hàm riêng, bật/tắt được trong config | Unit test **cho từng quy tắc** với các ca biên (dòng kết thúc bằng dấu chấm, tên thuốc có gạch nối...) |
| **P1.3** Phát hiện đoạn lỗi | Heuristic: tỉ lệ token không có trong từ điển tiếng Việt, ký tự lạ, từ dính liền → `flags=["ocr_suspect"]` | Đánh dấu được đúng các đoạn lỗi trong fixture | Precision/recall trên khoảng 50 đoạn gán nhãn tay ≥ 0.8 |
| **P1.4** `ocr_fixer.py`: LLM | Chỉ sửa các block bị đánh dấu. Prompt "chỉ sửa chính tả/dấu, không đổi nội dung". **Guard:** so diff ký tự; số, tên thuốc và đơn vị phải giữ nguyên, nếu không thì giữ bản gốc và gắn flag `fix_rejected` | Lưu cả `text_raw` và `text`; có báo cáo số block đã sửa và số block bị từ chối | Unit test cho guard (đổi số → bị từ chối). Duyệt tay 30 block đã sửa. |
| **P1.5** CLI + báo cáo | `dm p1 run [--pages]` tạo `blocks.jsonl`, `manifest.json` và `report.html` (so sánh trước/sau) | Chạy lại lần 2 dùng cache và ra kết quả giống hệt lần 1 | Integration test trên fixture |

**🚦 Gate P1** (trên chương mẫu, sau đó trên toàn sách):
- [ ] Đọc ngẫu nhiên 10 trang: không còn header/footer, không còn câu bị ngắt dòng, dấu tiếng Việt đúng.
- [ ] 0 trường hợp đổi số liệu hoặc tên thuốc (guard P1.4 + kiểm tra tay 30 block).
- [ ] Mọi test pass.

---

### P2: Dựng cấu trúc tài liệu (`structure/`)

**Mục tiêu:** chuyển text phẳng thành cây Sách → Chương → Bệnh → Mục → Mục con.
**Artifact:** `data/p2_tree/tree.json`. Mỗi node: `Node{node_id, parent_id, level, title, section_type, text, page_start, page_end, block_ids[]}`.

| Task | Nội dung | DoD | Test |
|---|---|---|---|
| **P2.1** Trích mục lục | Lấy danh sách chương/bệnh từ trang mục lục (quy tắc, LLM hỗ trợ nếu cần) | `toc.json`: danh sách tiêu đề kèm trang | So khớp tay với mục lục sách |
| **P2.2** `heading_detector.py` | Phân loại block là tiêu đề hay không, và ở cấp nào, dựa trên font size, bold, in hoa, mẫu đánh số. Ngưỡng nằm trong config. | Nhận diện đúng tiêu đề trên fixture | F1 ≥ 0.95 trên các tiêu đề đã gán nhãn của chương mẫu |
| **P2.3** `tree_builder.py` | Dựng cây từ chuỗi block và tiêu đề; đối chiếu với `toc.json` để sửa cấp hoặc phát hiện thiếu | Mọi block thuộc đúng một node; không có node rỗng | Unit test: dựng cây từ chuỗi block giả; kiểm tra các bất biến (cha/con, khoảng trang) |
| **P2.4** `section_mapper.py` | Ánh xạ tiêu đề mục → `section_type` chuẩn (`definition, cause, risk_factor, symptom, paraclinical, diagnosis, treatment, complication, prevention, other`). Dùng từ điển trước, LLM sau cho tiêu đề lạ, kết quả từ LLM được ghi ngược vào từ điển sau khi duyệt. | Từ điển `configs/section_map.yaml`; tỉ lệ `other` < 5% | Unit test từ điển; duyệt tay toàn bộ các ánh xạ do LLM đề xuất |
| **P2.5** Báo cáo cấu trúc | Xuất `tree_report.md`: số bệnh mỗi chương, các bệnh thiếu mục chuẩn, các node bất thường (quá dài, quá ngắn) | Có danh sách cảnh báo để duyệt | — |
| **EV.1** Khởi tạo bộ đánh giá | Tạo `eval/golden_qa_v1.jsonl` gồm khoảng 30 câu (chương mẫu): câu hỏi, đáp án, `node_id`/trang nguồn, loại (cụ thể/liệt kê/từ chối) | Có người chuyên môn duyệt | Schema validate |

**🚦 Gate P2:**
- [ ] Số bệnh dựng được **khớp 100%** với mục lục.
- [ ] Duyệt tay 10 bệnh: các mục được tách và gán `section_type` đúng ≥ 95%.
- [ ] Tỉ lệ `section_type = other` < 5%.
- [ ] `golden_qa_v1` sẵn sàng.

---

### P3: Index và Retrieval (`index/`)

**Mục tiêu:** tìm đúng đoạn cho câu hỏi cụ thể.
**Artifact:** `data/p3_index/chunks.jsonl`, vector store, BM25 index.

| Task | Nội dung | DoD | Test |
|---|---|---|---|
| **P3.1** `chunker.py` | Mỗi mục/mục con là một chunk; mục dài hơn `max_tokens` thì chia theo đoạn, có chồng lấn. Thêm tiền tố ngữ cảnh `[Bệnh: … \| Mục: …]`. Metadata: `disease, chapter, section_type, pages, node_id`. Hỗ trợ parent–child. | Không chunk nào vượt giới hạn; mọi chunk có metadata đủ | Unit test chia và gắn metadata |
| **P3.2** `embedder.py` | bge-m3 local (sentence-transformers), chạy theo batch, cache embedding theo hash nội dung | Embed toàn bộ chunk; chạy lại thì không embed lại | Unit test cache |
| **P3.3** `bm25.py` | Tách từ tiếng Việt (pyvi/underthesea), BM25 | Tìm được tên thuốc hoặc tên bệnh chính xác | Unit test với vài truy vấn từ khóa |
| **P3.4** `vector_store.py` | Interface `VectorStore` + 1 implementation (Chroma/Qdrant local), lọc theo metadata | Đổi backend chỉ cần sửa config | Test interface |
| **P3.5** `retriever.py` + `reranker.py` | Hybrid: BM25 + dense → RRF → rerank (bge-reranker-v2-m3) → top-k. Hàm `search(query, filters, k)` | Trả về chunk kèm điểm và nguồn | Integration test |
| **P3.6** `evaluation/retrieval.py` | Tính Recall@k và MRR trên golden set; so sánh BM25 / dense / hybrid / hybrid+rerank | Có `eval_report` lưu lại theo phiên bản | — |

**🚦 Gate P3:**
- [ ] **Recall@5 ≥ 90%** trên golden set (bỏ qua câu loại "liệt kê", vì loại đó thuộc P4).
- [ ] Hybrid+rerank tốt hơn hoặc bằng từng phương pháp riêng lẻ (có số liệu trong report).
- [ ] Mọi test pass, báo cáo lưu trong `eval/reports/`.

---

### P4: Knowledge Base có cấu trúc (`kb/`)

**Mục tiêu:** có dữ liệu bệnh có cấu trúc, chuẩn hóa, truy vấn được bằng SQL.
**Artifact:** `data/p4_kb/diseases.jsonl`, `data/p4_kb/kb.sqlite`.

| Task | Nội dung | DoD | Test |
|---|---|---|---|
| **P4.1** Schema `Disease` | Pydantic theo mục 4.4 của problem.md. Mỗi giá trị trong danh sách đều mang `evidence: {node_id, pages, quote}` | Schema được duyệt | Unit test validate |
| **P4.2** `extractor.py` | Mỗi bệnh: gửi text các node của bệnh đó + schema → LLM (JSON mode) → validate. **Guard:** `quote` phải xuất hiện (fuzzy match) trong text nguồn, nếu không thì loại giá trị đó và ghi log | Chạy được theo từng bệnh, tiếp tục được khi lỗi | Unit test cho guard; replay test |
| **P4.3** Nhãn tay | Gán nhãn tay khoảng 15–20 bệnh, lưu `eval/kb_gold_v1.jsonl` | Có người duyệt | — |
| **P4.4** `evaluation/kb.py` | Precision/recall theo từng trường, so với nhãn tay | Có report | — |
| **P4.5** `normalizer.py` | Gom tên đồng nghĩa (triệu chứng, thuốc, nguyên nhân): embedding → clustering → LLM đề xuất tên chuẩn → **xuất CSV cho người duyệt** → đọc lại thành `configs/synonyms.yaml` | Mọi thực thể đều được ánh xạ về tên chuẩn | Unit test áp dụng từ điển; duyệt tay toàn bộ cụm |
| **P4.6** `classifier.py` | Gán nhóm bệnh theo danh sách nhãn cố định (`configs/categories.yaml`) | Mỗi bệnh có ≥ 1 nhóm | Duyệt tay mẫu |
| **P4.7** `db.py` | Nạp vào SQLite: `diseases`, `symptoms`, `disease_symptom`, `drugs`, `disease_treatment`, `causes`... Có các hàm truy vấn tiện dụng (`find_diseases(symptoms=…, drugs=…)`) | Truy vấn liệt kê trả đúng | Unit test các query trên DB nhỏ |

**🚦 Gate P4:**
- [ ] Độ chính xác trích xuất ≥ 90% trên `kb_gold_v1`, **0 giá trị không có evidence**.
- [ ] Bảng đồng nghĩa đã được duyệt 100%.
- [ ] Các câu loại "liệt kê" trong golden set trả đúng bằng SQL.

---

### P5: Hỏi đáp (`qa/`, `app/`)

**Mục tiêu:** hỏi bằng ngôn ngữ tự nhiên, nhận câu trả lời đúng và có trích dẫn.

| Task | Nội dung | DoD | Test |
|---|---|---|---|
| **P5.1** `tools.py` | `search_text`, `get_disease`, `find_diseases`, `list_values`. Mỗi tool có JSON schema và docstring rõ ràng cho LLM | Tool trả kết quả có nguồn | Unit test từng tool |
| **P5.2** `agent.py` | Vòng lặp tool calling qua OpenRouter, giới hạn số bước, có log trace từng bước | Trả lời được câu cụ thể, câu liệt kê và câu hỗn hợp | Replay test với trace mẫu |
| **P5.3** `formatter.py` | Chuẩn hóa câu trả lời: trích dẫn `(Bệnh – Mục, tr.X)`, câu nhắc y khoa, câu "Sách không đề cập" | Mọi câu trả lời có trích dẫn hợp lệ (trang tồn tại) | Unit test validate trích dẫn |
| **P5.4** `evaluation/answers.py` | LLM-judge (dùng model khác với model trả lời): độ đúng, độ trung thực, trích dẫn đúng; tỉ lệ từ chối đúng | Report theo phiên bản | — |
| **P5.5** UI Streamlit | Tab hỏi đáp: hiện câu trả lời, nguồn và đoạn gốc; xem trace agent | Demo được | Kiểm tra tay |
| **P5.6** (tùy chọn) API FastAPI | `POST /ask`, `POST /search` | — | Integration test |

**🚦 Gate P5:**
- [ ] Trên golden set: độ đúng ≥ mục tiêu ở problem.md mục 8; **100% câu trả lời có trích dẫn hợp lệ**; tỉ lệ bịa ≈ 0.
- [ ] Duyệt tay 20 câu trả lời.

---

### P6: Batch query và Export (`batch/`)

| Task | Nội dung | DoD | Test |
|---|---|---|---|
| **P6.1** `runner.py` | Đầu vào là CSV/Excel câu hỏi hoặc template × danh sách bệnh. Chạy song song có giới hạn, tiếp tục được, lưu từng kết quả | Ngắt giữa chừng rồi chạy lại thì không chạy lại câu đã xong | Integration test |
| **P6.2** `exporter.py` | Xuất kết quả batch (Excel/JSON); xuất KB (Excel bảng bệnh–triệu chứng–điều trị); xuất chunks + metadata cho hệ RAG khác | File mở được, đủ cột | Unit test |
| **P6.3** Tab Batch trong UI | Upload file, theo dõi tiến độ, tải kết quả | — | Kiểm tra tay |

**🚦 Gate P6:**
- [ ] Chạy template "nguyên nhân/triệu chứng/điều trị" cho toàn bộ bệnh thành công, có báo cáo chi phí.
- [ ] Kiểm tra ngẫu nhiên 20 dòng kết quả.

---

### P7: Sinh dữ liệu huấn luyện, bản mẫu (`datagen/`)

**Mục tiêu:** sinh và kiểm định **dữ liệu mẫu** cho cả hai chế độ (A: closed-book, B: RAG) theo mục 6 của problem.md. **Chưa huấn luyện.**
**Artifact:** `data/p7_datagen/<type>/*.jsonl`, `data/p7_datagen/final/{train,val,test}_{A,B}.jsonl`.

Mỗi generator là **một class riêng** dùng chung interface `Generator.generate(source) -> list[Sample]`. Nhờ vậy thêm hoặc bớt loại dữ liệu không ảnh hưởng đến phần còn lại.

| Task | Nội dung | DoD | Test |
|---|---|---|---|
| **P7.1** Schema `Sample` | `messages[]` + `meta{task, mode, disease, section, pages, node_ids, fact_ids, teacher_model, prompt_id, quality{...}}` | Schema được duyệt | Unit test |
| **P7.2** `generators/paraphrase.py` (D1, D1b) | Văn bản sạch theo mục; diễn đạt lại N kiểu | Guard: số, thuốc, liều phải khớp nguồn | Unit test cho guard |
| **P7.3** `generators/qa_single.py` (D2, D8) | Hỏi–đáp theo từng mục/sự kiện, nhiều cách hỏi, hỏi theo cả hai chiều; sinh mẫu chế độ A | — | Replay test |
| **P7.4** `generators/qa_aggregate.py` (D3) | Sinh từ SQL trên KB (P4), đáp án tạo từ kết quả query, không để LLM tự nghĩ ra | Đáp án khớp kết quả query | Unit test |
| **P7.5** `generators/qa_rag.py` (D4, D5) | Câu hỏi + top-k từ retriever (P3) + chèn đoạn nhiễu; mẫu chế độ B; mẫu từ chối cho cả A và B | Có tỉ lệ từ chối theo config | Unit test cách ghép ngữ cảnh |
| **P7.6** `generators/extraction.py` (D6) | Văn bản bệnh → JSON từ KB đã duyệt | — | Validate schema |
| **P7.7** `generators/preference.py` (D7) | Cặp chosen/rejected (rejected = cố ý làm sai: đổi liều, lẫn bệnh, bỏ trích dẫn) | — | Unit test |
| **P7.8** `filters/` | Mỗi bộ lọc là một module: `faithfulness_judge`, `number_guard`, `dedup`, `format_check`, `length_check`. Mỗi mẫu ghi điểm vào `meta.quality` | Báo cáo tỉ lệ loại theo từng bộ lọc | Unit test từng bộ lọc |
| **P7.9** `splitter.py` | Chế độ B chia theo bệnh; chế độ A chia theo `fact_id` + kiểu diễn đạt. **Loại mọi mẫu trùng hoặc gần trùng với golden set** | Không rò rỉ giữa train và test | Unit test: kiểm tra giao nhau giữa các tập bằng 0 |
| **P7.10** `exporter.py` + báo cáo | Trộn theo tỉ lệ trong config, xuất JSONL theo chat format; `datagen_report.md`: số mẫu theo loại/chế độ, tỉ lệ bị lọc, chi phí, 20 mẫu ngẫu nhiên | — | — |
| **P7.11** Duyệt tay | Xuất 2–5% mẫu ra CSV cho người chuyên môn duyệt | ≥ 95% mẫu đạt | — |

**🚦 Gate P7:**
- [ ] Trên chương mẫu: mỗi loại D1–D8 có ≥ 50 mẫu qua bộ lọc.
- [ ] Duyệt tay: ≥ 95% đạt, **0 mẫu sai liều thuốc hoặc con số**.
- [ ] Kiểm tra rò rỉ train/test và golden set = 0.
- [ ] Ước tính được chi phí và thời gian để sinh cho toàn bộ sách.

---

### P8: Huấn luyện (giai đoạn sau, chỉ phác thảo)

Thực hiện sau khi P7 qua gate và đã rà soát điều khoản teacher model (problem.md mục 6.8).

| Task | Nội dung |
|---|---|
| P8.1 | Chọn model nền: chạy baseline (cấu hình 1 và 2 ở problem.md mục 6.7) cho 2–3 ứng viên |
| P8.2 | Sinh lại dữ liệu cho toàn sách bằng teacher model hợp lệ |
| P8.3 | CPT trên D1 + D1b → kiểm tra nhanh khả năng nhớ closed-book |
| P8.4 | SFT (trộn A/B) → đánh giá |
| P8.5 | (tùy chọn) DPO trên D7 |
| P8.6 | Đánh giá 4 cấu hình + kiểm tra suy giảm năng lực chung |
| P8.7 | Merge, lượng tử hóa, phục vụ qua vLLM/Ollama, đổi `base_url` trong `configs/models.yaml` |

Cấu hình huấn luyện (YAML của Unsloth/LLaMA-Factory) được lưu trong `training/configs/` và có version giống prompt.

---

## 5. Đảm bảo chất lượng xuyên suốt

### 5.1. Các tầng kiểm tra

| Tầng | Công cụ | Khi nào chạy |
|---|---|---|
| Lint, format, type | ruff, mypy | Mỗi commit (pre-commit) |
| Unit test | pytest, không gọi LLM thật | Mỗi commit |
| Integration test | pytest trên `tests/fixtures/` với LLM `replay` | Trước khi merge task |
| Đánh giá chất lượng (eval) | `dm eval <phase>` trên golden set | Mỗi khi đổi prompt, model, config hoặc thuật toán |
| Duyệt tay | CSV có `review_status` | Ở mỗi gate |

### 5.2. Kiểm soát hồi quy (regression)

- Mọi kết quả eval lưu trong `eval/reports/<phase>/<date>_<git-sha>.json`.
- `dm eval compare` so sánh với lần tốt nhất trước đó. **Chỉ số giảm quá 2% thì không merge.**
- Đổi prompt hoặc model = tăng version + chạy lại eval của phase đó và các phase phía sau.

### 5.3. Bộ đánh giá (EV) mở rộng dần

| Phiên bản | Khi nào | Quy mô |
|---|---|---|
| `golden_qa_v1` | P2 (chương mẫu) | ~30 câu |
| `golden_qa_v2` | Trước khi chạy toàn sách | ~100 câu, đủ các loại: cụ thể, liệt kê, từ chối, hỗn hợp |
| `kb_gold_v1` | P4 | 15–20 bệnh gán nhãn đầy đủ |
| `closed_book_test` | P7 | Câu hỏi diễn đạt mới cho chế độ A |

Golden set **chỉ được thêm câu, không sửa câu cũ** (nếu buộc phải sửa thì tạo version mới), để kết quả giữa các lần đo còn so sánh được.

---

## 6. Rủi ro và cách giảm thiểu

| Rủi ro | Ảnh hưởng | Giảm thiểu |
|---|---|---|
| Cấu trúc sách không đều, khó nhận diện tiêu đề | P2 sai kéo theo mọi phase sau sai | Dựa vào mục lục; gate P2 chặt; cho phép sửa tay bằng file override `configs/tree_overrides.yaml` |
| LLM sửa hoặc bịa nội dung y khoa | Sai thông tin nguy hiểm | Guard số/thuốc (P1.4, P7.2), bắt buộc evidence (P4.2), judge (P5.4, P7.8), duyệt tay |
| Chi phí API vượt dự kiến | — | Cache, chạy chương mẫu trước, ngân sách theo phase, dùng model rẻ cho tác vụ đơn giản |
| Prompt hoặc model đổi làm chất lượng giảm mà không biết | Hồi quy | Prompt có version + eval tự động + so sánh với lần tốt nhất |
| Rò rỉ dữ liệu test vào train | Kết quả đánh giá ảo | Splitter có kiểm tra giao nhau + loại các mẫu gần trùng golden set |
| Thiếu người duyệt chuyên môn | Không qua được gate | Xác định người duyệt từ P0; giữ khối lượng duyệt ở mức nhỏ (mẫu 2–5%) |

---

## 7. Thứ tự thực hiện đề xuất (milestones)

| Milestone | Gồm | Kết quả có thể demo |
|---|---|---|
| **M1: Nền móng** | P0, P1, P2 trên chương mẫu + EV.1 | Xem được cây cấu trúc chương mẫu và text sạch |
| **M2: MVP hỏi đáp** | P3 + P5 (chỉ `search_text`) trên chương mẫu | Hỏi đáp có trích dẫn trên một chương |
| **M3: Truy vấn tổng hợp** | P4 + P5 đầy đủ trên chương mẫu | Trả lời được câu liệt kê/lọc |
| **M4: Dữ liệu huấn luyện mẫu** | P7 trên chương mẫu | Bộ dữ liệu mẫu D1–D8 + báo cáo chất lượng |
| **M5: Toàn sách** | Chạy P1→P7 cho toàn sách, `golden_qa_v2`, P6 | Hệ thống hoàn chỉnh + export |
| **M6: Huấn luyện** | P8 | Model tự host |

Mỗi milestone kết thúc bằng: **qua gate của các phase liên quan → cập nhật README → ghi lại số liệu eval**.
