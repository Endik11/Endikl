from __future__ import annotations

from .combat.input_buffer import InputFrame


class HumanController:
    def __init__(self, input_manager, player: str) -> None:
        self.input = input_manager
        self.player = player

    def reset(self, seed: int) -> None:
        return None

    def build_input(self, snapshot, fighter_id: str, frame_number: int) -> InputFrame:
        if hasattr(self.input, "to_combat_frame"):
            return self.input.to_combat_frame(self.player, frame_number)
        held = self.input.controls_for(self.player)
        pressed = self.input.pressed_for(self.player)
        names = ("left", "right", "up", "down", "light_punch", "heavy_punch", "light_kick", "heavy_kick", "block", "throw")
        kwargs = {key: bool(held.get(key)) for key in names}
        kwargs["special"] = bool(held.get("energy"))
        kwargs["pressed"] = frozenset("special" if key == "energy" else key for key, value in pressed.items() if value)
        kwargs["held"] = frozenset("special" if key == "energy" else key for key, value in held.items() if value)
        kwargs["frame_number"] = frame_number
        return InputFrame(**kwargs)
