"""Fixture dùng chung cho mọi test.

`sample_book_for(seed)`: sách mẫu tổng hợp sinh MỘT LẦN mỗi seed cho cả phiên test (sinh một
cuốn mất ~1-1.5 giây vì phải dựng ảnh trang; trước đây nhiều test tự sinh lại cùng seed → bộ test
lên 87 giây). Các test chỉ ĐỌC sách dùng fixture này; test cần sinh mới (tính xác định, seed
khác, lệnh CLI make-sample-book) vẫn tự sinh.
"""

from collections.abc import Callable

import pytest

from dataminer.devtools.sample_book import SampleBook, make_sample_book

SampleBookFor = Callable[[int], SampleBook]


@pytest.fixture(scope="session")
def sample_book_for(tmp_path_factory: pytest.TempPathFactory) -> SampleBookFor:
    cache: dict[int, SampleBook] = {}

    def get(seed: int = 7) -> SampleBook:
        if seed not in cache:
            cache[seed] = make_sample_book(tmp_path_factory.mktemp(f"book_s{seed}"), seed=seed)
        return cache[seed]

    return get
