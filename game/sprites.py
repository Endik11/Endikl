from __future__ import annotations

import math
from functools import lru_cache

import pygame

from .settings import COLORS, MAX_ENERGY


SPRITE_WIDTH = 260
SPRITE_HEIGHT = 282
SPRITE_ANCHOR = pygame.Vector2(SPRITE_WIDTH // 2, 250)


def _mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def _dark(color: tuple[int, int, int], amount: float = 0.35) -> tuple[int, int, int]:
    return _mix(color, (0, 0, 0), amount)


def _light(color: tuple[int, int, int], amount: float = 0.35) -> tuple[int, int, int]:
    return _mix(color, (255, 255, 255), amount)


def _line(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    start: tuple[float, float],
    end: tuple[float, float],
    width: int,
) -> None:
    pygame.draw.line(surface, color, (int(start[0]), int(start[1])), (int(end[0]), int(end[1])), width)


def _circle(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    center: tuple[float, float],
    radius: int,
    width: int = 0,
) -> None:
    pygame.draw.circle(surface, color, (int(center[0]), int(center[1])), radius, width)


def _ellipse(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    rect: tuple[float, float, float, float],
    width: int = 0,
) -> None:
    pygame.draw.ellipse(surface, color, pygame.Rect(*(int(v) for v in rect)), width)


def _poly(surface: pygame.Surface, color: tuple[int, int, int], points: list[tuple[float, float]]) -> None:
    pygame.draw.polygon(surface, color, [(int(x), int(y)) for x, y in points])


def _rect(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    rect: tuple[float, float, float, float],
    radius: int = 0,
    width: int = 0,
) -> None:
    pygame.draw.rect(surface, color, pygame.Rect(*(int(v) for v in rect)), width, border_radius=radius)


class FighterSpriteFactory:
    def get(
        self,
        definition,
        state: str,
        frame: int,
        facing: int,
        energy: int,
        flash: bool = False,
    ) -> pygame.Surface:
        energy_full = energy >= MAX_ENERGY
        key = (definition.key, state, frame, 1 if facing >= 0 else -1, energy_full, flash)
        return self._render_cached(key, definition)

    @lru_cache(maxsize=512)
    def _render_cached(self, key: tuple, definition) -> pygame.Surface:
        fighter_key, state, frame, facing, energy_full, flash = key
        surface = pygame.Surface((SPRITE_WIDTH, SPRITE_HEIGHT), pygame.SRCALPHA)
        self._draw_energy_aura(surface, definition, state, frame, energy_full)
        self._draw_fighter(surface, definition, state, frame, flash)
        if facing < 0:
            surface = pygame.transform.flip(surface, True, False)
        return surface

    def _draw_energy_aura(self, surface, definition, state: str, frame: int, energy_full: bool) -> None:
        if not energy_full:
            return
        _, accent, _ = definition.palette
        pulse = int(32 + math.sin(frame * 0.8) * 10)
        aura = pygame.Surface((SPRITE_WIDTH, SPRITE_HEIGHT), pygame.SRCALPHA)
        _ellipse(aura, (*accent, pulse), (54, 48, 154, 202), 4)
        _ellipse(aura, (*_light(accent, 0.2), pulse // 2), (38, 32, 186, 232), 2)
        surface.blit(aura, (0, 0))

    def _draw_fighter(self, surface, definition, state: str, frame: int, flash: bool) -> None:
        primary, accent, dark = definition.palette
        if flash:
            primary = COLORS["white"]
            accent = COLORS["gold"]
            dark = (58, 62, 70)

        pose = self._pose(state, frame)
        skin = self._skin(definition.key)
        hair = self._hair(definition.key)

        cx = SPRITE_ANCHOR.x
        ground = SPRITE_ANCHOR.y
        hip = pygame.Vector2(cx + pose["lean"] * 0.35, ground - pose["hip_y"])
        chest = pygame.Vector2(cx + pose["lean"], ground - pose["chest_y"])
        neck = pygame.Vector2(cx + pose["lean"] * 1.15, ground - pose["neck_y"])

        self._draw_back_cloth(surface, definition, primary, accent, dark, hip, chest, pose, state, frame)
        self._draw_legs(surface, definition, primary, accent, dark, hip, ground, pose)
        self._draw_torso(surface, definition, primary, accent, dark, chest, hip, pose)
        self._draw_head(surface, definition, skin, hair, accent, dark, neck, pose, state)
        self._draw_arms(surface, definition, primary, accent, dark, skin, chest, pose, state)
        self._draw_front_details(surface, definition, primary, accent, dark, chest, hip, pose, state, frame)

    def _pose(self, state: str, frame: int) -> dict[str, object]:
        phase = frame / 7.0
        wave = math.sin(phase * math.tau)
        pose = {
            "lean": 0.0,
            "hip_y": 78.0,
            "chest_y": 158.0,
            "neck_y": 204.0,
            "crouch": 0.0,
            "arm_front": [pygame.Vector2(34, -18), pygame.Vector2(60, 22)],
            "arm_back": [pygame.Vector2(-33, -11), pygame.Vector2(-54, 34)],
            "leg_front": [pygame.Vector2(24, 28), pygame.Vector2(34, 78)],
            "leg_back": [pygame.Vector2(-22, 28), pygame.Vector2(-32, 78)],
            "head_angle": 0.0,
        }

        if state == "idle":
            pose["lean"] = wave * 2.5
            pose["chest_y"] = 160.0 + wave * 2.0
            pose["arm_front"] = [pygame.Vector2(32, -18 + wave * 2), pygame.Vector2(54, 20 + wave * 2)]
            pose["arm_back"] = [pygame.Vector2(-32, -11 - wave), pygame.Vector2(-50, 34 - wave)]
        elif state == "walk":
            swing = math.sin(phase * math.tau)
            pose["lean"] = 5.0
            pose["arm_front"] = [pygame.Vector2(28, -18), pygame.Vector2(45 - swing * 20, 20)]
            pose["arm_back"] = [pygame.Vector2(-30, -10), pygame.Vector2(-48 + swing * 18, 35)]
            pose["leg_front"] = [pygame.Vector2(22 + swing * 13, 28), pygame.Vector2(34 + swing * 28, 78)]
            pose["leg_back"] = [pygame.Vector2(-22 - swing * 13, 28), pygame.Vector2(-34 - swing * 26, 78)]
        elif state == "jump":
            pose["lean"] = 8.0
            pose["hip_y"] = 82.0
            pose["arm_front"] = [pygame.Vector2(30, -25), pygame.Vector2(46, -60)]
            pose["arm_back"] = [pygame.Vector2(-34, -18), pygame.Vector2(-58, -45)]
            pose["leg_front"] = [pygame.Vector2(22, 22), pygame.Vector2(52, 56)]
            pose["leg_back"] = [pygame.Vector2(-20, 25), pygame.Vector2(-38, 58)]
        elif state == "crouch":
            pose["lean"] = 6.0
            pose["hip_y"] = 52.0
            pose["chest_y"] = 124.0
            pose["neck_y"] = 166.0
            pose["crouch"] = 1.0
            pose["arm_front"] = [pygame.Vector2(30, -14), pygame.Vector2(62, 16)]
            pose["arm_back"] = [pygame.Vector2(-26, -8), pygame.Vector2(-44, 22)]
            pose["leg_front"] = [pygame.Vector2(28, 12), pygame.Vector2(70, 52)]
            pose["leg_back"] = [pygame.Vector2(-24, 12), pygame.Vector2(-64, 52)]
        elif state == "block":
            pose["lean"] = -5.0
            pose["arm_front"] = [pygame.Vector2(22, -28), pygame.Vector2(45, -58)]
            pose["arm_back"] = [pygame.Vector2(-12, -30), pygame.Vector2(33, -42)]
            pose["leg_front"] = [pygame.Vector2(26, 25), pygame.Vector2(48, 78)]
            pose["leg_back"] = [pygame.Vector2(-26, 26), pygame.Vector2(-38, 78)]
        elif state == "attack":
            strike = math.sin(min(1.0, phase * 1.35) * math.pi)
            pose["lean"] = 13.0 * strike
            pose["arm_front"] = [pygame.Vector2(38, -23), pygame.Vector2(95 + strike * 22, -34 + strike * 14)]
            pose["arm_back"] = [pygame.Vector2(-30, -13), pygame.Vector2(-53, 40)]
            pose["leg_front"] = [pygame.Vector2(28, 25), pygame.Vector2(55, 78)]
            pose["leg_back"] = [pygame.Vector2(-24, 28), pygame.Vector2(-48, 78)]
        elif state == "hit":
            pose["lean"] = -15.0
            pose["head_angle"] = -8.0
            pose["arm_front"] = [pygame.Vector2(18, -12), pygame.Vector2(38, 28)]
            pose["arm_back"] = [pygame.Vector2(-36, -5), pygame.Vector2(-80, -15)]
        elif state == "victory":
            pose["lean"] = 2.0 + wave * 2.0
            pose["arm_front"] = [pygame.Vector2(28, -30), pygame.Vector2(48, -92)]
            pose["arm_back"] = [pygame.Vector2(-36, -10), pygame.Vector2(-62, 32)]
        elif state == "down":
            pose["lean"] = 0.0
            pose["hip_y"] = 24.0
            pose["chest_y"] = 36.0
            pose["neck_y"] = 50.0
            pose["arm_front"] = [pygame.Vector2(46, 0), pygame.Vector2(88, 8)]
            pose["arm_back"] = [pygame.Vector2(-38, 0), pygame.Vector2(-86, 12)]
            pose["leg_front"] = [pygame.Vector2(46, 0), pygame.Vector2(90, 10)]
            pose["leg_back"] = [pygame.Vector2(-44, 0), pygame.Vector2(-92, 8)]
        return pose

    def _draw_back_cloth(self, surface, definition, primary, accent, dark, hip, chest, pose, state, frame) -> None:
        if state == "down":
            _ellipse(surface, (*_dark(dark, 0.1), 230), (52, 210, 150, 30))
            return
        sway = math.sin(frame * 0.55) * 7
        if definition.key == "sable":
            _poly(
                surface,
                (*_dark(accent, 0.15), 190),
                [
                    (chest.x - 24, chest.y - 16),
                    (chest.x - 70 + sway, chest.y + 44),
                    (hip.x - 50 + sway * 1.4, hip.y + 62),
                    (hip.x - 8, hip.y + 24),
                ],
            )
            _poly(
                surface,
                (*accent, 165),
                [
                    (chest.x + 8, chest.y - 16),
                    (chest.x + 76 + sway, chest.y + 30),
                    (hip.x + 56 + sway, hip.y + 66),
                    (hip.x + 10, hip.y + 24),
                ],
            )
        elif definition.key == "mira":
            _poly(
                surface,
                (*_dark(primary, 0.1), 210),
                [
                    (chest.x - 30, chest.y - 20),
                    (chest.x - 52 + sway, hip.y + 78),
                    (hip.x + 8, hip.y + 72),
                    (chest.x + 34, chest.y - 12),
                ],
            )
        else:
            _poly(
                surface,
                (*_dark(dark, 0.05), 220),
                [
                    (chest.x - 38, chest.y - 18),
                    (chest.x - 58 + sway, hip.y + 78),
                    (hip.x + 42 + sway, hip.y + 70),
                    (chest.x + 36, chest.y - 14),
                ],
            )

    def _draw_legs(self, surface, definition, primary, accent, dark, hip, ground, pose) -> None:
        for index, key in enumerate(("leg_back", "leg_front")):
            knee = hip + pose[key][0]
            foot = hip + pose[key][1]
            leg_color = _dark(primary, 0.18) if index == 0 else primary
            _line(surface, _dark(dark, 0.05), hip + pygame.Vector2(-4 + index * 8, -1), knee, 24)
            _line(surface, leg_color, hip + pygame.Vector2(-4 + index * 8, -1), knee, 16)
            _line(surface, _dark(dark, 0.05), knee, foot, 24)
            _line(surface, _mix(leg_color, accent, 0.18), knee, foot, 15)
            boot = pygame.Rect(0, 0, 48, 18)
            boot.center = (int(foot.x + 12), int(min(ground, foot.y + 2)))
            _rect(surface, _dark(dark, 0.0), boot, 7)
            _rect(surface, accent, (boot.x + 8, boot.y + 4, 18, 5), 2)
            _circle(surface, _light(accent, 0.15), knee, 8)

    def _draw_torso(self, surface, definition, primary, accent, dark, chest, hip, pose) -> None:
        shoulder_l = pygame.Vector2(chest.x - 38, chest.y - 28)
        shoulder_r = pygame.Vector2(chest.x + 40, chest.y - 23)
        waist_l = pygame.Vector2(hip.x - 30, hip.y - 14)
        waist_r = pygame.Vector2(hip.x + 32, hip.y - 12)
        _poly(surface, _dark(dark, 0.02), [shoulder_l, shoulder_r, waist_r, waist_l])
        _poly(
            surface,
            primary,
            [
                shoulder_l + pygame.Vector2(7, 5),
                shoulder_r + pygame.Vector2(-5, 4),
                waist_r + pygame.Vector2(-5, -3),
                waist_l + pygame.Vector2(5, -4),
            ],
        )

        chest_plate = [
            (chest.x - 23, chest.y - 17),
            (chest.x + 24, chest.y - 15),
            (hip.x + 18, hip.y - 27),
            (hip.x - 18, hip.y - 28),
        ]
        _poly(surface, _light(primary, 0.12), chest_plate)
        _poly(
            surface,
            accent,
            [
                (chest.x - 8, chest.y - 13),
                (chest.x + 12, chest.y - 12),
                (hip.x + 8, hip.y - 36),
                (hip.x - 8, hip.y - 36),
            ],
        )
        _rect(surface, _dark(dark, 0.05), (hip.x - 38, hip.y - 18, 78, 16), 5)
        _rect(surface, accent, (hip.x - 10, hip.y - 18, 20, 16), 4)

        for i in range(4):
            x = chest.x - 28 + i * 18
            _line(surface, _dark(primary, 0.35), (x, chest.y + 2), (x - 5, hip.y - 26), 2)

    def _draw_head(self, surface, definition, skin, hair, accent, dark, neck, pose, state: str) -> None:
        if state == "down":
            head_center = (neck.x + 48, neck.y + 22)
            _ellipse(surface, _dark(dark, 0.1), (head_center[0] - 24, head_center[1] - 15, 52, 34))
            _ellipse(surface, skin, (head_center[0] - 18, head_center[1] - 12, 42, 27))
            return

        _line(surface, _dark(dark, 0.08), (neck.x - 4, neck.y + 10), (neck.x - 2, neck.y + 35), 16)
        head_rect = pygame.Rect(0, 0, 48, 58)
        head_rect.center = (int(neck.x + pose["lean"] * 0.15), int(neck.y - 14))
        _ellipse(surface, _dark(dark, 0.0), head_rect.inflate(10, 10))
        _ellipse(surface, skin, head_rect)

        if definition.key == "kael":
            _poly(surface, hair, [(head_rect.left + 4, head_rect.top + 10), (head_rect.centerx, head_rect.top - 10), (head_rect.right - 4, head_rect.top + 13)])
            _rect(surface, accent, (head_rect.left + 8, head_rect.top + 24, 34, 10), 4)
        elif definition.key == "sable":
            _rect(surface, _dark(accent, 0.22), (head_rect.left + 4, head_rect.top + 25, 42, 18), 7)
            _poly(surface, hair, [(head_rect.left + 2, head_rect.top + 5), (head_rect.right + 16, head_rect.top + 22), (head_rect.right - 5, head_rect.bottom + 10)])
        elif definition.key == "orrin":
            _circle(surface, _dark(hair, 0.2), (head_rect.centerx, head_rect.top + 8), 22, 6)
            _rect(surface, accent, (head_rect.left + 7, head_rect.top + 20, 36, 9), 4)
        else:
            _poly(surface, hair, [(head_rect.left, head_rect.top + 7), (head_rect.centerx - 4, head_rect.top - 16), (head_rect.right + 16, head_rect.top + 22), (head_rect.right - 3, head_rect.bottom + 20)])
            _line(surface, accent, (head_rect.left + 8, head_rect.top + 22), (head_rect.right - 8, head_rect.top + 19), 3)

        eye_y = head_rect.top + 30
        _circle(surface, (20, 24, 28), (head_rect.centerx + 8, eye_y), 3)
        _circle(surface, _light(accent, 0.35), (head_rect.centerx + 9, eye_y - 1), 1)
        _line(surface, _dark(skin, 0.38), (head_rect.centerx + 3, eye_y + 12), (head_rect.centerx + 14, eye_y + 11), 2)

    def _draw_arms(self, surface, definition, primary, accent, dark, skin, chest, pose, state: str) -> None:
        for index, key in enumerate(("arm_back", "arm_front")):
            elbow = chest + pose[key][0]
            hand = chest + pose[key][1]
            shoulder = chest + pygame.Vector2(-29 if index == 0 else 31, -20 if index == 0 else -26)
            arm_color = _dark(primary, 0.15) if index == 0 else _light(primary, 0.08)
            gauntlet = accent if definition.key in ("kael", "orrin") else _mix(accent, COLORS["white"], 0.18)
            _circle(surface, _dark(dark, 0.0), shoulder, 16)
            _line(surface, _dark(dark, 0.02), shoulder, elbow, 22)
            _line(surface, arm_color, shoulder, elbow, 14)
            _line(surface, _dark(dark, 0.0), elbow, hand, 23)
            _line(surface, gauntlet, elbow, hand, 15)
            _circle(surface, _dark(dark, 0.02), hand, 16)
            _circle(surface, gauntlet, hand, 12)

            if definition.key == "orrin":
                _circle(surface, _light(gauntlet, 0.2), hand, 18, 4)
                _line(surface, _dark(dark, 0.1), (hand.x - 12, hand.y), (hand.x + 14, hand.y), 3)
            elif definition.key == "sable" and index == 1:
                blade_tip = hand + pygame.Vector2(28, -4 if state == "attack" else 12)
                _line(surface, COLORS["white"], hand, blade_tip, 4)
                _line(surface, accent, hand + pygame.Vector2(4, 3), blade_tip, 2)
            elif definition.key == "kael" and state == "attack" and index == 1:
                for i in range(3):
                    _line(
                        surface,
                        (*_light(accent, 0.2),),
                        (hand.x + i * 8, hand.y - 14 - i * 2),
                        (hand.x + 40 + i * 10, hand.y - 26 + i * 5),
                        3,
                    )

    def _draw_front_details(self, surface, definition, primary, accent, dark, chest, hip, pose, state: str, frame: int) -> None:
        if state == "down":
            return
        if definition.key == "kael":
            for i in range(3):
                start = (chest.x - 19 + i * 17, chest.y - 2)
                end = (chest.x - 10 + i * 13, hip.y - 36)
                _line(surface, _light(accent, 0.18), start, end, 2)
            _circle(surface, COLORS["red"], (chest.x + 7, chest.y + 12), 5)
        elif definition.key == "sable":
            _line(surface, _light(accent, 0.35), (chest.x - 34, chest.y - 4), (hip.x + 33, hip.y - 22), 5)
            _line(surface, primary, (chest.x - 28, chest.y + 6), (hip.x + 27, hip.y - 14), 3)
        elif definition.key == "orrin":
            for i in range(5):
                _circle(surface, accent, (chest.x - 28 + i * 14, chest.y + 20 + math.sin(frame + i) * 2), 4)
            _rect(surface, _light(primary, 0.1), (chest.x - 31, chest.y - 20, 22, 44), 4, 2)
            _rect(surface, _light(primary, 0.1), (chest.x + 9, chest.y - 20, 22, 44), 4, 2)
        else:
            for i in range(3):
                y = chest.y + i * 18
                _line(surface, COLORS["white"], (chest.x - 28, y), (chest.x + 28, y - 6), 2)
                _circle(surface, accent, (chest.x + 31, y - 7), 3)

    def _skin(self, key: str) -> tuple[int, int, int]:
        return {
            "kael": (191, 136, 105),
            "sable": (170, 124, 116),
            "orrin": (151, 109, 83),
            "mira": (206, 159, 132),
        }.get(key, (190, 145, 118))

    def _hair(self, key: str) -> tuple[int, int, int]:
        return {
            "kael": (42, 30, 26),
            "sable": (31, 25, 44),
            "orrin": (38, 42, 38),
            "mira": (218, 224, 230),
        }.get(key, (38, 34, 32))


SPRITE_FACTORY = FighterSpriteFactory()

