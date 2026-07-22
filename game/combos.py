from __future__ import annotations

from dataclasses import dataclass

from .collision import AttackData, BoxSpec


@dataclass(frozen=True)
class InputEvent:
    command: str
    time: float
    facing: int


@dataclass(frozen=True)
class ComboMove:
    name: str
    sequence: tuple[str, ...]
    attack: AttackData
    max_age: float = 0.75


class InputBuffer:
    def __init__(self, max_age: float = 1.1) -> None:
        self.max_age = max_age
        self.events: list[InputEvent] = []

    def push(self, command: str, now: float, facing: int) -> None:
        normalized = self._normalize(command, facing)
        if normalized:
            self.events.append(InputEvent(normalized, now, facing))
        self.prune(now)

    def prune(self, now: float) -> None:
        self.events = [event for event in self.events if now - event.time <= self.max_age]

    def tail(self, now: float, max_age: float) -> tuple[str, ...]:
        return tuple(event.command for event in self.events if now - event.time <= max_age)

    def clear(self) -> None:
        self.events.clear()

    def _normalize(self, command: str, facing: int) -> str:
        if command == "left":
            return "back" if facing > 0 else "forward"
        if command == "right":
            return "forward" if facing > 0 else "back"
        return command


SPECIAL_MOVES = {
    "ember_surge": AttackData(
        name="Пепельный всплеск",
        startup=0.12,
        active=0.22,
        recovery=0.32,
        damage=120,
        chip_damage=26,
        hit_stun=0.35,
        block_stun=0.2,
        knockback_x=520,
        knockback_y=-130,
        hitbox=BoxSpec(44, -152, 118, 84),
        energy_gain=90,
        energy_cost=180,
        cancellable=True,
    ),
    "rift_breaker": AttackData(
        name="Разрушитель разлома",
        startup=0.2,
        active=0.18,
        recovery=0.45,
        damage=180,
        chip_damage=42,
        hit_stun=0.48,
        block_stun=0.28,
        knockback_x=760,
        knockback_y=-380,
        hitbox=BoxSpec(34, -190, 132, 145),
        energy_gain=120,
        energy_cost=300,
        launcher=True,
    ),
    "veil_step": AttackData(
        name="Шаг вуали",
        startup=0.1,
        active=0.2,
        recovery=0.25,
        damage=95,
        chip_damage=18,
        hit_stun=0.3,
        block_stun=0.18,
        knockback_x=450,
        knockback_y=-60,
        hitbox=BoxSpec(18, -145, 116, 74),
        energy_gain=70,
        energy_cost=160,
        cancellable=True,
    ),
    "super": AttackData(
        name="Приговор звёздного падения",
        startup=0.28,
        active=0.28,
        recovery=0.62,
        damage=310,
        chip_damage=80,
        hit_stun=0.65,
        block_stun=0.4,
        knockback_x=980,
        knockback_y=-460,
        hitbox=BoxSpec(20, -205, 185, 180),
        energy_gain=0,
        energy_cost=1000,
        finisher="brutality",
    ),
}


DEFAULT_COMBOS = (
    ComboMove(
        "Пепельный всплеск",
        ("down", "forward", "light_punch"),
        SPECIAL_MOVES["ember_surge"],
    ),
    ComboMove(
        "Разрушитель разлома",
        ("back", "down", "forward", "heavy_punch"),
        SPECIAL_MOVES["rift_breaker"],
        max_age=0.95,
    ),
    ComboMove(
        "Шаг вуали",
        ("down", "back", "light_kick"),
        SPECIAL_MOVES["veil_step"],
    ),
    ComboMove(
        "Приговор звёздного падения",
        ("energy", "heavy_punch", "heavy_kick"),
        SPECIAL_MOVES["super"],
        max_age=0.5,
    ),
)


class ComboSystem:
    def __init__(self, moves: tuple[ComboMove, ...] = DEFAULT_COMBOS) -> None:
        self.moves = moves

    def match(self, buffer: InputBuffer, now: float, energy: int) -> AttackData | None:
        for move in sorted(self.moves, key=lambda m: len(m.sequence), reverse=True):
            commands = buffer.tail(now, move.max_age)
            if len(commands) < len(move.sequence):
                continue
            if commands[-len(move.sequence) :] == move.sequence:
                if energy >= move.attack.energy_cost:
                    buffer.clear()
                    return move.attack
        return None

