# Plan P0: Setup và khảo sát sách

> Trạng thái: `Đang làm`. P0.1 ✅, P0.2 ✅; P0.3–P0.6 chờ duyệt.
> Ngày tạo: 2026-10-19 · Cập nhật: 2026-10-19
> Tham chiếu: [plan.md](../../../plan.md) mục P0 · [problem.md](../../../problem.md)

## 1. Mục tiêu

1. Dựng **khung dự án chạy được** gồm package Python, công cụ chất lượng code, test, CLI và cấu hình. Mọi phase sau xây trên khung này.
2. Xây các **thành phần lõi dùng chung** (`core/`): cấu hình, LLM client, đọc/ghi dữ liệu có schema.
3. **Hiểu khuôn của cuốn sách** (cách trình bày tiêu đề, các mục, lỗi OCR) để thiết kế P1–P2 dựa trên dữ liệu thật thay vì phỏng đoán.

## 2. Đầu vào / Đầu ra

| | Artifact | Vị trí |
|---|---|---|
| Vào | PDF sách (cần cho P0.5) | `data/raw/<book>.pdf` |
| Ra | Khung dự án + package `dataminer` | toàn repo |
| Ra | Thành phần lõi | `src/dataminer/core/` |
| Ra | Hồ sơ cuốn sách | `docs/book_profile.md` |
| Ra | Trang mẫu dùng làm fixture | `tests/fixtures/pages/` |
| Ra | Cấu hình chương mẫu | `configs/default.yaml` (`pilot`) |

## 3. Phạm vi

- **Làm:** khung dự án, `core/` (config, llm_client, io, schemas cơ sở, logging), khảo sát sách, chọn chương mẫu.
- **Không làm:**
  - Không trích xuất hay làm sạch toàn bộ sách (thuộc P1).
  - Chưa định nghĩa schema nghiệp vụ như Block, Node, Disease: P0 chỉ tạo lớp cơ sở, các phase sau mới thêm schema của mình.
  - Chưa cài thư viện nặng (PyMuPDF, sentence-transformers...); thư viện nào cần ở phase nào thì thêm ở phase đó. Riêng PyMuPDF sẽ thêm ở P0.5.

## 4. Thiết kế

### 4.1. Công cụ

| Hạng mục | Lựa chọn | Lý do |
|---|---|---|
| Python | ≥ 3.11 (máy hiện có 3.12.10) | Typing hiện đại, nhanh |
| Quản lý môi trường/deps | **uv** (đã có 0.11) | Nhanh, có lockfile `uv.lock` giúp tái lập môi trường |
| Layout | `src/` layout, package `dataminer` | Tránh import nhầm, chuẩn cho test |
| Lint + format | **ruff** | Một công cụ thay cho flake8, isort và black |
| Type check | **mypy** (`strict` cho `src/`) | Bắt lỗi sớm, hợp với Pydantic |
| Test | **pytest** + pytest-cov | Chuẩn phổ biến |
| Pre-commit | **pre-commit** | Tự chạy ruff, mypy, kiểm tra file lớn trước mỗi commit |
| CLI | **typer** | Gọn, tự sinh `--help` |

### 4.2. Thành phần `core/`

```
core/
├─ config.py      Settings (Pydantic) ← configs/default.yaml (+ configs/local.yaml nếu có) + .env
├─ llm_client.py  LLMClient: chat() / chat_json(schema) → OpenRouter
├─ cache.py       SQLite cache: key = sha256(model, messages, params, schema)
├─ io.py          read_jsonl / write_jsonl / append_jsonl (validate Pydantic), write_manifest
├─ schemas.py     BaseRecord (id, schema_version), RunManifest
└─ logging.py     Logger thống nhất (console + file theo lần chạy)
```

**Thiết kế LLMClient (P0.3):**
- Dùng OpenAI SDK với `base_url = https://openrouter.ai/api/v1`.
- **Cache:** đã có kết quả thì trả về ngay, không gọi API.
- **Chế độ** (`LLM_MODE`):
  - `live`: gọi API và ghi cache.
  - `replay`: chỉ đọc cache, gặp lời gọi chưa có trong cache thì báo lỗi. Test dùng chế độ này.
  - `refresh`: bỏ qua cache, gọi lại API rồi ghi đè cache.
