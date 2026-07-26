from __future__ import annotations

import math
from dataclasses import dataclass

import pygame


Color = tuple[int, int, int]
Point = tuple[float, float]


def _clamp(value: float) -> int:
    return max(0, min(255, int(round(value))))


def _mix(first: Color, second: Color, amount: float) -> Color:
    t = max(0.0, min(1.0, amount))
    return tuple(_clamp(a + (b - a) * t) for a, b in zip(first, second))


def _shade(color: Color, amount: float) -> Color:
    return _mix(color, (255, 255, 255) if amount >= 0 else (0, 0, 0), abs(amount))


def _point(transform, floor_y: int | None = None) -> Point:
    y = transform.y
    if floor_y is not None:
        y = min(y, floor_y)
    return transform.x, y


def _end(transform, floor_y: int | None = None) -> Point:
    radians = math.radians(transform.rotation - 90.0)
    point = (transform.x + math.cos(radians) * transform.length, transform.y + math.sin(radians) * transform.length)
    if floor_y is not None:
        return point[0], min(point[1], floor_y)
    return point


def _px(point: Point) -> tuple[int, int]:
    return int(round(point[0])), int(round(point[1]))


def _offset(point: Point, normal: Point, amount: float) -> Point:
    return point[0] + normal[0] * amount, point[1] + normal[1] * amount


def _unit(start: Point, end: Point) -> Point:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = max(0.001, math.hypot(dx, dy))
    return dx / length, dy / length


def _normal(start: Point, end: Point) -> Point:
    direction = _unit(start, end)
    return -direction[1], direction[0]


@dataclass(frozen=True, slots=True)
class CharacterStyle:
    hair_shape: str
    torso_shape: str
    guard_shape: str
    scarf: bool
    cape: bool
    mask: bool
    boots: str
    weapon: str
    glow_shape: str


STYLES: dict[str, CharacterStyle] = {
    "ash_guard": CharacterStyle("crest", "plate", "shoulder", False, False, False, "armored", "blade", "core"),
    "veil_runner": CharacterStyle("veil", "wrap", "ribbon", True, True, True, "light", "energy", "diamond"),
    "iron_monk": CharacterStyle("topknot", "wrap", "disc", True, False, False, "heavy", "fist", "none"),
    "storm_dancer": CharacterStyle("wind", "coat", "shoulder", False, True, False, "light", "energy", "ring"),
    "wind_disciple": CharacterStyle("headband", "wrap", "ribbon", True, False, False, "light", "staff", "none"),
    "storm_warden": CharacterStyle("horns", "plate", "shoulder", False, True, True, "armored", "blade", "rune"),
}


