from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .debug import log_error, log_warning


def read_json_object(path: Path, label: str) -> dict[str, Any] | None:
    """Read a JSON object; malformed, missing, or non-object data returns None."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        log_error(f"Failed to read {label} JSON from {path}", exc)
        return None
    if not isinstance(data, dict):
        log_warning("Ignoring %s JSON because its root is not an object: %s", label, path)
        return None
    return data


def write_json_atomic(path: Path, data: dict[str, Any], label: str) -> bool:
    """Atomically replace a JSON file so interrupted writes do not corrupt it."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        os.replace(temporary, path)
    except OSError as exc:
        log_error(f"Failed to write {label} JSON to {path}", exc)
        try:
            temporary.unlink(missing_ok=True)
        except OSError as cleanup_exc:
            log_warning("Unable to remove temporary JSON file %s: %s", temporary, cleanup_exc)
        return False
    return True
