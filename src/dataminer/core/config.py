"""Cấu hình dự án: một nguồn duy nhất, có kiểm tra kiểu.

Các lớp cấu hình (lớp sau ghi đè lớp trước, gộp sâu):
    1. configs/default.yaml              giá trị mặc định (commit)
    2. configs/models.yaml               tác vụ → model (commit), nạp vào khóa `models`
    3. configs/books/<book_id>/book.yaml HỒ SƠ SÁCH: thiết lập riêng của cuốn đang chạy (commit)
    4. configs/local.yaml                tùy chỉnh máy cá nhân (KHÔNG commit, tùy chọn)
    5. Biến môi trường                   `DM__LLM__CONCURRENCY=8` (giá trị parse như YAML);
                                         API key đọc từ `OPENROUTER_API_KEY`.
Sách đang chạy: `dm --book <id>` > `DM__PROJECT__BOOK_ID` > local.yaml > default.yaml.
Chuỗi `{book_id}` trong cấu hình (đường dẫn dữ liệu, từ điển…) được thay bằng sách đang chạy.
Biến môi trường lấy từ `.env` rồi `os.environ` (os.environ thắng).

Xem docs/phases/P0/P0.2_plan.md.
"""

import difflib
import hashlib
import json
import os
import types
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal, Union, get_args, get_origin

import yaml
from dotenv import dotenv_values
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    SecretStr,
    ValidationError,
    model_validator,
)

from dataminer.core.errors_vi import describe_error

ENV_PREFIX = "DM__"
API_KEY_ENV = "OPENROUTER_API_KEY"
REQUIRED_TASKS: tuple[str, ...] = (
    "ping",
    "fix_ocr",
    "classify",
    "extract",
    "qa",
    "judge",
    "datagen",
)

DEFAULT_FILE = "configs/default.yaml"
MODELS_FILE = "configs/models.yaml"
LOCAL_FILE = "configs/local.yaml"
BOOKS_DIR = "configs/books"  # configs/books/<book_id>/book.yaml
BOOK_PLACEHOLDER = "{book_id}"


class ConfigError(Exception):
    """Cấu hình không hợp lệ hoặc thiếu. Thông điệp đã được định dạng cho người đọc."""


