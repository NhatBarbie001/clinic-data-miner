"""Kiểu dữ liệu và lỗi của LLM client."""

from typing import Any

from pydantic import BaseModel, Field


class LLMError(Exception):
    """Lỗi gọi LLM không thể tự khắc phục (sai key, hết credit, sai model, hết lượt retry...)."""


class CacheMissError(LLMError):
    """Chế độ replay nhưng request chưa có trong cache."""


class BudgetExceededError(LLMError):
    """Đã chi chạm ngân sách - dừng trước khi gọi API."""


class LLMJSONError(LLMError):
    """Model không trả về JSON hợp lệ theo schema sau khi đã yêu cầu sửa."""

    def __init__(self, message: str, last_output: str, errors: list[str]) -> None:
        super().__init__(message)
        self.last_output = last_output
        self.errors = errors


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0
    cost_usd: float = 0.0
    cost_estimated: bool = False  # True: tự tính từ bảng giá vì response thiếu usage.cost


class LLMResponse(BaseModel):
    content: str
    reasoning: str | None = None
    # Giữ nguyên để gửi lại ở lượt sau (hội thoại nhiều lượt có reasoning).
    reasoning_details: list[Any] | None = None
    model: str
    provider: str | None = None
    finish_reason: str | None = None
    usage: Usage = Field(default_factory=Usage)
    cached: bool = False
    latency_s: float = 0.0
    attempts: int = 0
    cache_key: str = ""

    def as_assistant_message(self) -> dict[str, Any]:
        """Message assistant để nối tiếp hội thoại (giữ reasoning_details nếu có)."""
        message: dict[str, Any] = {"role": "assistant", "content": self.content}
        if self.reasoning_details:
            message["reasoning_details"] = self.reasoning_details
        return message
