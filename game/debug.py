from __future__ import annotations

import logging
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = ROOT_DIR / "saves" / "errors.log"

logger = logging.getLogger("mortal_end")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False


def log_error(message: str, exc: Exception | None = None) -> None:
    if exc is None:
        logger.error(message)
    else:
        logger.exception("%s: %s", message, exc)


def log_event(message: str) -> None:
    logger.info(message)
