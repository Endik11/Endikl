from __future__ import annotations

import os
import sys
import time
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.combat.combat_event import CombatEvent
from game.combat.combat_world import CombatWorld
from game.combat.enums import CombatEventType
from game.combat_renderer import CombatRenderer
from game.content_registry import get_default_registry
from game.settings import GameSettings


def main() -> None:
    pygame.init()
    registry = get_default_registry()
    settings = GameSettings()
    world = CombatWorld(registry, "kael", "sable", "neon_foundry")
    renderer = CombatRenderer(registry, settings)
    renderer.set_arena("neon_foundry")
    surface = pygame.Surface((1280, 720))
    before = world.snapshot().digest()
    event = CombatEvent(0, CombatEventType.ATTACK_HIT, position=(640, 430))
    renderer.handle_combat_events([event])
    frames = 1000
    started = time.perf_counter()
    for _ in range(frames):
        renderer.draw(surface, world.snapshot(), 1.0, world)
    elapsed = time.perf_counter() - started
    after = world.snapshot().digest()
    if before != after:
        raise RuntimeError("renderer mutated CombatWorld")
    avg_ms = elapsed * 1000 / frames
    fps = frames / elapsed if elapsed > 0 else 0.0
    print(f"frames={frames} elapsed={elapsed:.4f}s fps={fps:.0f} avg_ms={avg_ms:.4f}")
    pygame.quit()


if __name__ == "__main__":
    main()