def find_project_root(start: Path | None = None) -> Path:
    """Tìm gốc repo: thư mục gần nhất (đi ngược lên) có `pyproject.toml`."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    raise FileNotFoundError("Không tìm thấy pyproject.toml - hãy chạy trong thư mục dự án.")


# --------------------------------------------------------------------------- schema


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProjectCfg(_Strict):
    book_id: str = Field(pattern=r"^[a-z0-9_-]+$")
    book_file: str
    # phạm vi nội dung chính (trang PDF, gồm 2 đầu) dùng cho `--scope all`; None = cả file
    content_pages: tuple[int, int] | None = None


class PathsCfg(_Strict):
    raw_dir: Path
    data_dir: Path
    cache_dir: Path
    samples_dir: Path
    prompts_dir: Path
    eval_dir: Path


class LLMCfg(_Strict):
    base_url: str
    mode: Literal["live", "replay", "refresh"] = "live"
    concurrency: int = Field(default=4, ge=1, le=64)
    max_retries: int = Field(default=4, ge=0, le=10)
    timeout_s: float = Field(default=120, gt=0)
    backoff_base_s: float = Field(default=1.0, ge=0)
    backoff_max_s: float = Field(default=30.0, ge=0)
    json_retries: int = Field(default=2, ge=0, le=5)
    api_key: SecretStr | None = None


NonNegUSD = Annotated[float, Field(ge=0)]


class BudgetCfg(_Strict):
    total_usd: NonNegUSD
    per_task_usd: dict[str, NonNegUSD] = Field(default_factory=dict)


class ReasoningCfg(_Strict):
    """Tham số `reasoning` của OpenRouter (bật chế độ suy luận của model)."""

    enabled: bool = False
    effort: Literal["low", "medium", "high"] | None = None


class ModelSpec(_Strict):
    model: str = Field(min_length=1)
    temperature: float = Field(default=0.0, ge=0, le=2)
    max_tokens: int = Field(default=4096, ge=1)
    reasoning: ReasoningCfg = Field(default_factory=ReasoningCfg)
    fallbacks: list[str] = Field(default_factory=list)


class PilotCfg(_Strict):
    page_start: int | None = Field(default=None, ge=1)
    page_end: int | None = Field(default=None, ge=1)
    diseases: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_range(self) -> "PilotCfg":
        if (self.page_start is None) != (self.page_end is None):
            raise ValueError("page_start và page_end phải cùng có hoặc cùng để trống")
        if (
            self.page_start is not None
            and self.page_end is not None
            and self.page_start > self.page_end
        ):
            raise ValueError(f"page_start ({self.page_start}) phải ≤ page_end ({self.page_end})")
        return self


class FurnitureCfg(_Strict):
    """P1.2 - nhận diện header/footer/số trang."""

    top_zone: float = Field(default=0.09, gt=0, lt=0.5)  # tỉ lệ chiều cao trang
    bottom_zone: float = Field(default=0.09, gt=0, lt=0.5)
    min_repeat_pages: int = Field(default=2, ge=2)  # lặp ở ≥ n trang → header/footer chạy
    small_ratio: float = Field(default=0.95, gt=0, le=1)  # chữ ≤ ratio × thân bài, nằm ở lề


class BlocksCfg(_Strict):
    """P1.3 - dựng block."""

    bullet_markers: list[str] = Field(default_factory=lambda: ["-", "•", "–", "+"])
    para_gap_ratio: float = Field(default=0.25, gt=0)  # khoảng dôi ≥ ratio × cỡ chữ → đoạn mới
    x_tolerance: float = Field(default=3.0, ge=0)  # sai số lề trái (pt)
    join_across_pages: bool = True
    table_min_rows: int = Field(default=2, ge=2)
    table_min_cells: int = Field(default=2, ge=2)
    heading_size_delta: float = Field(default=1.5, gt=0)  # chỉ dựa cỡ chữ: phải ≥ thân bài + delta
    # nhận bảng = các dòng cùng hàng ngang. Sách in 2 cột phải TẮT: 2 cột cạnh nhau trông như bảng
    detect_tables: bool = True
    # bỏ gạch nối cuối dòng khi nối 2 dòng ("dis-" + "ease" → "disease") - sách tiếng Anh
    dehyphenate: bool = False


class FixCfg(_Strict):
    """P1.4 - sửa lỗi OCR bằng LLM + guard theo token."""

    enabled: bool = True
    prompt: str = "p1_fix_ocr"  # file prompts/<prompt>.md
    blocks_per_call: int = Field(default=25, ge=1, le=200)
    max_changed_ratio: float = Field(default=0.35, gt=0, le=1)  # > tỉ lệ này → từ chối cả block
    min_similarity: float = Field(default=0.6, ge=0, le=1)  # giống nhau (đã bỏ dấu) tối thiểu
    glossary: str = "configs/books/{book_id}/glossary.yaml"  # thuật ngữ được bảo vệ (gốc repo)


class P1Cfg(_Strict):
    """Phase P1 - trích xuất và làm sạch text (các task sau bổ sung nhóm của mình)."""

    furniture: FurnitureCfg = Field(default_factory=FurnitureCfg)
    blocks: BlocksCfg = Field(default_factory=BlocksCfg)
    fix: FixCfg = Field(default_factory=FixCfg)


class TocCfg(_Strict):
    """P2.1 - mục lục."""

    pages: Literal["auto"] | tuple[int, int] = "auto"  # auto = tự tìm; hoặc [a, b] (trang PDF)
    search_pages: int = Field(default=15, ge=1)  # tìm trong n trang đầu
    min_entries: int = Field(default=2, ge=1)  # trang có ≥ n dòng chấm dẫn → trang mục lục

    @model_validator(mode="after")
    def _check_pages(self) -> "TocCfg":
        if self.pages != "auto" and not 1 <= self.pages[0] <= self.pages[1]:
            raise ValueError(f"pages phải là 'auto' hoặc [a, b] với 1 ≤ a ≤ b, nhận {self.pages}")
        return self


class HeadingsCfg(_Strict):
    """P2.2 - phân cấp tiêu đề."""

    disease_size_delta: float = Field(default=1.5, gt=0)  # IN HOA, không số, cỡ ≥ thân bài + delta
    use_toc: bool = True  # dùng mục lục để xác nhận/sửa cấp
    toc_match_min: float = Field(default=0.85, gt=0, le=1)  # độ giống tối thiểu khi khớp gần
    # mục lục có liệt kê từng bệnh không? true: bệnh vắng mặt trong mục lục → đáng ngờ (sách mẫu);
    # false: mục lục chỉ tới chương (sách IASP) → không hạ tin cậy bệnh
    toc_lists_diseases: bool = True
    llm_fallback: bool = True  # tiêu đề còn tin cậy thấp → hỏi LLM (tác vụ `classify`)
    prompt: str = "p2_classify_heading"


class SectionsCfg(_Strict):
    """P2.4 - ánh xạ loại mục."""

    map: str = "configs/books/{book_id}/section_map.yaml"  # tên mục → loại (gốc repo)
    fuzzy_min: float = Field(default=0.9, gt=0, le=1)  # khớp gần (chịu lỗi OCR nhầm 1 ký tự)
    llm_fallback: bool = True  # tên mục lạ → LLM đề xuất → hàng đợi duyệt
    prompt: str = "p2_classify_section"
    context_chars: int = Field(default=400, ge=0)  # phần đầu nội dung mục gửi kèm cho LLM


class P2Cfg(_Strict):
    """Phase P2 - dựng cây cấu trúc (các task sau bổ sung nhóm của mình)."""

    toc: TocCfg = Field(default_factory=TocCfg)
    headings: HeadingsCfg = Field(default_factory=HeadingsCfg)
    sections: SectionsCfg = Field(default_factory=SectionsCfg)


class Settings(_Strict):
    project: ProjectCfg
    paths: PathsCfg
    llm: LLMCfg
    budget: BudgetCfg
    models: dict[str, ModelSpec]
    pilot: PilotCfg = Field(default_factory=PilotCfg)
    p1: P1Cfg = Field(default_factory=P1Cfg)
    p2: P2Cfg = Field(default_factory=P2Cfg)

    _fingerprint: str = PrivateAttr(default="")
    _sources: list[str] = PrivateAttr(default_factory=list)
    _root: Path = PrivateAttr(default=Path())

    @model_validator(mode="after")
    def _check_tasks(self) -> "Settings":
        missing = [t for t in REQUIRED_TASKS if t not in self.models]
        if missing:
            raise ValueError(f"models: thiếu tác vụ bắt buộc: {', '.join(missing)}")
        unknown = sorted(set(self.budget.per_task_usd) - set(self.models))
        if unknown:
            raise ValueError(f"budget.per_task_usd: tác vụ không có trong models: {unknown}")
        return self

    # ------------------------------------------------------------- tiện ích

    def model_for(self, task: str) -> ModelSpec:
        """ModelSpec cho tác vụ; lỗi liệt kê tác vụ hợp lệ nếu không tồn tại."""
        try:
            return self.models[task]
        except KeyError:
            valid = ", ".join(sorted(self.models))
            raise ConfigError(f"Không có tác vụ '{task}' trong models. Hợp lệ: {valid}") from None

    def require_api_key(self) -> str:
        """API key OpenRouter; lỗi kèm hướng dẫn nếu chưa đặt."""
        if self.llm.api_key is None or not self.llm.api_key.get_secret_value():
            raise ConfigError(
                f"Chưa có {API_KEY_ENV}. Copy .env.example thành .env và điền key "
                "(tạo key tại https://openrouter.ai/keys)."
            )
        return self.llm.api_key.get_secret_value()

    def fingerprint(self) -> str:
        """Hash ngắn của cấu hình (không gồm bí mật, đường dẫn tương đối) - ghi vào manifest."""
        return self._fingerprint

    @property
    def root(self) -> Path:
        """Gốc dự án (thư mục có pyproject.toml) - mọi đường dẫn tương đối tính từ đây."""
        return self._root

    def from_root(self, relative: str) -> Path:
        """Đường dẫn tương đối gốc dự án (vd. từ điển `configs/books/book01/section_map.yaml`);
        `{book_id}` được thay bằng sách đang chạy."""
        return self._root / relative.replace(BOOK_PLACEHOLDER, self.project.book_id)

    @property
    def sources(self) -> list[str]:
        """Các lớp cấu hình đã được áp dụng, theo thứ tự."""
        return list(self._sources)

    def to_display_dict(self) -> dict[str, Any]:
        """Cấu hình dạng dict để hiển thị - API key đã bị che."""
        data: dict[str, Any] = self.model_dump(mode="json")
        data["llm"]["api_key"] = "***(đã đặt)" if self.llm.api_key else "(chưa đặt)"
        return data


# --------------------------------------------------------------------------- nạp


def _read_yaml(path: Path, *, required: bool) -> dict[str, Any] | None:
    if not path.is_file():
        if required:
            raise ConfigError(f"Thiếu file cấu hình bắt buộc: {path}")
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" dòng {mark.line + 1}, cột {mark.column + 1}" if mark else ""
        problem = getattr(exc, "problem", None) or str(exc)
        raise ConfigError(f"{path}: YAML không hợp lệ ở{where}: {problem}") from None
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"{path}: nội dung gốc phải là mapping (key: value)")
    return data


def _env_layer(env: Mapping[str, str]) -> dict[str, Any]:
    """`DM__LLM__CONCURRENCY=8` → {"llm": {"concurrency": 8}}."""
    layer: dict[str, Any] = {}
    for key, raw in env.items():
        if not key.upper().startswith(ENV_PREFIX):
            continue
        parts = [p.lower() for p in key[len(ENV_PREFIX) :].split("__") if p]
        if not parts:
            continue
        try:
            value = yaml.safe_load(raw) if raw != "" else ""
        except yaml.YAMLError:
            value = raw
        node = layer
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    return layer


def _merge(
    base: dict[str, Any],
    override: Mapping[str, Any],
    label: str,
    sources: dict[str, str],
    prefix: str = "",
) -> None:
    """Gộp sâu `override` vào `base` (tại chỗ) và ghi lại nguồn của từng khóa."""
    for key, value in override.items():
        path = f"{prefix}{key}"
        if isinstance(value, Mapping) and isinstance(base.get(key), dict):
            sources.setdefault(path, label)
            _merge(base[key], value, label, sources, f"{path}.")
        else:
            base[key] = json.loads(json.dumps(value, default=str))  # bản sao sâu
            sources[path] = label
            # khóa con của giá trị bị thay thế giờ thuộc về lớp này
            for sub in [s for s in sources if s.startswith(f"{path}.")]:
                sources[sub] = label


def _source_of(loc: tuple[str, ...], sources: Mapping[str, str], order: list[str]) -> str | None:
    """Lớp cấu hình gây ra giá trị tại `loc`.

    Với lỗi ở cấp nhóm (vd. `pilot` sai do page_start > page_end), lấy lớp *sau cùng*
    đã đặt bất kỳ khóa nào trong nhóm - đó là lớp vừa làm nhóm trở nên sai.
    """
    rank = {label: i for i, label in enumerate(order)}
    for end in range(len(loc), 0, -1):
        path = ".".join(loc[:end])
        labels = [
            label for key, label in sources.items() if key == path or key.startswith(f"{path}.")
        ]
        if labels:
            return max(labels, key=lambda label: rank.get(label, -1))
    return None


def _model_at(loc: tuple[str, ...]) -> type[BaseModel] | None:
    """Kiểu BaseModel tương ứng với đường dẫn khóa (để gợi ý tên khóa đúng)."""
    current: Any = Settings
    for part in loc:
        if isinstance(current, type) and issubclass(current, BaseModel):
            field = current.model_fields.get(part)
            if field is None:
                return None
            current = field.annotation
        elif get_origin(current) is dict:
            current = get_args(current)[1]
        else:
            return None
        if get_origin(current) in (Union, types.UnionType):
            models = [a for a in get_args(current) if isinstance(a, type)]
            current = next((a for a in models if issubclass(a, BaseModel)), None)
    if isinstance(current, type) and issubclass(current, BaseModel):
        return current
    return None


def _format_errors(exc: ValidationError, sources: Mapping[str, str], order: list[str]) -> str:
    lines: list[str] = []
    for err in exc.errors():
        loc = tuple(str(p) for p in err["loc"])
        key = ".".join(loc) or "(gốc)"
        msg = describe_error(err)
        if err["type"] == "extra_forbidden":
            parent = _model_at(loc[:-1])
            if parent is not None:
                close = difflib.get_close_matches(loc[-1], list(parent.model_fields), n=1)
                if close:
                    msg += f" - có phải ý bạn là '{close[0]}'?"
        source = _source_of(loc, sources, order)
        suffix = f"  [nguồn: {source}]" if source else ""
        if key == "(gốc)" and msg.startswith(("models:", "budget.")):
            lines.append(f"  - {msg}")
        else:
            lines.append(f"  - {key}: {msg}{suffix}")
    return f"Cấu hình không hợp lệ ({len(lines)} lỗi):\n" + "\n".join(lines)


def _read_env(root: Path) -> dict[str, str]:
    env = {k: v for k, v in dotenv_values(root / ".env").items() if v is not None}
    env.update(os.environ)
    return env


def _substitute(value: Any, book_id: str) -> Any:
    """Thay `{book_id}` trong mọi chuỗi của cấu hình (đệ quy)."""
    if isinstance(value, str):
        return value.replace(BOOK_PLACEHOLDER, book_id)
    if isinstance(value, dict):
        return {k: _substitute(v, book_id) for k, v in value.items()}
    if isinstance(value, list):
        return [_substitute(v, book_id) for v in value]
    return value


def load_settings(
    root: Path | None = None, env: Mapping[str, str] | None = None, *, book: str | None = None
) -> Settings:
    """Nạp và kiểm tra cấu hình.

    Args:
        root: gốc dự án; mặc định tìm từ thư mục hiện tại.
        env: biến môi trường; mặc định `.env` + `os.environ`. Test truyền dict riêng.
        book: sách cần chạy; mặc định `dm --book` > env > local.yaml > default.yaml.
    """
    root = (root or find_project_root()).resolve()
    if env is None:
        env = _read_env(root)

    merged: dict[str, Any] = {}
    sources: dict[str, str] = {}
    applied: list[str] = []

    default = _read_yaml(root / DEFAULT_FILE, required=True) or {}
    _merge(merged, default, DEFAULT_FILE, sources)
    applied.append(DEFAULT_FILE)

    models = _read_yaml(root / MODELS_FILE, required=True) or {}
    _merge(merged, {"models": models}, MODELS_FILE, sources)
    applied.append(MODELS_FILE)

    local = _read_yaml(root / LOCAL_FILE, required=False)
    env_layer = _env_layer(env)

    # Sách đang chạy → nạp hồ sơ sách (giữa models.yaml và local.yaml).
    book_id = book
    for layer in (env_layer, local or {}, merged):
        if book_id:
            break
        project = layer.get("project")
        if isinstance(project, dict) and isinstance(project.get("book_id"), str):
            book_id = project["book_id"]
    profile_file = f"{BOOKS_DIR}/{book_id}/book.yaml"
    profile = _read_yaml(root / profile_file, required=False) if book_id else None
    if profile is not None:
        _merge(merged, profile, profile_file, sources)
        applied.append(profile_file)

    if local is not None:
        _merge(merged, local, LOCAL_FILE, sources)
        applied.append(LOCAL_FILE)

    if env_layer:
        _merge(merged, env_layer, "env", sources)
        names = sorted(k for k in env if k.upper().startswith(ENV_PREFIX))
        applied.append("env: " + ", ".join(names))

    if book_id:
        merged.setdefault("project", {})["book_id"] = book_id
        merged = _substitute(merged, book_id)

    # Fingerprint: trước khi thêm bí mật và resolve đường dẫn → ổn định giữa các máy.
    canonical = json.dumps(merged, sort_keys=True, ensure_ascii=False, default=str)
    fingerprint = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]

    api_key = env.get(API_KEY_ENV)
    if api_key:
        merged.setdefault("llm", {})["api_key"] = api_key
        applied.append(f"env: {API_KEY_ENV}")

    paths = merged.get("paths")
    if isinstance(paths, dict):
        for name, value in paths.items():
            if isinstance(value, str) and not Path(value).is_absolute():
                paths[name] = str(root / value)

    try:
        settings = Settings.model_validate(merged)
    except ValidationError as exc:
        order = [DEFAULT_FILE, MODELS_FILE, profile_file, LOCAL_FILE, "env"]
        raise ConfigError(_format_errors(exc, sources, order)) from None

    settings._fingerprint = fingerprint
    settings._sources = applied
    settings._root = root
    return settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cấu hình của dự án hiện tại (nạp một lần, dùng lại)."""
    return load_settings()


def reset_settings_cache() -> None:
    """Xóa cache của `get_settings()` (dùng sau khi sửa cấu hình trong cùng tiến trình)."""
    get_settings.cache_clear()
