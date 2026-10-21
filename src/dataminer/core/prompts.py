"""Nạp prompt có version (nguyên tắc N6): `prompts/<id>.md` với front matter YAML.

    ---
    id: p1_fix_ocr
    version: v1
    task: fix_ocr
    notes: ...
    ---
    <nội dung prompt>

`id` phải trùng tên file; `version` bắt buộc - được ghi vào manifest mỗi lần chạy.
"""

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

from dataminer.core.errors_vi import describe_validation


class PromptError(Exception):
    """File prompt thiếu hoặc sai định dạng."""


class Prompt(BaseModel):
    id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    task: str | None = None
    notes: str | None = None
    text: str = Field(min_length=1)

    @property
    def ref(self) -> str:
        return f"{self.id}@{self.version}"


def load_prompt(prompts_dir: Path, prompt_id: str) -> Prompt:
    path = prompts_dir / f"{prompt_id}.md"
    if not path.is_file():
        raise PromptError(f"Không có file prompt {path}")
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise PromptError(f"{path.name}: thiếu front matter (--- id/version --- ở đầu file)")
    try:
        _, front, body = raw.split("---", 2)
        meta = yaml.safe_load(front) or {}
    except (ValueError, yaml.YAMLError) as exc:
        raise PromptError(f"{path.name}: front matter không hợp lệ ({exc})") from None
    if not isinstance(meta, dict):
        raise PromptError(f"{path.name}: front matter phải là mapping")
    try:
        prompt = Prompt.model_validate({**meta, "text": body.strip()})
    except ValidationError as exc:
        raise PromptError(f"{path.name}: " + "; ".join(describe_validation(exc))) from None
    if prompt.id != prompt_id:
        raise PromptError(f"{path.name}: id '{prompt.id}' không trùng tên file '{prompt_id}'")
    return prompt
