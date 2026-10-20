"""Schema cơ sở: lớp cha cho mọi bản ghi, ID ổn định, manifest của một lần chạy.

Mỗi phase định nghĩa schema nghiệp vụ của mình bằng cách kế thừa `BaseRecord`
và tăng `SCHEMA_VERSION` mỗi khi đổi cấu trúc (N2).
"""

import hashlib
import unicodedata
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BaseRecord(BaseModel):
    """Lớp cha của mọi bản ghi lưu ra file JSONL. Khóa lạ bị từ chối."""

    model_config = ConfigDict(extra="forbid")

    SCHEMA_VERSION: ClassVar[int] = 1

    id: str = Field(min_length=1)
    # Tự điền = SCHEMA_VERSION khi tạo mới; khi đọc file mà khác → báo lỗi.
    schema_version: int = 0

    @model_validator(mode="before")
    @classmethod
    def _fill_version(cls, data: Any) -> Any:
        if isinstance(data, dict) and "schema_version" not in data:
            return {**data, "schema_version": cls.SCHEMA_VERSION}
        return data

    @model_validator(mode="after")
    def _check_version(self) -> "BaseRecord":
        expected = type(self).SCHEMA_VERSION
        if self.schema_version != expected:
            raise ValueError(
                f"schema_version={self.schema_version} nhưng code hiện tại của "
                f"{type(self).__name__} là v{expected} - file được tạo bởi phiên bản code khác, "
                "hãy chạy lại phase sinh ra file này"
            )
        return self


def stable_id(*parts: object, prefix: str = "") -> str:
    """ID ổn định từ nội dung (N3): cùng `parts` → cùng ID mỗi lần chạy.

    Các phần được chuẩn hóa Unicode NFC (chữ Việt dựng sẵn/tổ hợp cho cùng ID) và nối bằng
    ký tự phân cách riêng, nên ("ab", "c") khác ("a", "bc").
    """
    joined = "\x1f".join(unicodedata.normalize("NFC", str(p)) for p in parts)
    digest = hashlib.sha1(joined.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}" if prefix else digest


class FileInfo(BaseModel):
    """Một file vào/ra của lần chạy."""

    path: str  # tương đối với gốc repo (dạng /), để manifest giống nhau giữa các máy
    records: int | None = None  # số dòng không trống (JSONL); None với file nhị phân
    sha256: str
    bytes: int


class LLMUsage(BaseModel):
    calls: int = 0
    cost_usd: float = 0.0


class RunManifest(BaseModel):
    """Manifest của một lần chạy phase (N8)."""

    run_id: str
    phase: str
    status: Literal["running", "success", "failed"] = "running"
    started_at: str
    finished_at: str | None = None
    duration_s: float | None = None
    git_commit: str | None = None
    git_dirty: bool | None = None
    config_fingerprint: str
    models: dict[str, str] = Field(default_factory=dict)
    prompts: dict[str, str] = Field(default_factory=dict)
    inputs: list[FileInfo] = Field(default_factory=list)
    outputs: list[FileInfo] = Field(default_factory=list)
    llm: LLMUsage = Field(default_factory=LLMUsage)
    counts: dict[str, int] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
    error: str | None = None
