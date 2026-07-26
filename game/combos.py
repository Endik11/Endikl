from __future__ import annotations

from dataclasses import dataclass

from .collision import AttackData
from .content_registry import get_default_registry


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


def _build_compatibility_views():
    from .definition_adapters import build_legacy_attack, build_legacy_combo
    registry = get_default_registry()
    attacks = {
        definition.legacy_action_name: build_legacy_attack(
            definition, registry.localization.get(definition.display_name_key)
        )
        for definition in registry.attacks.values()
        if definition.legacy_action_name in {"ember_surge", "rift_breaker", "veil_step", "super"}
    }
    combos = tuple(
        build_legacy_combo(
            combo,
            build_legacy_attack(registry.get_attack(combo.resulting_attack_id), registry.localization.get(registry.get_attack(combo.resulting_attack_id).display_name_key)),
            registry.localization.get(combo.display_name_key),
        )
        for combo in registry.combos.values() if combo.enabled
    )
    return attacks, combos


SPECIAL_MOVES, DEFAULT_COMBOS = _build_compatibility_views()


def refresh_combo_views() -> None:
    global DEFAULT_COMBOS
    attacks, combos = _build_compatibility_views()
    SPECIAL_MOVES.clear()
    SPECIAL_MOVES.update(attacks)
    DEFAULT_COMBOS = combos


class ComboSystem:
    def __init__(self, moves: tuple[ComboMove, ...] | None = None) -> None:
        self.moves = DEFAULT_COMBOS if moves is None else moves

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
