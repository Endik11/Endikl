from __future__ import annotations

import json
from pathlib import Path

from .content_errors import ContentValidationError, DuplicateContentIdError


class DataLoader:
    """UTF-8 JSON reader with structural and duplicate-id checks."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)

    def load_records(self, filename: str, root_key: str) -> list[dict[str, object]]:
        path = self.data_dir / filename
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise ContentValidationError(f"Cannot read {path}: {exc}") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get(root_key), list):
            raise ContentValidationError(f"{path}: expected object with list '{root_key}'")
        records = payload[root_key]
        seen: set[str] = set()
        result: list[dict[str, object]] = []
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                raise ContentValidationError(f"{path}:{root_key}[{index}] must be an object")
            content_id = record.get("id")
            if isinstance(content_id, str) and content_id in seen:
                raise DuplicateContentIdError(f"Duplicate {root_key} id '{content_id}' in {path}")
            if isinstance(content_id, str):
                seen.add(content_id)
            result.append(record)
        return result

    def load_mapping(self, filename: str, root_key: str) -> dict[str, str]:
        path = self.data_dir / filename
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise ContentValidationError(f"Cannot read {path}: {exc}") from exc
        mapping = payload.get(root_key) if isinstance(payload, dict) else None
        if not isinstance(mapping, dict) or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in mapping.items()
        ):
            raise ContentValidationError(f"{path}: '{root_key}' must map strings to strings")
        return dict(mapping)