- **Retry** với backoff mũ khi gặp lỗi 429, 5xx hoặc timeout. Lỗi 4xx khác thì báo lỗi ngay.
- **Giới hạn tốc độ:** dùng semaphore giới hạn số request đồng thời (lấy từ config).
- **`chat_json(schema)`:** gửi `response_format` dạng JSON schema, rồi parse và validate bằng Pydantic. Nếu sai, gửi lại kèm thông báo lỗi, tối đa N lần.
- **Ghi chi phí:** lưu token vào/ra và chi phí (nếu OpenRouter trả về) theo từng `task_tag`. Mỗi task có ngân sách; vượt ngân sách thì dừng và báo lỗi `BudgetExceeded`.
- Phần lõi viết bất đồng bộ (async) để chạy song song khi chạy lô, kèm hàm bọc đồng bộ cho script đơn giản.

### 4.3. Khảo sát sách (P0.5)

Viết script `scripts/survey_book.py` (dùng PyMuPDF) để:
1. Thống kê toàn sách: số trang, số trang không có text, phân bố cỡ chữ.
2. Xuất 10–15 trang mẫu (trang mục lục, đầu chương, đầu bệnh, trang có bảng, trang lỗi nặng) ra dạng `dict` gồm text, font, size, bold, bbox. Cùng với đó xuất **ảnh PNG** của trang để đối chiếu bằng mắt.
3. Tự động gợi ý: các dòng lặp lại ở đầu/cuối trang (ứng viên header/footer), cỡ chữ của các cấp tiêu đề.

Từ kết quả đó viết `docs/book_profile.md` bằng tay (có hỗ trợ từ script).

## 5. Danh sách task

### P0.1 Khởi tạo repo và khung dự án
- **Mục tiêu:** có một package cài đặt được, test chạy được, công cụ chất lượng code hoạt động, CLI chạy được.
- **File sẽ tạo:**
  - `pyproject.toml`, `uv.lock`, `.python-version`
  - `.gitignore`, `.env.example`, `.pre-commit-config.yaml`, `README.md`
  - `src/dataminer/__init__.py`, `src/dataminer/cli.py`
  - `__init__.py` rỗng cho các module: `core, ingest, structure, index, kb, qa, batch, datagen, evaluation`
  - Thư mục: `configs/`, `prompts/`, `scripts/`, `app/`, `eval/`, `tests/{unit,integration,fixtures}/`, `samples/`, `data/` (chỉ chứa `.gitkeep`, phần còn lại bị gitignore)
- **Cách làm:**
  - `git init`.
  - Dùng uv tạo môi trường; deps tối thiểu: `pydantic`, `pyyaml`, `python-dotenv`, `typer`.
  - Dev deps: `pytest`, `pytest-cov`, `ruff`, `mypy`, `pre-commit`, `types-PyYAML`.
  - CLI `dm` có 2 lệnh:
    - `dm version`: in ra phiên bản.
    - `dm info`: in đường dẫn dự án, phiên bản Python, danh sách module, trạng thái các thư mục, có hay chưa có `.env` và PDF.
- **Test sẽ viết** (`tests/unit/test_scaffold.py`):
  - Import được package và đủ 9 module con.
  - Phiên bản lấy từ package metadata khớp với `pyproject.toml`.
  - `dm version` và `dm info` chạy với exit code 0, output có các trường mong đợi.
  - Các thư mục bắt buộc tồn tại.
  - `.gitignore` chặn `data/*` và `.env`, không chặn `samples/`.
- **Data mẫu** (`samples/P0.1/`):
  - `project_tree.txt`: cây thư mục.
  - `cli_info.txt`: output của `dm info`.
  - `quality_checks.txt`: output thật của ruff, mypy, pytest và pre-commit.
