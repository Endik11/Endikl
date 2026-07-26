from __future__ import annotations

from .debug import log_warning


class LocalizationManager:
    def __init__(self, strings: dict[str, str] | None = None) -> None:
        self._strings = dict(strings or {})
        self._warned: set[str] = set()

    def replace(self, strings: dict[str, str]) -> None:
        self._strings = dict(strings)

    def has(self, key: str) -> bool:
        return key in self._strings

    def get(self, key: str, **values: object) -> str:
        text = self._strings.get(key)
        if text is None:
            if key not in self._warned:
                self._warned.add(key)
                log_warning("Unknown localization key: %s", key)
            return f"[{key}]"
        try:
            return text.format(**values)
        except (KeyError, ValueError) as exc:
            if key not in self._warned:
                self._warned.add(key)
                log_warning("Localization formatting failed for %s: %s", key, exc)
            return text
