"""Chỉ tiêu "đạt" cho sách KHÔNG có đáp án (docs/phases/P2R/plan.md mục 5): đếm độc lập + so.

Mỗi hàm nhận dữ liệu đã rút gọn (danh sách mã, số đếm, nút) và trả `CheckResult` - ai gọi tự
lo phần đếm độc lập trên PDF (không được dùng lại code của bộ luật đang kiểm).
"""

import re
from collections.abc import Callable, Sequence

from pydantic import BaseModel, Field

from dataminer.model.tree import Node

RE_SEQ_CODE = re.compile(r"^(?P<group>[^-]+)-(?P<main>\d+)(?:\.(?P<sub>\d+))?$")


class CheckResult(BaseModel):
    id: str  # "A2"
    name: str
    value: str  # kết quả đo, dạng đọc được
    threshold: str
    passed: bool
    details: list[str] = Field(default_factory=list)

    def line(self) -> str:
        mark = "ĐẠT" if self.passed else "CHƯA ĐẠT"
        return f"{self.id} {self.name}: {self.value} (ngưỡng {self.threshold}) → {mark}"


def code_sequence(codes: Sequence[str], allowed_gaps: Sequence[str] = ()) -> CheckResult:
    """A2 - mã trong mỗi nhóm phải LIÊN TIẾP theo thứ tự đọc: XI-1, XI-2, …; mã con IX-7.1,
    IX-7.2 sau IX-7 (hoặc mở đầu số mới: I-16.1). Nhảy số = sót hội chứng hoặc đọc sai mã.
    `allowed_gaps`: chỗ sách TỰ nhảy (đã soát tay), dạng "XI-3→XI-5"."""
    last: dict[str, tuple[int, int]] = {}
    seen: set[str] = set()
    problems: list[str] = []
    for code in codes:
        m = RE_SEQ_CODE.match(code)
        if not m:
            problems.append(f"mã không đúng dạng: {code}")
            continue
        if code in seen:
            problems.append(f"mã trùng: {code}")
            continue
        seen.add(code)
        group, main, sub = m.group("group"), int(m.group("main")), int(m.group("sub") or 0)
        prev_main, prev_sub = last.get(group, (0, 0))
        # cùng số chính → mã con kế tiếp; số chính mới → +1, mã con 0 hoặc .1
        ok = sub == prev_sub + 1 if main == prev_main else main == prev_main + 1 and sub in (0, 1)
        if not ok:
            before = f"{group}-{prev_main}" + (f".{prev_sub}" if prev_sub else "")
            jump = f"{before if prev_main else '(đầu nhóm)'}→{code}"
            if jump not in allowed_gaps:
                problems.append(jump)
        last[group] = (main, sub)
    return CheckResult(
        id="A2",
        name="mã hội chứng liên tiếp trong mỗi nhóm",
        value=f"{len(problems)} chỗ nhảy/trùng trên {len(codes)} mã",
        threshold="0 (trừ chỗ sách tự nhảy đã liệt kê)",
        passed=not problems,
        details=problems,
    )


def count_match(found: int, expected: int, *, tolerance: float = 0.01) -> CheckResult:
    """A3 - số hội chứng trong cây ↔ số mã đếm độc lập trên PDF, lệch ≤ `tolerance`."""
    diff = abs(found - expected) / expected if expected else float(found > 0)
    return CheckResult(
        id="A3",
        name="số hội chứng có mã (cây ↔ đếm độc lập trên PDF)",
        value=f"cây {found} · PDF {expected} · lệch {diff:.1%}",
        threshold=f"≤ {tolerance:.0%}",
        passed=diff <= tolerance,
    )


def section_coverage(
    syndromes: Sequence[Node],
    children: Callable[[Node], Sequence[Node]],
    required: re.Pattern[str],
    *,
    minimum: float = 0.9,
) -> CheckResult:
    """A4 - tỉ lệ hội chứng có ít nhất một mục con khớp `required` (vd. Definition hoặc Code)."""
    missing = [
        f"'{s.display_title}' (PDF {s.page_start})"
        for s in syndromes
        if not any(required.match(c.title) for c in children(s))
    ]
    share = 1 - len(missing) / len(syndromes) if syndromes else 0.0
    return CheckResult(
        id="A4",
        name=f"hội chứng có mục chính ({required.pattern})",
        value=f"{share:.1%} ({len(syndromes) - len(missing)}/{len(syndromes)})",
        threshold=f"≥ {minimum:.0%}",
        passed=share >= minimum,
        details=missing,
    )
