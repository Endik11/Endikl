from __future__ import annotations

import pygame

from .animation import Animator
from .collision import AttackData, BoxSpec, is_attack_active
from .combos import ComboSystem, InputBuffer
from .content_registry import get_default_registry
from .definition_adapters import build_legacy_attack
from .definitions import FighterDefinition
from .settings import (
    AIR_MOVE_SPEED,
    COLORS,
    FRICTION,
    GRAVITY,
    GROUND_Y,
    JUMP_SPEED,
    LEFT_WALL,
    MAX_ENERGY,
    MAX_HEALTH,
    MOVE_SPEED,
    RIGHT_WALL,
    clamp,
)
from .sprites import SPRITE_ANCHOR, SPRITE_FACTORY


_CONTENT = get_default_registry()
BASE_ATTACKS: dict[str, AttackData] = {}


def refresh_attack_views() -> None:
    BASE_ATTACKS.clear()
    BASE_ATTACKS.update({
        definition.legacy_action_name: build_legacy_attack(
            definition,
            _CONTENT.localization.get(definition.display_name_key),
        )
        for definition in _CONTENT.attacks.values()
        if definition.legacy_action_name in {
            "light_punch", "heavy_punch", "light_kick", "heavy_kick",
            "crouch_punch", "crouch_kick", "air_kick",
        }
    })
    # Emergency content intentionally defines only two attacks; aliases keep
    # every legacy input path safe without duplicating fallback definitions.
    if "light_punch" in BASE_ATTACKS and "heavy_punch" in BASE_ATTACKS:
        BASE_ATTACKS.setdefault("light_kick", BASE_ATTACKS["light_punch"])
        BASE_ATTACKS.setdefault("heavy_kick", BASE_ATTACKS["heavy_punch"])
        BASE_ATTACKS.setdefault("crouch_punch", BASE_ATTACKS["light_punch"])
        BASE_ATTACKS.setdefault("crouch_kick", BASE_ATTACKS["heavy_punch"])
        BASE_ATTACKS.setdefault("air_kick", BASE_ATTACKS["heavy_punch"])


refresh_attack_views()

FIGHTER_RENDER_SCALE = 1.14


FIGHTER_DEFINITIONS = _CONTENT.fighters


