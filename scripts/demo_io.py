"""Minh họa P0.4: ghi/đọc JSONL, chạy dở → chạy tiếp, manifest, log, thông báo lỗi.

Chạy:  uv run python scripts/demo_io.py
Kết quả: data/p0_demo/ (progress.jsonl, records.jsonl, manifest.json, runs/*.json|*.log)

Mô phỏng một phase "xử lý 5 bệnh":
  Lần 1: xử lý được 3 bệnh thì tiến trình "chết" (đang ghi dở bản ghi thứ 4).
  Lần 2: tự dọn dòng ghi dở, bỏ qua 3 bệnh đã xong, xử lý 2 bệnh còn lại.
"""

import shutil
import sys

from pydantic import Field

from dataminer.core.config import get_settings
from dataminer.core.io import (
    DataFileError,
    append_jsonl,
    read_done_ids,
    read_jsonl,
    write_jsonl,
)
from dataminer.core.run import RunRecorder
from dataminer.core.schemas import BaseRecord, stable_id

PHASE = "p0_demo"
BOOK = "book01"
DISEASES = [
    ("Cúm", ["sốt", "ho", "đau mỏi người"], 12),
    ("Viêm khớp dạng thấp", ["đau khớp", "sưng khớp", "cứng khớp buổi sáng"], 120),
    ("Thoái hóa khớp gối", ["đau khớp gối", "lục khục khi cử động"], 140),
    ("Viêm loét dạ dày tá tràng", ["đau thượng vị", "ợ hơi", "buồn nôn"], 210),
    ("Tăng huyết áp", ["đau đầu", "chóng mặt", "ù tai"], 305),
]


class DiseaseNote(BaseRecord):
    """Bản ghi ví dụ - các phase thật sẽ định nghĩa schema riêng theo cách này."""

    name: str = Field(min_length=1)
    symptoms: list[str] = Field(min_length=1)
    page: int = Field(ge=1)


class SimulatedCrashError(RuntimeError):
    pass


def make(name: str, symptoms: list[str], page: int) -> DiseaseNote:
    return DiseaseNote(
        id=stable_id(BOOK, name, prefix="dz"), name=name, symptoms=symptoms, page=page
    )


def process(crash_after: int | None) -> None:
    settings = get_settings()
    out_dir = settings.paths.data_dir / PHASE
    progress = out_dir / "progress.jsonl"

    with RunRecorder(settings, PHASE) as run:
        done = read_done_ids(progress)  # tự dọn dòng ghi dở nếu có
        todo = [make(*d) for d in DISEASES]
        pending = [r for r in todo if r.id not in done]
        print(f"  đã xong từ trước: {len(done)} · cần xử lý: {len(pending)}")
        run.count("skipped_done", len(done))

        for i, record in enumerate(pending, start=1):
            if crash_after is not None and i > crash_after:
                with progress.open("a", encoding="utf-8") as fh:  # ghi dở rồi "chết"
                    fh.write('{"id": "' + record.id + '", "name": "' + record.name[:6])
                raise SimulatedCrashError(f"mô phỏng tiến trình chết khi đang ghi '{record.name}'")
            append_jsonl(progress, record)
            print(f"  ✓ {record.name}  ({record.id})")
        run.count("processed", len(pending))

        final = out_dir / "records.jsonl"
        n = write_jsonl(final, read_jsonl(progress, DiseaseNote))  # ghi atomic bản cuối
        run.add_output(final)
        run.count("records", n)
        run.note(f"hoàn tất {n}/{len(todo)} bệnh")
    print(f"  manifest: {run.manifest_path.relative_to(settings.paths.data_dir.parent)}")


def show_validation_errors() -> None:
    settings = get_settings()
    bad = settings.paths.data_dir / PHASE / "bad_example.jsonl"
    cases = {
        "thiếu trường + sai kiểu": (
            '{"id": "dz_1", "name": "Cúm", "symptoms": ["sốt"], "page": 12}\n'
            '{"id": "dz_2", "name": "Sởi", "page": "mười"}\n'
        ),
        "danh sách rỗng + trang âm": (
            '{"id": "dz_3", "name": "Thủy đậu", "symptoms": [], "page": -1}\n'
        ),
        "khóa gõ nhầm": '{"id": "dz_4", "name": "Lao", "symtoms": ["ho"], "page": 50}\n',
        "không phải JSON": '{"id": "dz_5", name: Lao}\n',
        "schema_version cũ": (
            '{"id": "dz_6", "schema_version": 0, "name": "Lao", "symptoms": ["ho"], "page": 50}\n'
        ),
    }
    for label, content in cases.items():
        bad.write_text(content, encoding="utf-8")
        try:
            list(read_jsonl(bad, DiseaseNote))
        except DataFileError as exc:
            print(f"  [{label}]\n    {exc}")
    bad.unlink()


def main() -> int:
    settings = get_settings()
    shutil.rmtree(settings.paths.data_dir / PHASE, ignore_errors=True)

    print("== Lần chạy 1 (sẽ 'chết' sau 3 bệnh)")
    try:
        process(crash_after=3)
    except SimulatedCrashError as exc:
        print(f"  ✗ {exc}")

    print("\n== Lần chạy 2 (chạy tiếp)")
    process(crash_after=None)

    print("\n== Thông báo lỗi khi đọc file có dòng sai")
    show_validation_errors()
    return 0


if __name__ == "__main__":
    sys.exit(main())
