from __future__ import annotations

import random
from dataclasses import dataclass, field


DIFFICULTY = {
    "easy": {
        "reaction": 0.34,
        "aggression": 0.35,
        "block_chance": 0.15,
        "combo_chance": 0.08,
    },
    "normal": {
        "reaction": 0.22,
        "aggression": 0.55,
        "block_chance": 0.28,
        "combo_chance": 0.18,
    },
    "hard": {
        "reaction": 0.13,
        "aggression": 0.72,
        "block_chance": 0.45,
        "combo_chance": 0.3,
    },
}


COMMANDS = (
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
    "pause",
)


@dataclass
class FighterAI:
    difficulty: str = "normal"
    controls: dict[str, bool] = field(default_factory=lambda: {key: False for key in COMMANDS})
    previous: dict[str, bool] = field(default_factory=lambda: {key: False for key in COMMANDS})
    decision_timer: float = 0.0
    combo_script: list[str] = field(default_factory=list)
    combo_timer: float = 0.0

    def update(self, dt: float, fighter, opponent) -> tuple[dict[str, bool], dict[str, bool]]:
        profile = DIFFICULTY.get(self.difficulty, DIFFICULTY["normal"])
        self.decision_timer -= dt
        self.combo_timer -= dt

        if self.decision_timer <= 0:
            self.decision_timer = random.uniform(profile["reaction"], profile["reaction"] * 1.7)
            self._decide(fighter, opponent, profile)

        if self.combo_script and self.combo_timer <= 0:
            command = self.combo_script.pop(0)
            self.controls[command] = True
            self.combo_timer = 0.08
        else:
            for command in ("light_punch", "heavy_punch", "light_kick", "heavy_kick", "energy"):
                if command not in self.combo_script:
                    self.controls[command] = False

        pressed = {
            command: self.controls.get(command, False) and not self.previous.get(command, False)
            for command in COMMANDS
        }
        self.previous = dict(self.controls)
        return dict(self.controls), pressed

    def _decide(self, fighter, opponent, profile: dict[str, float]) -> None:
        self.controls = {key: False for key in COMMANDS}
        distance = opponent.pos.x - fighter.pos.x
        abs_distance = abs(distance)
        move_toward = "right" if distance > 0 else "left"
        move_back = "left" if distance > 0 else "right"

        incoming = opponent.current_attack is not None and abs_distance < 185
        if incoming and random.random() < profile["block_chance"]:
            self.controls["block"] = True
            if random.random() < 0.3:
                self.controls["down"] = True
            return

        if abs_distance > 180:
            self.controls[move_toward] = True
            if random.random() < 0.06:
                self.controls["up"] = True
            return

        if abs_distance < 78:
            if random.random() < 0.38:
                self.controls[move_back] = True
                return

        if random.random() < profile["combo_chance"] and fighter.energy >= 180:
            self._queue_special(distance)
            return

        if random.random() < profile["aggression"]:
            button = random.choice(("light_punch", "heavy_punch", "light_kick", "heavy_kick"))
            self.controls[button] = True
            if fighter.energy > 450 and random.random() < 0.22:
                self.controls["energy"] = True
        else:
            self.controls[move_back if random.random() < 0.5 else move_toward] = True

    def _queue_special(self, distance: float) -> None:
        forward = "right" if distance > 0 else "left"
        back = "left" if distance > 0 else "right"
        roll = random.random()
        if roll < 0.45:
            self.combo_script = ["down", forward, "light_punch"]
        elif roll < 0.85:
            self.combo_script = [back, "down", forward, "heavy_punch"]
        else:
            self.combo_script = ["energy", "heavy_punch", "heavy_kick"]
        self.combo_timer = 0.01

