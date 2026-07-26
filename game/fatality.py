from __future__ import annotations

# Compatibility module name retained for Stage 3; a later stage may rename the
# internal module after downstream imports and persisted counters are migrated.

from dataclasses import dataclass

import pygame


@dataclass
class FinisherState:
    active: bool = False
    winner_index: int = 0
    loser_index: int = 1
    timer: float = 0.0
    chosen: str | None = None
    banner_timer: float = 0.0

    def start(self, winner_index: int, loser_index: int) -> None:
        self.active = True
        self.winner_index = winner_index
        self.loser_index = loser_index
        self.timer = 4.0
        self.chosen = None
        self.banner_timer = 0.0

    def update(self, dt: float) -> bool:
        if not self.active:
            return False
        self.timer -= dt
        self.banner_timer = max(0.0, self.banner_timer - dt)
        if self.timer <= 0 and self.chosen is None:
            self.chosen = "victory"
        return self.chosen is not None

    def select(self, kind: str) -> None:
        if self.active and self.chosen is None:
            self.chosen = kind
            self.banner_timer = 1.6

    def reset(self) -> None:
        self.active = False
        self.timer = 0.0
        self.chosen = None
        self.banner_timer = 0.0


def detect_finisher(
    winner,
    loser,
    pressed: dict[str, bool],
    stage_left: int,
    stage_right: int,
) -> str | None:
    """Small original finisher rules for the prototype."""
    near_edge = loser.pos.x < stage_left + 95 or loser.pos.x > stage_right - 95
    if near_edge and pressed.get("heavy_kick") and pressed.get("energy"):
        return "stage_finish"
    if pressed.get("down") and pressed.get("heavy_punch") and winner.energy >= 300:
        winner.energy -= 300
        return "shadow_finish"
    if pressed.get("heavy_punch") and pressed.get("heavy_kick") and winner.energy >= 500:
        winner.energy -= 500
        return "final_strike"
    return None


def draw_finisher_overlay(
    surface: pygame.Surface,
    font_big: pygame.font.Font,
    font_small: pygame.font.Font,
    state: FinisherState,
) -> None:
    if not state.active:
        return

    if state.chosen is None:
        text = "ЗАВЕРШИ ИХ"
        sub = "Вниз + сильный удар: Теневой финал   Энергия + сильный удар у края: Финал арены"
    elif state.chosen == "shadow_finish":
        text = "ТЕНЕВОЙ ФИНАЛ"
        sub = "Поединок завершается кинематографическим всплеском тени."
    elif state.chosen == "final_strike":
        text = "ПОСЛЕДНИЙ УДАР"
        sub = "Последний сверхудар разносит раунд в щепки."
    elif state.chosen == "stage_finish":
        text = "ФИНАЛ АРЕНЫ"
        sub = "Сама арена забирает поверженного бойца."
    else:
        text = "ПОБЕДА"
        sub = "Честь зафиксирована в архиве."

    label = font_big.render(text, True, (232, 181, 82))
    surface.blit(label, label.get_rect(center=(surface.get_width() // 2, 165)))
    hint = font_small.render(sub, True, (238, 241, 244))
    surface.blit(hint, hint.get_rect(center=(surface.get_width() // 2, 215)))
