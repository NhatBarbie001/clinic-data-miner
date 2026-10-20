"""Logging thống nhất: console (stderr) + file log riêng cho từng lần chạy.

Logger `dataminer` luôn ở mức DEBUG; mỗi handler tự giữ mức của mình, nên file log chi tiết
không làm console ồn hơn.
"""

import logging
from pathlib import Path

LOGGER_NAME = "dataminer"
FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"
_CONSOLE_MARK = "_dataminer_console"


def _root_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    return logger


def setup_logging(level: str | int = "INFO") -> logging.Logger:
    """Gắn (hoặc cập nhật mức) handler console. Gọi nhiều lần không nhân đôi."""
    logger = _root_logger()
    console = next((h for h in logger.handlers if getattr(h, _CONSOLE_MARK, False)), None)
    if console is None:
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(FORMAT, DATEFMT))
        setattr(console, _CONSOLE_MARK, True)
        logger.addHandler(console)
        logger.propagate = False  # tránh in lặp qua root logger
    console.setLevel(level)
    return logger


def add_file_handler(path: Path, level: str | int = "DEBUG") -> logging.Handler:
    """Ghi log `dataminer.*` ra file UTF-8. Nhớ gỡ bằng `remove_handler` khi xong."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(FORMAT, DATEFMT))
    _root_logger().addHandler(handler)
    return handler


def remove_handler(handler: logging.Handler) -> None:
    logging.getLogger(LOGGER_NAME).removeHandler(handler)
    handler.close()
