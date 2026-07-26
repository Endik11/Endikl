from __future__ import annotations

import pygame

from .ai import COMMANDS


class InputManager:
    def __init__(self, settings) -> None:
        self.settings = settings
        self.previous = {
            "p1": {command: False for command in COMMANDS},
            "p2": {command: False for command in COMMANDS},
        }
        self.controls = {
            "p1": {command: False for command in COMMANDS},
            "p2": {command: False for command in COMMANDS},
        }
        self.pressed = {
            "p1": {command: False for command in COMMANDS},
            "p2": {command: False for command in COMMANDS},
        }
        self.joysticks: list[pygame.joystick.Joystick] = []
        pygame.joystick.init()
        self.refresh_joysticks()

    def refresh_joysticks(self) -> None:
        self.joysticks = []
        for index in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(index)
            joystick.init()
            self.joysticks.append(joystick)

    def poll(self) -> tuple[dict[str, dict[str, bool]], dict[str, dict[str, bool]], bool, list[pygame.event.Event]]:
        quit_requested = False
        events = list(pygame.event.get())
        for event in events:
            if event.type == pygame.QUIT:
                quit_requested = True
            elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                self.refresh_joysticks()

        keys = pygame.key.get_pressed()
        self.controls = {
            "p1": self._keyboard_controls(keys, "p1"),
            "p2": self._keyboard_controls(keys, "p2"),
        }
        if self.settings.controls.gamepad_enabled:
            for player, joystick in self._assigned_joysticks().items():
                pad_controls = self._gamepad_controls(joystick)
                for command, held in pad_controls.items():
                    self.controls[player][command] |= held

        self.pressed = {
            player: {
                command: self.controls[player][command] and not self.previous[player][command]
                for command in COMMANDS
            }
            for player in ("p1", "p2")
        }
        self.previous = {
            player: dict(self.controls[player])
            for player in ("p1", "p2")
        }
        return self.controls, self.pressed, quit_requested, events

    def pressed_for(self, player: str) -> dict[str, bool]:
        return self.pressed[player]

    def controls_for(self, player: str) -> dict[str, bool]:
        return self.controls[player]

    def to_combat_frame(self, player: str, frame_number: int):
        from .combat.input_buffer import InputFrame
        held = self.controls_for(player)
        pressed = self.pressed_for(player)
        fields = {key: bool(held.get(key)) for key in (
            "left", "right", "up", "down", "light_punch", "heavy_punch",
            "light_kick", "heavy_kick", "block", "throw",
        )}
        fields["special"] = bool(held.get("energy"))
        fields["pressed"] = frozenset("special" if key == "energy" else key for key, value in pressed.items() if value)
        fields["held"] = frozenset("special" if key == "energy" else key for key, value in held.items() if value)
        fields["frame_number"] = frame_number
        return InputFrame(**fields)

    def _keyboard_controls(self, keys, player: str) -> dict[str, bool]:
        mapping = self.settings.controls.keyboard[player]
        return {command: bool(keys[mapping[command]]) for command in COMMANDS}

    def _assigned_joysticks(self) -> dict[str, pygame.joystick.Joystick]:
        if not self.joysticks:
            return {}
        if len(self.joysticks) == 1:
            return {"p2": self.joysticks[0]}
        return {"p1": self.joysticks[0], "p2": self.joysticks[1]}

    def _gamepad_controls(self, joystick: pygame.joystick.Joystick) -> dict[str, bool]:
        axis_x = joystick.get_axis(0) if joystick.get_numaxes() > 0 else 0.0
        axis_y = joystick.get_axis(1) if joystick.get_numaxes() > 1 else 0.0
        controls = {command: False for command in COMMANDS}
        controls["left"] = axis_x < -0.35
        controls["right"] = axis_x > 0.35
        controls["up"] = axis_y < -0.45
        controls["down"] = axis_y > 0.45
        if joystick.get_numhats() > 0:
            hat_x, hat_y = joystick.get_hat(0)
            controls["left"] |= hat_x < 0
            controls["right"] |= hat_x > 0
            controls["up"] |= hat_y > 0
            controls["down"] |= hat_y < 0
        button_map = {
            "light_punch": 0,
            "heavy_punch": 2,
            "light_kick": 1,
            "heavy_kick": 3,
            "block": 4,
            "energy": 5,
            "pause": 7,
        }
        for command, button in button_map.items():
            if joystick.get_numbuttons() > button:
                controls[command] |= bool(joystick.get_button(button))
        if joystick.get_numaxes() > 5:
            controls["energy"] |= joystick.get_axis(5) > 0.4
        return controls


# Compatibility name used by existing imports.
InputRouter = InputManager
