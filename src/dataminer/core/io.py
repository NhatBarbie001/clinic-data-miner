"""Đọc/ghi dữ liệu an toàn (N1, N2, N4).

- Ghi atomic: ghi ra file tạm cùng thư mục rồi `os.replace` → không bao giờ để lại file hỏng.
- Đọc có validate từng dòng theo schema; lỗi báo `file:dòng: trường: lý do`.
- Append từng bản ghi + đọc lại các `id` đã xong → chạy tiếp sau khi bị ngắt.
- Không sửa nội dung: ghi rồi đọc lại giống hệt từng byte (chuẩn hóa văn bản là việc của P1).
"""

import contextlib
import hashlib
import json
import os
import tempfile
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from dataminer.core.errors_vi import describe_validation
from dataminer.core.schemas import FileInfo

T = TypeVar("T", bound=BaseModel)


class DataFileError(Exception):
    """File dữ liệu không đọc được hoặc có bản ghi sai schema."""


def _dumps(record: BaseModel) -> str:
    return json.dumps(record.model_dump(mode="json"), ensure_ascii=False)


def _atomic_write(path: Path, lines: Iterable[str]) -> int:
    """Ghi các dòng vào file tạm rồi thay thế `path`. Trả số dòng đã ghi."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    count = 0
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            for line in lines:
                fh.write(line)
                fh.write("\n")
                count += 1
            fh.flush()
            os.fsync(fh.fileno())
        tmp.replace(path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    return count


def write_jsonl(path: Path, records: Iterable[BaseModel]) -> int:
    """Ghi toàn bộ bản ghi ra JSONL (atomic). Lỗi giữa chừng → file cũ nguyên vẹn."""
    return _atomic_write(path, (_dumps(r) for r in records))


def append_jsonl(path: Path, record: BaseModel) -> None:
    """Thêm một bản ghi vào cuối file (dùng cho bước xử lý từng phần, chạy tiếp được)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(_dumps(record) + "\n")
        fh.flush()


def read_jsonl(path: Path, model: type[T]) -> Iterator[T]:
    """Đọc từng dòng (không nạp cả file) và validate theo `model`. Bỏ dòng trống."""
    if not path.is_file():
        raise DataFileError(f"{path}: không tồn tại")
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                raise DataFileError(
                    f"{path.name}:{lineno}: không phải JSON hợp lệ ({exc.msg}, cột {exc.colno})"
                ) from None
            try:
                yield model.model_validate(data)
            except ValidationError as exc:
                detail = "; ".join(describe_validation(exc))
                raise DataFileError(f"{path.name}:{lineno}: {detail}") from None


def repair_tail(path: Path) -> bool:
    """Cắt dòng cuối bị ghi dở (tiến trình chết giữa lúc append). Trả True nếu đã cắt."""
    if not path.is_file():
        return False
    raw = path.read_bytes()
    if not raw or raw.endswith(b"\n"):
        return False
    cut = raw.rfind(b"\n") + 1  # 0 nếu cả file chỉ có một dòng dở
    tail = raw[cut:]
    try:
        json.loads(tail)
    except ValueError:
        with path.open("r+b") as fh:
            fh.truncate(cut)
        return True
    # Dòng cuối là JSON đầy đủ, chỉ thiếu "\n" → bổ sung cho các lần append sau.
    with path.open("ab") as fh:
        fh.write(b"\n")
    return False


def read_done_ids(path: Path) -> set[str]:
    """Tập `id` đã có trong file (không validate - nhanh). Tự dọn dòng cuối ghi dở."""
    if not path.is_file():
        return set()
    repair_tail(path)
    done: set[str] = set()
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                done.add(str(json.loads(line)["id"]))
            except (json.JSONDecodeError, KeyError, TypeError):
                raise DataFileError(f"{path.name}:{lineno}: dòng hỏng hoặc thiếu 'id'") from None
    return done


def write_json(path: Path, data: Any) -> None:
    """Ghi JSON thường (atomic), thụt lề cho dễ đọc."""
    if isinstance(data, BaseModel):
        data = data.model_dump(mode="json")
    text = json.dumps(data, ensure_ascii=False, indent=2)
    _atomic_write(path, [text])


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise DataFileError(f"{path}: không tồn tại") from None
    except json.JSONDecodeError as exc:
        raise DataFileError(f"{path.name}: JSON lỗi ở dòng {exc.lineno}: {exc.msg}") from None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_records(path: Path) -> int:
    """Số dòng không trống."""
    with path.open("rb") as fh:
        return sum(1 for line in fh if line.strip())


def file_info(path: Path, root: Path, *, records: bool = True) -> FileInfo:
    """Thông tin file cho manifest; đường dẫn tương đối với `root` nếu được."""
    resolved = path.resolve()
    rel = resolved
    with contextlib.suppress(ValueError):
        rel = resolved.relative_to(root.resolve())
    return FileInfo(
        path=rel.as_posix(),
        records=count_records(path) if records else None,
        sha256=sha256_file(path),
        bytes=path.stat().st_size,
    )
