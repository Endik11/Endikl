from __future__ import annotations

import pygame


class RoundAnnouncer:
    FALLBACK = {
        "round": "ROUND",
        "ready": "READY",
        "fight": "FIGHT",
        "ko": "KNOCKOUT",
        "draw": "DRAW",
        "double_ko": "DOUBLE KNOCKOUT",
        "sudden_death": "SUDDEN DEATH",
        "victory": "VICTORY",
        "shadow_finish": "SHADOW FINISH",
    }

    def __init__(self, registry) -> None:
        self.registry = registry
        self._font: pygame.font.Font | None = None

    def message(self, snapshot) -> str:
        result = str(snapshot.round_result or "")
        if result == "DRAW":
            return self._text("draw")
        if result == "DOUBLE_KO":
            return self._text("double_ko")
        if result:
            return self._text("victory")
        if snapshot.frame_number < 80:
            return f"{self._text('round')} 1"
        if 80 <= snapshot.frame_number < 130:
            return self._text("ready")
        if 130 <= snapshot.frame_number < 180:
            return self._text("fight")
        return ""

    def draw(self, surface: pygame.Surface, snapshot) -> None:
        message = self.message(snapshot)
        if not message:
            return
        if self._font is None:
            self._font = pygame.font.SysFont("Segoe UI", 58, bold=True)
        text = self._font.render(message, True, (238, 241, 244))
        surface.blit(text, text.get_rect(center=(640, 154)))

    def _text(self, key: str) -> str:
        hud = self.registry.hud
        localization_key = hud.announcer_keys.get(key, "") if hud else ""
        localized = self.registry.localization.get(localization_key) if localization_key else ""
        if localized and not localized.startswith("["):
            return localized
        return self.FALLBACK.get(key, key.upper())