- **DoD:** ✅ Hoàn thành, xem [P0.1_report.md](P0.1_report.md)
  - [x] `uv sync` thành công, có `uv.lock`
  - [x] `ruff check` và `ruff format --check` pass
  - [x] `mypy src` (strict) pass
  - [x] `pytest` pass toàn bộ
  - [x] `pre-commit run --all-files` pass
  - [x] `dm version` / `dm info` chạy được
  - [x] Báo cáo `P0.1_report.md` + `samples/P0.1/`

### P0.2 Cấu hình (`core/config.py`, `configs/*.yaml`)
> Plan chi tiết: [P0.2_plan.md](P0.2_plan.md)
- **File:** `core/config.py`, `configs/default.yaml`, `configs/models.yaml`, test.
- **Cách làm:**
  - Định nghĩa `Settings` bằng Pydantic, gồm: `paths`, `llm` (base_url, mode, concurrency, max_retries, timeout), `budget`, `pilot`.
  - `models.yaml` ánh xạ tác vụ sang model, ví dụ `fix_ocr`, `extract`, `qa`, `judge`, `datagen`.
  - Thứ tự ưu tiên khi trùng giá trị: `default.yaml` < `local.yaml` (không commit) < biến môi trường.
- **Test:**
  - Load cấu hình hợp lệ.
  - Thiếu hoặc sai kiểu thì báo lỗi rõ tên key.
  - Biến môi trường ghi đè được giá trị trong YAML.
  - Không có API key thì vẫn load được, chỉ báo lỗi khi thực sự gọi LLM.
- **Data mẫu:** `samples/P0.2/resolved_config.yaml` (cấu hình sau khi gộp, đã che API key).
- **DoD:** ✅ Hoàn thành, xem [P0.2_report.md](P0.2_report.md). Test pass; `dm config show` in ra cấu hình đã gộp và che key.

### P0.3 LLM client (`core/llm_client.py`, `core/cache.py`)
- **Cách làm:** theo thiết kế ở mục 4.2.
- **Test** (mock HTTP, không tốn tiền):
  - Gọi 2 lần giống hệt nhau thì chỉ gọi API 1 lần.
  - Chế độ `replay` gặp lời gọi chưa cache thì báo lỗi.
  - Retry khi lỗi 429/5xx, không retry khi lỗi 400.
  - JSON sai schema thì retry kèm thông báo lỗi, quá N lần thì báo lỗi.
  - Ghi đúng token và chi phí; vượt ngân sách thì báo `BudgetExceeded`.
  - Giới hạn đồng thời được tôn trọng.
- **Kiểm tra thật:** `dm llm ping` gửi 1 câu tiếng Việt đơn giản và 1 câu `chat_json` qua OpenRouter, chi phí khoảng dưới $0.01.
- **Data mẫu:** `samples/P0.3/ping_result.json` (request, response, usage, cost, cache hit), `samples/P0.3/cost_log.jsonl`.
- **DoD:** test pass; ping thật thành công; chạy ping lần 2 thì lấy từ cache (cache hit).

### P0.4 I/O và schema cơ sở (`core/io.py`, `core/schemas.py`, `core/logging.py`)
- **Cách làm:**
  - `BaseRecord(id, schema_version)`.
  - `RunManifest`: phase, thời gian bắt đầu/kết thúc, git commit, hash cấu hình, model, prompt version, số bản ghi vào/ra, chi phí.
  - `write_jsonl` ghi kiểu atomic: ghi ra file tạm rồi đổi tên, để không bao giờ để lại file hỏng.
  - `append_jsonl` + `read_done_ids` phục vụ chạy tiếp từ chỗ dừng.
  - Đọc từng dòng, dòng sai schema thì báo lỗi kèm số dòng.
- **Test:**
  - Ghi rồi đọc lại khớp nhau, đúng UTF-8 tiếng Việt và NFC.
  - Bản ghi sai thì báo lỗi kèm số dòng.
  - Ghi atomic: lỗi giữa chừng thì file cũ còn nguyên.
  - Tiếp tục được: bỏ qua các id đã xong.
