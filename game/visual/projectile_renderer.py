from __future__ import annotations

import pygame


class ProjectileRenderer:
    def draw(self, surface: pygame.Surface, snapshot, camera) -> None:
        for projectile in snapshot.projectiles:
            projectile_id, owner_id, x, y, lifetime, durability = projectile
            screen = camera.world_to_screen(float(x), float(y))
            color = (87, 202, 236) if owner_id == "p1" else (232, 181, 82)
            pygame.draw.circle(surface, color, screen, 13)
            pygame.draw.circle(surface, (*color, 120), screen, 24, 2)
            pygame.draw.line(surface, color, (screen[0] - 32, screen[1]), (screen[0] - 8, screen[1]), 3)