class CharacterArtRenderer:
    """Paints readable combat silhouettes over the simulation-owned skeleton.

    The rig supplies positions and animation timing. This layer owns only the
    art treatment, so changing a glove or shoulder plate cannot change a hitbox.
    """

    OUTLINE: Color = (6, 9, 15)
    INK: Color = (18, 22, 31)

    def draw(self, surface: pygame.Surface, transforms, visual, snapshot, floor_y: int) -> None:
        bones = {transform.id: transform for transform in transforms}
        style = STYLES.get(visual.silhouette, STYLES["ash_guard"])
        roles = visual.palette_roles
        colors = self._colors(roles)
        hit = snapshot.state in {"HIT_STUN", "BLOCK_STUN", "THROWN", "LAUNCHED", "KNOCKDOWN"}
        attacking = bool(getattr(snapshot, "attack_id", ""))

        self._draw_back_cloth(surface, bones, visual, style, colors, floor_y)
        self._draw_leg(surface, bones, "left", colors, floor_y, style, hit, back=True)
        self._draw_torso(surface, bones, visual, style, colors, floor_y, hit)
        self._draw_leg(surface, bones, "right", colors, floor_y, style, hit)
        self._draw_arm(surface, bones, "left", colors, floor_y, style, hit)
        self._draw_arm(surface, bones, "right", colors, floor_y, style, hit)
        self._draw_weapon(surface, bones, visual, style, colors, floor_y, attacking)
        self._draw_head(surface, bones, visual, style, colors, snapshot, floor_y, hit)
        self._draw_action_rim(surface, bones, visual, style, colors, snapshot, floor_y)

    @staticmethod
    def _colors(roles: dict[str, Color]) -> dict[str, Color]:
        primary = roles.get("primary", (220, 220, 220))
        secondary = roles.get("secondary", primary)
        accent = roles.get("accent", (240, 240, 240))
        cloth = roles.get("cloth", _shade(primary, -0.65))
        skin = roles.get("skin", (190, 145, 115))
        return {
            "primary": primary,
            "primary_light": _shade(primary, 0.24),
            "primary_dark": _shade(primary, -0.42),
            "secondary": secondary,
            "secondary_light": _shade(secondary, 0.24),
            "secondary_dark": _shade(secondary, -0.42),
            "accent": accent,
            "accent_light": _shade(accent, 0.2),
            "cloth": cloth,
            "cloth_light": _shade(cloth, 0.24),
            "skin": skin,
            "skin_light": _shade(skin, 0.18),
            "skin_shadow": _shade(skin, -0.3),
            "outline": CharacterArtRenderer.OUTLINE,
            "ink": CharacterArtRenderer.INK,
            "hit": (255, 108, 86),
            "white": (246, 248, 255),
        }

    @staticmethod
    def _poly(surface: pygame.Surface, points: list[Point], fill: Color, colors: dict[str, Color], inset: float = 0.88) -> None:
        if len(points) < 3:
            return
        pygame.draw.polygon(surface, colors["outline"], [_px(point) for point in points])
        center = (sum(point[0] for point in points) / len(points), sum(point[1] for point in points) / len(points))
        inner = [(center[0] + (point[0] - center[0]) * inset, center[1] + (point[1] - center[1]) * inset) for point in points]
        pygame.draw.polygon(surface, fill, [_px(point) for point in inner])

    @staticmethod
    def _line(surface: pygame.Surface, start: Point, end: Point, width: float, color: Color, outline: Color, *, caps: bool = True) -> None:
        a, b = _px(start), _px(end)
        outer = max(2, int(round(width + 6)))
        inner = max(1, int(round(width)))
        pygame.draw.line(surface, outline, a, b, outer)
        pygame.draw.line(surface, color, a, b, inner)
        if caps:
            pygame.draw.circle(surface, outline, a, max(2, outer // 2))
            pygame.draw.circle(surface, outline, b, max(2, outer // 2))
            pygame.draw.circle(surface, color, a, max(1, inner // 2))
            pygame.draw.circle(surface, color, b, max(1, inner // 2))

    @staticmethod
    def _joint(surface: pygame.Surface, center: Point, radius: float, fill: Color, colors: dict[str, Color], *, ring: Color | None = None) -> None:
        c = _px(center)
        outer = max(3, int(radius + 4))
        pygame.draw.circle(surface, colors["outline"], c, outer)
        pygame.draw.circle(surface, ring or fill, c, max(2, int(radius + 1)))
        pygame.draw.circle(surface, fill, c, max(2, int(radius - 2)))

    def _draw_back_cloth(self, surface, bones, visual, style, colors, floor_y) -> None:
        if not style.cape and not any(name in visual.attachments for name in ("cloth_left", "cloth_right")):
            return
        for side in ("left", "right"):
            bone = bones.get(f"cloth_{side}")
            if bone is None or f"cloth_{side}" not in visual.attachments:
                continue
            start = _point(bone)
            end = _end(bone, floor_y)
            direction = _unit(start, end)
            normal = (-direction[1], direction[0])
            width = 13 if style.cape else 8
            wave = 8 * (1 if side == "left" else -1)
            points = [
                _offset(start, normal, width),
                _offset(start, normal, -width),
                _offset(_offset(end, normal, -width * 0.35), direction, wave),
                _offset(_offset(end, normal, width * 0.35), direction, wave),
            ]
            self._poly(surface, points, colors["cloth"], colors, 0.91)
            self._line(surface, _offset(start, normal, width * 0.55), _offset(end, normal, width * 0.22), 2, colors["cloth_light"], colors["outline"], caps=False)

    def _draw_leg(self, surface, bones, side, colors, floor_y, style, hit, back=False) -> None:
        thigh = bones.get(f"{side}_thigh")
        shin = bones.get(f"{side}_shin")
        foot = bones.get(f"{side}_foot")
        if not thigh or not shin:
            return
        start, knee = _point(thigh, floor_y), _end(thigh, floor_y)
        knee_center = _point(shin, floor_y)
        ankle = _end(shin, floor_y)
        shade = colors["primary_dark"] if back else colors["primary"]
        lower = colors["secondary_dark"] if back else colors["secondary"]
        if hit:
            shade = _mix(shade, colors["hit"], 0.25)
            lower = _mix(lower, colors["hit"], 0.18)
        self._line(surface, start, knee, 17 if style.boots == "heavy" else 14, shade, colors["outline"])
        self._line(surface, knee_center, ankle, 14 if style.boots == "heavy" else 11, lower, colors["outline"])
        self._joint(surface, knee_center, 9 if style.boots == "heavy" else 7, colors["accent"], colors, ring=colors["secondary_dark"])
        if foot:
            foot_start = _point(foot, floor_y)
            foot_end = _end(foot, floor_y)
            boot = colors["secondary_dark"] if style.boots != "light" else colors["cloth"]
            self._line(surface, foot_start, foot_end, 12 if style.boots == "heavy" else 10, boot, colors["outline"])
            toe = _px((foot_end[0] + (5 if foot_end[0] >= foot_start[0] else -5), min(foot_end[1] + 2, floor_y - 5)))
            pygame.draw.ellipse(surface, colors["outline"], pygame.Rect(toe[0] - 15, toe[1] - 8, 30, 16))
            pygame.draw.ellipse(surface, colors["secondary"], pygame.Rect(toe[0] - 11, toe[1] - 5, 24, 10))
            pygame.draw.line(surface, colors["accent"], (toe[0] - 8, toe[1] + 2), (toe[0] + 9, toe[1] + 2), 2)

    def _draw_torso(self, surface, bones, visual, style, colors, floor_y, hit) -> None:
        pelvis = bones.get("pelvis")
        upper = bones.get("torso_upper")
        left_shoulder = bones.get("left_shoulder")
        right_shoulder = bones.get("right_shoulder")
        if not pelvis or not upper or not left_shoulder or not right_shoulder:
            return
        hip = _point(pelvis, floor_y)
        shoulder_points = sorted([_point(left_shoulder, floor_y), _point(right_shoulder, floor_y)], key=lambda item: item[0])
        left, right = shoulder_points
        hip_left = (hip[0] - 22, hip[1] - 7)
        hip_right = (hip[0] + 22, hip[1] - 7)
        fill = colors["primary"] if style.torso_shape != "wrap" else colors["cloth"]
        if hit:
            fill = _mix(fill, colors["hit"], 0.2)
        self._poly(surface, [left, right, hip_right, hip_left], fill, colors, 0.93)
        chest = _point(upper, floor_y)
        normal = _normal(left, right)
        self._line(surface, _offset(left, normal, -4), _offset(right, normal, -4), 4, colors["primary_light"], colors["outline"], caps=False)
        self._line(surface, (hip_left[0] + 3, hip_left[1] - 2), (hip_right[0] - 3, hip_right[1] - 2), 8, colors["secondary_dark"], colors["outline"], caps=False)
        self._line(surface, (hip_left[0] + 8, hip_left[1] - 7), (hip_right[0] - 8, hip_right[1] - 7), 2, colors["accent"], colors["outline"], caps=False)
        self._draw_chest_shape(surface, chest, left, right, style, colors)
        self._draw_shoulder(surface, _point(left_shoulder), colors, style, hit)
        self._draw_shoulder(surface, _point(right_shoulder), colors, style, hit)
        core = bones.get("energy_core")
        if core and "energy_core" in visual.attachments and style.glow_shape != "none":
            self._draw_glow(surface, _point(core), colors["accent"], style.glow_shape)
        if style.scarf:
            self._draw_scarf(surface, chest, colors)

    def _draw_chest_shape(self, surface, chest, left, right, style, colors) -> None:
        center = ((left[0] + right[0]) * 0.5, (left[1] + right[1]) * 0.5)
        width = max(18.0, abs(right[0] - left[0]) * 0.32)
        if style.torso_shape == "plate":
            points = [(center[0], center[1] - 20), (center[0] + width, center[1] - 5), (center[0] + width * 0.72, center[1] + 23), (center[0], center[1] + 34), (center[0] - width * 0.72, center[1] + 23), (center[0] - width, center[1] - 5)]
            self._poly(surface, points, colors["secondary"], colors, 0.9)
            self._line(surface, (center[0], center[1] - 13), (center[0], center[1] + 24), 3, colors["accent"], colors["outline"], caps=False)
        elif style.torso_shape == "coat":
            self._line(surface, (center[0], center[1] - 17), (center[0], center[1] + 35), 7, colors["cloth_light"], colors["outline"], caps=False)
            self._line(surface, (center[0] - 12, center[1] - 10), (center[0] - 5, center[1] + 29), 2, colors["accent"], colors["outline"], caps=False)
        else:
            self._line(surface, (center[0] - 15, center[1] - 6), (center[0] + 15, center[1] + 24), 5, colors["secondary_light"], colors["outline"], caps=False)
            self._line(surface, (center[0] + 15, center[1] - 6), (center[0] - 15, center[1] + 24), 3, colors["accent"], colors["outline"], caps=False)

    def _draw_shoulder(self, surface, center, colors, style, hit) -> None:
        fill = colors["secondary"] if style.guard_shape != "ribbon" else colors["primary_light"]
        if hit:
            fill = _mix(fill, colors["hit"], 0.3)
        radius = 12 if style.guard_shape == "disc" else 10
        self._joint(surface, center, radius, fill, colors, ring=colors["primary_dark"])
        if style.guard_shape == "shoulder":
            pygame.draw.arc(surface, colors["accent"], pygame.Rect(int(center[0] - radius), int(center[1] - radius), radius * 2, radius * 2), math.pi, math.tau, 2)

    def _draw_arm(self, surface, bones, side, colors, floor_y, style, hit) -> None:
        upper = bones.get(f"{side}_upper_arm")
        forearm = bones.get(f"{side}_forearm")
        hand = bones.get(f"{side}_hand")
        if not upper or not forearm:
            return
        start, elbow = _point(upper, floor_y), _end(upper, floor_y)
        elbow_center, wrist = _point(forearm, floor_y), _end(forearm, floor_y)
        arm = colors["primary"] if side == "right" else colors["primary_dark"]
        guard = colors["secondary"] if side == "right" else colors["secondary_dark"]
        if hit:
            arm = _mix(arm, colors["hit"], 0.25)
            guard = _mix(guard, colors["hit"], 0.2)
        self._line(surface, start, elbow, 13, arm, colors["outline"])
        self._line(surface, elbow_center, wrist, 11, guard, colors["outline"])
        self._joint(surface, elbow_center, 7, colors["accent"], colors, ring=colors["secondary_dark"])
        if hand:
            palm = _point(hand, floor_y)
            self._joint(surface, palm, 8, colors["skin_shadow"] if style.weapon == "fist" else colors["accent"], colors, ring=colors["outline"])
            self._draw_knuckles(surface, palm, colors)
        if style.guard_shape == "ribbon":
            direction = _unit(start, elbow)
            self._line(surface, _offset(start, (-direction[1], direction[0]), 4), _offset(elbow, (-direction[1], direction[0]), 4), 2, colors["accent"], colors["outline"], caps=False)

    def _draw_knuckles(self, surface, palm, colors) -> None:
        for index in range(3):
            x = palm[0] + 4 + index * 3
            y = palm[1] - 2 + abs(index - 1)
            pygame.draw.circle(surface, colors["white"], (int(x), int(y)), 1)

    def _draw_weapon(self, surface, bones, visual, style, colors, floor_y, attacking) -> None:
        weapon = bones.get("weapon")
        if weapon is None or ("weapon" not in visual.attachments and style.weapon not in {"blade", "energy", "staff"}):
            return
        start, tip = _point(weapon, floor_y), _end(weapon, floor_y)
        direction = _unit(start, tip)
        normal = (-direction[1], direction[0])
        if style.weapon == "staff":
            self._line(surface, start, tip, 7, colors["secondary_dark"], colors["outline"])
            self._line(surface, _offset(start, normal, 2), _offset(tip, normal, 2), 2, colors["accent"], colors["outline"], caps=False)
            pygame.draw.circle(surface, colors["accent"], _px(tip), 7)
            return
        if style.weapon == "fist":
            return
        if style.weapon == "energy":
            self._line(surface, start, tip, 9 if attacking else 6, colors["accent"], colors["outline"])
            self._line(surface, _offset(start, normal, 3), _offset(tip, normal, 3), 2, colors["white"], colors["outline"], caps=False)
            pygame.draw.circle(surface, colors["accent_light"], _px(tip), 7 if attacking else 5)
            return
        grip = _offset(start, direction, -10)
        self._line(surface, grip, start, 5, colors["secondary_dark"], colors["outline"])
        width = 8 if attacking else 6
        points = [
            _offset(start, normal, width),
            _offset(start, normal, -width),
            _offset(_offset(tip, normal, 2), direction, 4),
            tip,
            _offset(_offset(tip, normal, -2), direction, 4),
        ]
        self._poly(surface, points, colors["accent"], colors, 0.93)
        self._line(surface, _offset(start, normal, 2), _offset(tip, normal, 1), 2, colors["white"], colors["outline"], caps=False)

    def _draw_head(self, surface, bones, visual, style, colors, snapshot, floor_y, hit) -> None:
        head = bones.get("head")
        neck = bones.get("neck")
        if not head:
            return
        if neck:
            self._line(surface, _point(neck, floor_y), _end(neck, floor_y), 12, colors["skin_shadow"], colors["outline"])
        center = _point(head)
        center = (center[0], min(center[1], floor_y - 28))
        radius = max(16, int(head.thickness * 0.64))
        skin = _mix(colors["skin"], colors["hit"], 0.28) if hit else colors["skin"]
        pygame.draw.circle(surface, colors["outline"], _px(center), radius + 6)
        pygame.draw.circle(surface, colors["skin_shadow"], _px((center[0] - 2, center[1] + 3)), radius + 1)
        pygame.draw.circle(surface, skin, _px(center), radius)
        self._draw_face(surface, center, colors, snapshot.facing, style)
        self._draw_hair(surface, center, radius, style, colors, snapshot.facing, visual)

    def _draw_face(self, surface, center, colors, facing, style) -> None:
        direction = 1 if facing >= 0 else -1
        eye_x = center[0] + direction * max(5, int(0.45 * 16))
        eye_y = center[1] - 4
        if style.mask:
            mask = pygame.Rect(int(center[0] - 18), int(center[1] - 1), 36, 12)
            pygame.draw.rect(surface, colors["ink"], mask, border_radius=5)
            pygame.draw.line(surface, colors["accent"], (mask.left + 5, mask.centery), (mask.right - 5, mask.centery), 2)
        else:
            pygame.draw.circle(surface, colors["white"], (int(eye_x), int(eye_y)), 4)
            pygame.draw.circle(surface, colors["ink"], (int(eye_x + direction), int(eye_y)), 2)
            pygame.draw.line(surface, colors["skin_shadow"], _px((center[0] + direction * 5, center[1] + 4)), _px((center[0] + direction * 11, center[1] + 6)), 2)
            pygame.draw.line(surface, colors["ink"], _px((center[0] + direction * 3, center[1] + 12)), _px((center[0] + direction * 9, center[1] + 11)), 2)

    def _draw_hair(self, surface, center, radius, style, colors, facing, visual) -> None:
        direction = 1 if facing >= 0 else -1
        hair = colors["secondary_dark"]
        if style.hair_shape == "crest":
            points = [(center[0] - radius, center[1] - 5), (center[0] - radius * 0.5, center[1] - radius - 12), (center[0] - 2, center[1] - radius + 2), (center[0] + radius * 0.4, center[1] - radius - 16), (center[0] + radius, center[1] - 4)]
            self._poly(surface, points, hair, colors, 0.9)
        elif style.hair_shape == "veil":
            pygame.draw.arc(surface, colors["outline"], pygame.Rect(int(center[0] - radius - 8), int(center[1] - radius - 6), radius * 2 + 16, radius * 2 + 18), math.pi, math.tau, 9)
            pygame.draw.arc(surface, colors["secondary"], pygame.Rect(int(center[0] - radius - 5), int(center[1] - radius - 3), radius * 2 + 10, radius * 2 + 12), math.pi, math.tau, 5)
        elif style.hair_shape == "topknot":
            pygame.draw.circle(surface, colors["outline"], _px((center[0], center[1] - radius - 8)), 10)
            pygame.draw.circle(surface, hair, _px((center[0], center[1] - radius - 8)), 6)
            pygame.draw.arc(surface, colors["accent"], pygame.Rect(int(center[0] - 14), int(center[1] - radius - 15), 28, 24), math.pi, math.tau, 2)
        elif style.hair_shape == "wind":
            self._line(surface, (center[0] - radius, center[1] - radius * 0.55), (center[0] - radius - 18 * direction, center[1] - radius - 10), 7, hair, colors["outline"])
            self._line(surface, (center[0] - radius + 4, center[1] - radius * 0.3), (center[0] - radius - 14 * direction, center[1] - radius + 10), 4, colors["accent"], colors["outline"])
        elif style.hair_shape == "headband":
            pygame.draw.arc(surface, colors["accent"], pygame.Rect(int(center[0] - radius - 3), int(center[1] - radius - 3), radius * 2 + 6, radius * 2 + 6), math.pi * 0.85, math.pi * 1.9, 4)
            self._line(surface, (center[0] - direction * 8, center[1] - radius + 1), (center[0] - direction * 28, center[1] - radius - 7), 4, colors["accent"], colors["outline"])
        elif style.hair_shape == "horns":
            for sign in (-1, 1):
                points = [(center[0] + sign * 5, center[1] - radius + 3), (center[0] + sign * 18, center[1] - radius - 15), (center[0] + sign * 22, center[1] - radius + 8)]
                self._poly(surface, points, hair, colors, 0.86)
        else:
            pygame.draw.arc(surface, hair, pygame.Rect(int(center[0] - radius), int(center[1] - radius), radius * 2, radius * 2), math.pi, math.tau, 5)

    def _draw_scarf(self, surface, center, colors) -> None:
        points = [(center[0] - 17, center[1] - 7), (center[0] + 17, center[1] - 7), (center[0] + 13, center[1] + 7), (center[0] - 13, center[1] + 7)]
        self._poly(surface, points, colors["accent"], colors, 0.88)

    def _draw_glow(self, surface, center, color, shape) -> None:
        c = _px(center)
        glow = _mix(color, (255, 255, 255), 0.2)
        for radius, alpha in ((18, 30), (12, 55), (7, 220)):
            layer = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(layer, (*color, alpha), (radius + 2, radius + 2), radius)
            surface.blit(layer, (c[0] - radius - 2, c[1] - radius - 2), special_flags=pygame.BLEND_ADD)
        if shape == "diamond":
            pygame.draw.polygon(surface, self.OUTLINE, [(c[0], c[1] - 9), (c[0] + 9, c[1]), (c[0], c[1] + 9), (c[0] - 9, c[1])])
            pygame.draw.polygon(surface, glow, [(c[0], c[1] - 6), (c[0] + 6, c[1]), (c[0], c[1] + 6), (c[0] - 6, c[1])])
        elif shape == "ring":
            pygame.draw.circle(surface, self.OUTLINE, c, 10, 4)
            pygame.draw.circle(surface, glow, c, 7, 2)
        elif shape == "rune":
            pygame.draw.line(surface, glow, (c[0] - 7, c[1]), (c[0] + 7, c[1]), 2)
            pygame.draw.line(surface, glow, (c[0], c[1] - 7), (c[0], c[1] + 7), 2)

    def _draw_action_rim(self, surface, bones, visual, style, colors, snapshot, floor_y) -> None:
        state = getattr(snapshot, "state", "")
        attack_id = getattr(snapshot, "attack_id", "")
        if attack_id:
            hand = bones.get("right_hand")
            if hand:
                center = _point(hand, floor_y)
                radius = 13 if "special" in attack_id or "super" in attack_id else 9
                pygame.draw.circle(surface, colors["outline"], _px(center), radius + 4, 3)
                pygame.draw.arc(surface, colors["accent"], pygame.Rect(int(center[0] - radius), int(center[1] - radius), radius * 2, radius * 2), 0.3, 5.8, 3)
        if state in {"BLOCK_HIGH", "BLOCK_LOW", "BLOCK_STUN"}:
            torso = bones.get("torso_upper")
            if torso:
                center = _point(torso)
                pygame.draw.arc(surface, colors["accent"], pygame.Rect(int(center[0] - 32), int(center[1] - 38), 64, 76), math.pi * 0.9, math.pi * 2.1, 3)
