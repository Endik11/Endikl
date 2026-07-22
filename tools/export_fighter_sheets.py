from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pygame

from game.fighter import FIGHTER_DEFINITIONS
from game.sprites import SPRITE_FACTORY, SPRITE_HEIGHT, SPRITE_WIDTH
from game.settings import ROOT_DIR


STATES = ("idle", "walk", "jump", "crouch", "block", "attack", "hit", "down", "victory")
FRAMES_PER_STATE = 8


def main() -> None:
    pygame.init()
    target_dir = ROOT_DIR / "assets" / "fighters"
    target_dir.mkdir(parents=True, exist_ok=True)

    for definition in FIGHTER_DEFINITIONS.values():
        sheet = pygame.Surface(
            (SPRITE_WIDTH * FRAMES_PER_STATE, SPRITE_HEIGHT * len(STATES)),
            pygame.SRCALPHA,
        )
        for row, state in enumerate(STATES):
            for frame in range(FRAMES_PER_STATE):
                sprite = SPRITE_FACTORY.get(definition, state, frame, 1, 1000)
                sheet.blit(sprite, (frame * SPRITE_WIDTH, row * SPRITE_HEIGHT))
        pygame.image.save(sheet, target_dir / f"{definition.key}_sheet.png")

    pygame.quit()


if __name__ == "__main__":
    main()