class Fighter:
    def __init__(
        self,
        definition: FighterDefinition,
        player_index: int,
        spawn: tuple[float, float],
    ) -> None:
        self.definition = definition
        self.player_index = player_index
        self.spawn = pygame.Vector2(spawn)
        self.pos = pygame.Vector2(spawn)
        self.vel = pygame.Vector2()
        self.facing = 1 if player_index == 0 else -1
        self.health = definition.max_health
        self.max_health = definition.max_health
        self.energy = 0
        self.round_wins = 0
        self.state = "idle"
        self.on_ground = True
        self.crouching = False
        self.blocking = False
        self.dead = False
        self.current_attack: AttackData | None = None
        self.attack_timer = 0.0
        self.attack_has_hit = False
        self.hit_stun = 0.0
        self.block_stun = 0.0
        self.combo_hits = 0
        self.combo_timer = 0.0
        self.last_attack_name = ""
        self.input_buffer = InputBuffer()
        self.stance = "neutral"
        self.throw_timer = 0.0
        self.tag_timer = 0.0
        self.combo_system = ComboSystem()
        self.animator = Animator()
        self.flash_timer = 0.0
        self.trail_timer = 0.0

    @property
    def display_name(self) -> str:
        return self.definition.name

    @property
    def is_busy(self) -> bool:
        return self.current_attack is not None or self.hit_stun > 0 or self.block_stun > 0

    def reset_round(self, spawn_x: float, facing: int) -> None:
        self.pos.update(spawn_x, GROUND_Y)
        self.vel.update(0, 0)
        self.facing = facing
        self.health = self.max_health
        self.energy = min(self.energy, MAX_ENERGY // 2)
        self.state = "idle"
        self.on_ground = True
        self.crouching = False
        self.blocking = False
        self.dead = False
        self.current_attack = None
        self.attack_timer = 0.0
        self.attack_has_hit = False
        self.hit_stun = 0.0
        self.block_stun = 0.0
        self.combo_hits = 0
        self.combo_timer = 0.0
        self.input_buffer.clear()
        self.stance = "neutral"
        self.throw_timer = 0.0
        self.tag_timer = 0.0

    def update_facing(self, opponent_x: float) -> None:
        if self.current_attack is None and self.hit_stun <= 0 and self.block_stun <= 0:
            self.facing = 1 if opponent_x >= self.pos.x else -1

    def update(
        self,
        dt: float,
        controls: dict[str, bool],
        pressed: dict[str, bool],
        now: float,
        allow_control: bool = True,
        training_infinite_energy: bool = False,
    ) -> None:
        if self.dead:
            self._update_animation(dt)
            return

        self.input_buffer.prune(now)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        self.combo_timer = max(0.0, self.combo_timer - dt)
        self.throw_timer = max(0.0, self.throw_timer - dt)
        self.tag_timer = max(0.0, self.tag_timer - dt)
        if self.combo_timer <= 0:
            self.combo_hits = 0

        self._record_pressed_inputs(pressed, now)
        self._update_stun(dt)
        self._update_attack(dt)

        if training_infinite_energy:
            self.energy = MAX_ENERGY

        if allow_control and not self.is_busy:
            self._handle_movement(controls, pressed)
            self._handle_attacks(controls, pressed, now)
        else:
            self.blocking = False
            self.crouching = False if not controls.get("down") else self.crouching
            if self.on_ground:
                self.vel.x *= FRICTION

        self._integrate(dt)
        self._update_animation(dt)

    def _record_pressed_inputs(self, pressed: dict[str, bool], now: float) -> None:
        for command in (
            "left",
            "right",
            "up",
            "down",
            "light_punch",
            "heavy_punch",
            "light_kick",
            "heavy_kick",
            "block",
            "throw",
            "stance",
            "tag",
            "energy",
        ):
            if pressed.get(command):
                self.input_buffer.push(command, now, self.facing)

    def _update_stun(self, dt: float) -> None:
        if self.hit_stun > 0:
            self.hit_stun = max(0.0, self.hit_stun - dt)
        if self.block_stun > 0:
            self.block_stun = max(0.0, self.block_stun - dt)

    def _update_attack(self, dt: float) -> None:
        if self.current_attack is None:
            return
        self.attack_timer += dt
        if self.attack_timer >= self.current_attack.total_time:
            self.current_attack = None
            self.attack_timer = 0.0
            self.attack_has_hit = False

    def _handle_movement(self, controls: dict[str, bool], pressed: dict[str, bool]) -> None:
        self.crouching = self.on_ground and controls.get("down", False)
        self.blocking = (
            self.on_ground
            and controls.get("block", False)
            and not controls.get("up", False)
        )

        if pressed.get("stance"):
            self.stance = "back" if self.stance == "neutral" else "neutral"

        if pressed.get("tag") and self.tag_timer <= 0:
            self.tag_timer = 0.25

        if pressed.get("throw") and self.throw_timer <= 0 and self.on_ground:
            self.throw_timer = 0.25

        if self.crouching or self.blocking:
            self.vel.x *= FRICTION
        else:
            horizontal = int(controls.get("right", False)) - int(controls.get("left", False))
            speed = self.definition.speed if self.on_ground else AIR_MOVE_SPEED
            if horizontal:
                self.vel.x = horizontal * speed
            elif self.on_ground:
                self.vel.x *= FRICTION

        if pressed.get("up") and self.on_ground and not self.crouching and not self.blocking:
            self.vel.y = self.definition.jump_speed
            self.on_ground = False

    def _handle_attacks(
        self,
        controls: dict[str, bool],
        pressed: dict[str, bool],
        now: float,
    ) -> None:
        attack_button = next(
            (
                command
                for command in ("light_punch", "heavy_punch", "light_kick", "heavy_kick")
                if pressed.get(command)
            ),
            None,
        )
        if attack_button is None:
            return

        if self.combo_hits >= 1 and attack_button in ("light_punch", "heavy_punch"):
            attack_button = "heavy_punch"
        elif self.combo_hits >= 1 and attack_button in ("light_kick", "heavy_kick"):
            attack_button = "heavy_kick"

        special = self.combo_system.match(self.input_buffer, now, self.energy)
        if special is not None:
            self.start_attack(special)
            return

        if not self.on_ground:
            attack = BASE_ATTACKS["air_kick"]
        elif self.crouching and attack_button in ("light_punch", "heavy_punch"):
            attack = BASE_ATTACKS["crouch_punch"]
        elif self.crouching and attack_button in ("light_kick", "heavy_kick"):
            attack = BASE_ATTACKS["crouch_kick"]
        else:
            attack = BASE_ATTACKS[attack_button]

        if controls.get("energy") and self.energy >= 100:
            attack = self._empowered_attack(attack)
        self.start_attack(attack)

    def _empowered_attack(self, attack: AttackData) -> AttackData:
        return AttackData(
            name=f"Charged {attack.name}",
            startup=max(0.03, attack.startup - 0.02),
            active=attack.active + 0.04,
            recovery=attack.recovery + 0.04,
            damage=int(attack.damage * 1.22),
            chip_damage=int(attack.chip_damage * 1.4),
            hit_stun=attack.hit_stun + 0.05,
            block_stun=attack.block_stun + 0.04,
            knockback_x=attack.knockback_x * 1.18,
            knockback_y=attack.knockback_y * 1.12,
            hitbox=attack.hitbox,
            energy_gain=attack.energy_gain,
            energy_cost=100,
            cancellable=attack.cancellable,
            launcher=attack.launcher,
            finisher=attack.finisher,
        )

    def start_attack(self, attack: AttackData) -> None:
        if self.current_attack is not None or self.hit_stun > 0 or self.block_stun > 0:
            return
        if self.energy < attack.energy_cost:
            return
        self.energy -= attack.energy_cost
        self.current_attack = attack
        self.attack_timer = 0.0
        self.attack_has_hit = False
        self.last_attack_name = attack.name
        self.blocking = False
        self.state = "attack"

    def _integrate(self, dt: float) -> None:
        if not self.on_ground:
            self.vel.y += GRAVITY * dt

        self.pos += self.vel * dt
        self.pos.x = clamp(self.pos.x, LEFT_WALL, RIGHT_WALL)

        if self.pos.y >= GROUND_Y:
            self.pos.y = GROUND_Y
            self.vel.y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if self.on_ground and abs(self.vel.x) < 8:
            self.vel.x = 0

    def _update_animation(self, dt: float) -> None:
        if self.dead:
            clip = "down"
        elif self.current_attack is not None:
            clip = "attack"
        elif self.hit_stun > 0:
            clip = "hit"
        elif self.block_stun > 0 or self.blocking:
            clip = "block"
        elif not self.on_ground:
            clip = "jump"
        elif self.crouching:
            clip = "crouch"
        elif abs(self.vel.x) > 30:
            clip = "walk"
        else:
            clip = "idle"
        self.state = clip
        self.animator.play(clip)
        self.animator.update(dt)

    def body_rect(self) -> pygame.Rect:
        width = 90
        height = 152 if self.crouching else 218
        return pygame.Rect(
            int(self.pos.x - width / 2),
            int(self.pos.y - height),
            width,
            height,
        )

    def hurtbox(self) -> pygame.Rect:
        rect = self.body_rect().inflate(-14, -10)
        if self.current_attack is not None:
            rect.width += 8
        return rect

    def attack_rect(self) -> pygame.Rect | None:
        if not is_attack_active(self.current_attack, self.attack_timer):
            return None
        return self.current_attack.hitbox.to_rect(self.pos, self.facing)

    def can_be_hit(self) -> bool:
        return not self.dead

    def is_blocking_attack(self, attacker_x: float) -> bool:
        if not self.blocking and self.block_stun <= 0:
            return False
        incoming_from_left = attacker_x < self.pos.x
        facing_incoming = self.facing < 0 if incoming_from_left else self.facing > 0
        return facing_incoming

    def receive_hit(self, attack: AttackData, attacker_x: float, facing: int) -> str:
        blocked = self.is_blocking_attack(attacker_x)
        damage = attack.chip_damage if blocked else attack.damage
        self.health = int(clamp(self.health - damage, -999, self.max_health))
        self.energy = int(clamp(self.energy + (18 if blocked else 30), 0, MAX_ENERGY))
        self.flash_timer = 0.12

        if blocked:
            self.block_stun = max(self.block_stun, attack.block_stun)
            self.vel.x = attack.knockback_x * 0.22 * facing
            if self.on_ground:
                self.vel.y = 0
            return "blocked"

        self.hit_stun = max(self.hit_stun, attack.hit_stun)
        self.vel.x = attack.knockback_x * facing
        if attack.knockback_y < 0 or not self.on_ground:
            self.vel.y = attack.knockback_y
            self.on_ground = False
        self.blocking = False
        self.crouching = False
        if self.health <= 0:
            self.dead = True
            self.state = "down"
        return "hit"

    def grant_hit_reward(self, attack: AttackData) -> None:
        self.energy = int(clamp(self.energy + attack.energy_gain, 0, MAX_ENERGY))
        self.combo_hits += 1
        self.combo_timer = 1.2

    def draw(
        self,
        surface: pygame.Surface,
        offset: pygame.Vector2,
        debug_boxes: bool = False,
    ) -> None:
        base = pygame.Vector2(self.pos.x - offset.x, self.pos.y - offset.y)
        shadow_width = 136 if self.on_ground else 88
        shadow = pygame.Rect(0, 0, shadow_width, 16)
        shadow.center = (int(base.x), int(GROUND_Y + 8 - offset.y))
        pygame.draw.ellipse(surface, (0, 0, 0, 92), shadow)

        sprite = SPRITE_FACTORY.get(
            self.definition,
            self.state,
            self.animator.frame,
            self.facing,
            self.energy,
            flash=self.flash_timer > 0,
        )
        if FIGHTER_RENDER_SCALE != 1:
            sprite = pygame.transform.smoothscale(
                sprite,
                (
                    int(sprite.get_width() * FIGHTER_RENDER_SCALE),
                    int(sprite.get_height() * FIGHTER_RENDER_SCALE),
                ),
            )
        sprite_pos = base - SPRITE_ANCHOR * FIGHTER_RENDER_SCALE
        surface.blit(sprite, (int(sprite_pos.x), int(sprite_pos.y)))

        if debug_boxes:
            hurt = self.hurtbox().move(-offset.x, -offset.y)
            pygame.draw.rect(surface, (70, 170, 255), hurt, 2)
            attack = self.attack_rect()
            if attack:
                pygame.draw.rect(surface, (255, 70, 70), attack.move(-offset.x, -offset.y), 2)
