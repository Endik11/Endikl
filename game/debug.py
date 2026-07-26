from __future__ import annotations

import logging
import platform
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pygame


ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = ROOT_DIR / "saves" / "game.log"
LOGGER_NAME = "mortal_end"
GAME_VERSION = "0.1.0-stage1"


class WindowsSafeRotatingFileHandler(RotatingFileHandler):
    """Keep logging when another Windows process briefly owns the log file."""

    def doRollover(self) -> None:
        try:
            super().doRollover()
        except PermissionError:
            if self.stream:
                self.stream.close()
            self.stream = self._open()


def configure_logging(debug: bool = False, log_path: Path = LOG_PATH) -> logging.Logger:
    """Configure the game logger once and fall back to stderr if files are unavailable."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.propagate = False
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handler: logging.Handler = WindowsSafeRotatingFileHandler(
            log_path,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
    except OSError:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_logger() -> logging.Logger:
    return configure_logging()


def log_runtime_info(
    resolution: tuple[int, int] | None = None,
    state: str | None = None,
) -> None:
    get_logger().info(
        "startup game_version=%s python=%s pygame=%s os=%s resolution=%s state=%s",
        GAME_VERSION,
        platform.python_version(),
        pygame.version.ver,
        f"{platform.system()} {platform.release()}",
        resolution,
        state,
    )


def log_debug(message: str, *args: object) -> None:
    get_logger().debug(message, *args)


def log_event(message: str, *args: object) -> None:
    get_logger().info(message, *args)


def log_warning(message: str, *args: object) -> None:
    get_logger().warning(message, *args)


def log_error(message: str, exc: BaseException | None = None) -> None:
    logger = get_logger()
    if exc is None:
        logger.error(message)
    else:
        logger.error(message, exc_info=(type(exc), exc, exc.__traceback__))


def log_critical(message: str, exc: BaseException) -> None:
    get_logger().critical(
        message,
        exc_info=(type(exc), exc, exc.__traceback__),
    )


def shutdown_logging() -> None:
    """Flush log handlers without globally shutting down unrelated logging users."""
    logger = logging.getLogger(LOGGER_NAME)
    for handler in logger.handlers:
        handler.flush()