- **Data mẫu:** `samples/P0.4/example_records.jsonl`, `samples/P0.4/example_manifest.json`.
- **DoD:** test pass, mypy strict pass.

### P0.5 Khảo sát sách (**cần PDF**)
- **Cách làm:** theo mục 4.3. Thêm thư viện `pymupdf`.
- **Test:** script chạy trên một PDF nhỏ tự tạo trong test (2–3 trang có tiêu đề, header, footer), kiểm tra thống kê và phát hiện header đúng.
- **Data mẫu:** `samples/P0.5/` gồm thống kê sách, 3–5 trang mẫu (JSON + PNG), danh sách ứng viên header/footer.
- **Kết quả:** `docs/book_profile.md`, `tests/fixtures/pages/` (5–10 trang đại diện).
- **DoD:** `book_profile.md` mô tả được bằng quy tắc cụ thể:
  - Đầu chương, đầu bệnh, đầu mục trông thế nào.
  - Danh sách tên mục chuẩn của một bệnh.
  - Các kiểu lỗi OCR hay gặp, kèm ví dụ.
  - Header/footer.
  - Bảng.

### P0.6 Chọn chương mẫu
- **Cách làm:** dựa trên P0.5, đề xuất 1 chương có khoảng 5–10 bệnh, đa dạng (có bảng, có danh sách thuốc, có lỗi OCR), rồi **chủ dự án xác nhận**.
- **Kết quả:** `configs/default.yaml` → `pilot: {pages: [a, b], diseases: [...]}`.
- **DoD:** chủ dự án đã duyệt chương mẫu.

## 6. Cấu hình và prompt mới
- Chưa có prompt nghiệp vụ. P0.3 có một prompt `ping` để kiểm tra kết nối.
- Model mặc định đề xuất cho `models.yaml` sẽ được chốt ở P0.2. Bạn có thể chỉ định model OpenRouter muốn dùng.

## 7. Ước tính chi phí LLM
- P0.3 ping: khoảng 2–4 lời gọi, **dưới $0.01**.
- Các task khác không gọi LLM.

## 8. Gate của phase
- [ ] Mọi task từ P0.1 đến P0.6 có báo cáo và mẫu dữ liệu.
- [ ] Kiểm tra cục bộ (ruff, mypy, pytest, pre-commit) pass.
- [ ] Gọi được OpenRouter qua `llm_client`, cache hoạt động.
- [ ] `book_profile.md` mô tả được bằng quy tắc "đầu bệnh mới trông thế nào" và "mục Triệu chứng trông thế nào".
- [ ] Chương mẫu đã được duyệt.

## 9. Rủi ro và câu hỏi cần chủ dự án quyết định
1. **PDF sách:** cần chép vào `data/raw/` trước P0.5.
2. **Git commit:** sau mỗi task, mình có nên tạo commit không, hay bạn tự commit? Hiện tại mình chỉ `git init` và **không commit** nếu chưa được yêu cầu.
3. **Model OpenRouter:** bạn có model ưu tiên hoặc giới hạn ngân sách không? Nếu không, mình sẽ đề xuất ở P0.2.
4. **Rủi ro:** pre-commit cần tải hook từ GitHub ở lần chạy đầu. Nếu mạng chặn, sẽ chuyển sang dùng hook `local` chạy công cụ có sẵn trong môi trường uv.

## 10. Lịch sử thay đổi plan
| Ngày | Thay đổi | Lý do |
|---|---|---|
| 2026-10-19 | Tạo plan | — |
| 2026-10-20 | P0.2: model = `deepseek/deepseek-v4.1-flash-1017` cho mọi tác vụ, thêm `reasoning` vào ModelSpec; ngân sách $20 tổng / $1 cho P0 | Quyết định của chủ dự án |
| 2026-10-19 | P0.1: entry point `dm` đổi từ `cli:app` sang `cli:main` (ép UTF-8); hook whitespace/EOF bỏ qua `samples/`; thêm `.gitattributes` | Lỗi mã hóa tiếng Việt khi chuyển hướng output trên Windows; giữ output mẫu nguyên văn; tránh diff CRLF |
