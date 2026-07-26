from __future__ import annotations

from dataclasses import replace

from ..combat.input_buffer import InputFrame
from .ai_decision import decide
from .ai_difficulty import AI_DIFFICULTIES
from .ai_memory import AIMemory
from .ai_perception import perceive
from .ai_profile import AIProfile
from .ai_random import AIRandom


class AIController:
    def __init__(self, profile: AIProfile, difficulty: str = "medium", allowed_commands=()) -> None:
        self.profile = profile
        self.difficulty = AI_DIFFICULTIES[difficulty]
        self.allowed_commands = frozenset(allowed_commands)
        self.memory = AIMemory()
        self.rng = AIRandom()
        self._action = None
        self._action_until = -1
        self._previous = frozenset()
        self.reset(1)

    def reset(self, seed: int) -> None:
        self.rng.reset(seed); self.memory.clear(); self._action = None; self._action_until = -1; self._previous = frozenset()

    def build_input(self, snapshot, fighter_id: str, frame_number: int) -> InputFrame:
        reaction = max(0, self.profile.reaction_frames + self.difficulty.reaction_modifier)
        interval = max(1, self.profile.decision_interval_frames + self.difficulty.decision_modifier)
        if frame_number < reaction:
            return InputFrame(frame_number=frame_number)
        view = perceive(snapshot, fighter_id)
        self.memory.remember("jump" if view.opponent_airborne else "attack" if view.opponent_attacking else "idle")
        if self._action is None or frame_number > self._action_until or frame_number % interval == 0:
            self._action = decide(view, self.profile, self.difficulty, self.rng, self.memory)
            self._action_until = frame_number + self._action.duration - 1
        buttons = set(self._action.buttons)
        if self.rng.chance(self.profile.execution_error_probability + self.difficulty.error_modifier):
            buttons.clear(); self.memory.errors.append(self._action.name)
        forbidden = set(self.profile.forbidden_commands)
        buttons -= forbidden
        if self.allowed_commands:
            attacks = {x for x in buttons if x not in {"forward", "back", "left", "right", "up", "down", "block", "throw", "special"}}
            buttons -= {x for x in attacks if x not in self.allowed_commands}
        own = view.self_fighter
        physical = set(buttons)
        physical.discard("forward"); physical.discard("back")
        if "forward" in buttons: physical.add("right" if own.facing > 0 else "left")
        if "back" in buttons: physical.add("left" if own.facing > 0 else "right")
        pressed = frozenset(physical - self._previous); self._previous = frozenset(physical)
        kwargs = {name: name in physical for name in ("left", "right", "up", "down", "light_punch", "heavy_punch", "light_kick", "heavy_kick", "block", "throw", "special")}
        return InputFrame(**kwargs, pressed=pressed, held=frozenset(physical), frame_number=frame_number)
