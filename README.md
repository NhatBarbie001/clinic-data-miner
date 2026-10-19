# Data-miner

Khai thác dữ liệu y khoa từ sách PDF tiếng Việt (đã OCR): hỏi đáp, truy vấn hàng loạt, RAG và sinh dữ liệu huấn luyện LLM.

- Yêu cầu bài toán: [problem.md](problem.md)
- Kế hoạch và quy trình làm việc: [plan.md](plan.md)
- Plan và báo cáo từng phase: [docs/phases/](docs/phases/)
- Dữ liệu mẫu của từng task: [samples/](samples/)

## Cài đặt

Cần [uv](https://docs.astral.sh/uv/) và Python ≥ 3.11.

```bash
uv sync                      # tạo .venv và cài deps theo uv.lock
cp .env.example .env         # điền OPENROUTER_API_KEY
uv run pre-commit install    # bật kiểm tra tự động trước mỗi commit
```

Chép file PDF sách vào `data/raw/`.

## Lệnh thường dùng

```bash
uv run dm --help             # danh sách lệnh
uv run dm info               # kiểm tra môi trường và trạng thái dự án

uv run pytest                # test (bỏ qua test gọi API thật)
uv run pytest -m live        # chỉ chạy test gọi API thật (tốn tiền)
uv run ruff check .          # lint
uv run ruff format .         # format
uv run mypy                  # type check (strict)
uv run pre-commit run --all-files
```

## Cấu trúc

```
configs/   cấu hình YAML          prompts/   prompt có version
src/dataminer/                    tests/     unit · integration · fixtures
  core/ ingest/ structure/        eval/      bộ câu hỏi chuẩn + report
  index/ kb/ qa/ batch/           samples/   mẫu dữ liệu nhỏ theo task (commit)
  datagen/ evaluation/ cli.py     data/      artifact lớn (KHÔNG commit)
```
