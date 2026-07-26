from __future__ import annotations

from .debug import log_warning


class LocalizationManager:
    def __init__(self, strings: dict[str, str] | None = None, *, languages: dict[str, dict[str,str]] | None = None, language: str = "ru", fallback: str = "ru") -> None:
        self._languages = {key:dict(value) for key,value in (languages or {language:strings or {}}).items()}
        self.language = language if language in self._languages else fallback
        self.fallback = fallback if fallback in self._languages else self.language
        self._strings = self._languages.get(self.language,{})
        self._warned: set[str] = set()

    def replace(self, strings: dict[str, str]) -> None:
        self._strings = dict(strings)
        self._languages[self.language]=self._strings

    def switch(self, language: str) -> bool:
        if language not in self._languages:return False
        self.language=language;self._strings=self._languages[language];return True

    def has(self, key: str) -> bool:
        return key in self._strings

    def get(self, key: str, **values: object) -> str:
        text = self._strings.get(key) or self._languages.get(self.fallback,{}).get(key)
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
