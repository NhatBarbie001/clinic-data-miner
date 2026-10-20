"""Thông báo lỗi validate (Pydantic) bằng tiếng Việt - dùng chung cho cấu hình và dữ liệu."""

from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError


def describe_error(err: Mapping[str, Any]) -> str:
    """Một lỗi Pydantic → câu tiếng Việt (kèm giá trị đã nhận nếu có ích)."""
    kind = err["type"]
    ctx = err.get("ctx") or {}
    shown = f" (nhận: {err['input']!r})" if "input" in err and kind != "missing" else ""
    messages = {
        "missing": "thiếu giá trị bắt buộc",
        "extra_forbidden": "khóa không tồn tại",
        "less_than_equal": f"phải ≤ {ctx.get('le')}{shown}",
        "less_than": f"phải < {ctx.get('lt')}{shown}",
        "greater_than_equal": f"phải ≥ {ctx.get('ge')}{shown}",
        "greater_than": f"phải > {ctx.get('gt')}{shown}",
        "literal_error": (
            f"phải là một trong: {str(ctx.get('expected')).replace(' or ', ', ')}{shown}"
        ),
        "string_too_short": f"không được để trống{shown}",
        "too_short": f"phải có ít nhất {ctx.get('min_length')} phần tử{shown}",
        "too_long": f"chỉ được tối đa {ctx.get('max_length')} phần tử",
        "string_pattern_mismatch": f"không khớp mẫu {ctx.get('pattern')}{shown}",
        "int_parsing": f"phải là số nguyên{shown}",
        "int_type": f"phải là số nguyên{shown}",
        "float_parsing": f"phải là số{shown}",
        "float_type": f"phải là số{shown}",
        "bool_parsing": f"phải là true/false{shown}",
        "string_type": f"phải là chuỗi{shown}",
        "list_type": f"phải là danh sách{shown}",
        "dict_type": f"phải là đối tượng (key: value){shown}",
        "model_type": f"phải là đối tượng (key: value){shown}",
    }
    if kind in messages:
        return messages[kind]
    if kind == "value_error":
        return str(ctx.get("error", err["msg"]))
    return f"{err['msg']}{shown}"


def describe_validation(exc: ValidationError, root_label: str = "(bản ghi)") -> list[str]:
    """Mọi lỗi của một ValidationError → danh sách "đường.dẫn: lý do"."""
    lines = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err["loc"]) or root_label
        lines.append(f"{loc}: {describe_error(err)}")
    return lines
