from __future__ import annotations

import math
import random
from array import array
from dataclasses import dataclass

import pygame

from .ai import COMMANDS, FighterAI
from .camera import Camera
from .collision import resolve_body_overlap
from .fatality import FinisherState, detect_finisher, draw_finisher_overlay
from .fighter import FIGHTER_DEFINITIONS, Fighter
from .menu import ARENAS, ArenaSelectScreen, CharacterSelectScreen, CollectionScreen, MenuScreen, SettingsScreen, StatsScreen, draw_text
from .particles import ParticleSystem
from .debug import log_error
from .save import SaveManager
from .shop import ShopScreen
from .settings import (
    COLORS,
    FPS,
    GAME_TITLE,
    GROUND_Y,
    LEFT_WALL,
    MAX_ENERGY,
    RIGHT_WALL,
    SettingsManager,
    VIRTUAL_HEIGHT,
    VIRTUAL_WIDTH,
    clamp,
)


@dataclass
class MatchContext:
    mode: str = "vs"
    p1_key: str = "kael"
    p2_key: str = "sable"
    arena_key: str = "neon_foundry"
    ladder: list[str] | None = None
    ladder_index: int = 0


class ToneBank:
    """Tiny generated sounds so the prototype has feedback without assets."""

    def __init__(self, volume: float) -> None:
        self.enabled = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.enabled = True
            self.sounds = {
                "hit": self._tone(140, 0.08, volume),
                "block": self._tone(96, 0.06, volume * 0.8),
                "select": self._tone(520, 0.05, volume * 0.6),
                "ko": self._tone(70, 0.35, volume),
            }
        except pygame.error:
            self.enabled = False

    def _tone(self, frequency: float, seconds: float, volume: float) -> pygame.mixer.Sound:
        sample_rate = 44100
        count = int(sample_rate * seconds)
        samples = array("h")
        for i in range(count):
            envelope = 1.0 - (i / max(1, count))
            value = int(math.sin(i * math.tau * frequency / sample_rate) * 24000 * volume * envelope)
            samples.append(value)
        return pygame.mixer.Sound(buffer=samples)

    def play(self, name: str) -> None:
        if self.enabled and name in self.sounds:
            self.sounds[name].play()


class InputRouter:
    def __init__(self, settings) -> None:
        self.settings = settings
        self.previous = {
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
        events: list[pygame.event.Event] = []
        for event in pygame.event.get():
            events.append(event)
            if event.type == pygame.QUIT:
                quit_requested = True
            elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                self.refresh_joysticks()

        keys = pygame.key.get_pressed()
        controls = {
            "p1": self._keyboard_controls(keys, "p1"),
            "p2": self._keyboard_controls(keys, "p2"),
        }

        if self.settings.controls.gamepad_enabled:
            for player, joystick in self._assigned_joysticks().items():
                pad_controls = self._gamepad_controls(joystick)
                for command, held in pad_controls.items():
                    controls[player][command] = controls[player][command] or held

        pressed = {
            player: {
                command: controls[player][command] and not self.previous[player][command]
                for command in COMMANDS
            }
            for player in ("p1", "p2")
        }
        self.previous = {
            player: {command: controls[player][command] for command in COMMANDS}
            for player in ("p1", "p2")
        }
        return controls, pressed, quit_requested, events

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
                controls[command] = controls[command] or joystick.get_button(button)
        if joystick.get_numaxes() > 5:
            controls["energy"] = controls["energy"] or joystick.get_axis(5) > 0.4
        return controls


class GameEngine:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load()
        self.save_manager = SaveManager()
        self.profile = self.save_manager.load()

        self.screen = self._create_display()
        self.canvas = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT)).convert()
        self.clock = pygame.time.Clock()
        self.fonts = self._load_fonts()
        self.input = InputRouter(self.settings)
        self.audio = ToneBank(self.settings.audio.sfx_volume)
        self.camera = Camera()
        self.particles = ParticleSystem()
        self.finisher = FinisherState()

        self.state = "menu"
        self.running = True
        self.time = 0.0
        self.menu_screen = MenuScreen()
        self.settings_screen = SettingsScreen(self.settings)
        self.character_screen: CharacterSelectScreen | None = None
        self.arena_screen: ArenaSelectScreen | None = None
        self.collection_screen = CollectionScreen(self.profile)
        self.stats_screen = StatsScreen(self.profile)
        self.context = MatchContext()
        self.fighters: list[Fighter] = []
        self.ai: FighterAI | None = None
        self.round_index = 1
        self.round_timer = self.settings.gameplay.round_seconds
        self.round_phase = "intro"
        self.phase_timer = 1.5
        self.match_message = ""
        self.match_winner_index: int | None = None
        self.pending_finisher: str | None = None
        self.debug_boxes = False
        self.pause_selected = 0
        self.pause_items = [("Продолжить", "resume"), ("Настройки", "settings"), ("Рестарт", "restart"), ("Главное меню", "menu"), ("Выйти", "quit_game")]
        self.shop_screen = ShopScreen()
        self.pause_confirm = False
        self.pending_quit = False
        self.pause_button_rects: list[pygame.Rect] = []
        self.pause_hover_index: int | None = None

    def _create_display(self) -> pygame.Surface:
        flags = pygame.RESIZABLE
        if self.settings.video.fullscreen:
            flags |= pygame.FULLSCREEN
        return pygame.display.set_mode(
            (self.settings.video.width, self.settings.video.height),
            flags,
        )

    def _load_fonts(self) -> dict[str, pygame.font.Font]:
        return {
            "title": pygame.font.SysFont("Segoe UI", 72, bold=True),
            "subtitle": pygame.font.SysFont("Segoe UI", 42, bold=True),
            "menu": pygame.font.SysFont("Segoe UI", 32, bold=True),
            "body": pygame.font.SysFont("Segoe UI", 24),
            "small": pygame.font.SysFont("Segoe UI", 19),
            "tiny": pygame.font.SysFont("Segoe UI", 15),
        }

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 1 / 30)
            self.time += dt
            controls, pressed, quit_requested, events = self.input.poll()
            if quit_requested:
                self.running = False

            self._update(dt, controls, pressed, events)
            self._draw()
            self._present()

        self.settings_manager.save()
        self.save_manager.save()
        pygame.quit()

    def _update(
        self,
        dt: float,
        controls: dict[str, dict[str, bool]],
        pressed: dict[str, dict[str, bool]],
        events: list[pygame.event.Event],
    ) -> None:
        if pressed["p1"].get("heavy_punch") and pressed["p1"].get("heavy_kick") and pressed["p1"].get("block"):
            self.debug_boxes = not self.debug_boxes

        if self.state == "menu":
            action = self.menu_screen.update(pressed["p1"], events)
            self._handle_menu_action(action)
        elif self.state == "settings":
            action = self.settings_screen.update(pressed["p1"], events)
            if action == "back":
                self.settings_manager.settings = self.settings_screen.settings
                self.settings_manager.save()
                self.settings = self.settings_manager.settings
                self.screen = self._create_display()
                self.audio = ToneBank(self.settings.audio.sfx_volume)
                self.state = "pause" if self.round_phase == "paused_settings" else "menu"
                if self.round_phase == "paused_settings":
                    self.round_phase = "fight"
        elif self.state == "shop":
            action = self.shop_screen.update(pressed["p1"], self.profile, self.save_manager, events)
            if action == "back":
                self.state = "menu"
        elif self.state == "collection":
            action = self.collection_screen.update(pressed["p1"], events)
            if action == "back":
                self.state = "menu"
        elif self.state == "stats":
            action = self.stats_screen.update(pressed["p1"], events)
            if action == "back":
                self.state = "menu"
        elif self.state == "character_select" and self.character_screen:
            action = self.character_screen.update(pressed["p1"], pressed["p2"], events)
            if action == "arena":
                self.context.p1_key = self.character_screen.p1_key
                self.context.p2_key = self.character_screen.p2_key
                self.profile.selected_fighter = self.context.p1_key
                self.save_manager.save()
                self._start_match()
                self.audio.play("select")
            elif action == "back":
                self.state = "menu"
        elif self.state == "arena_select" and self.arena_screen:
            action = self.arena_screen.update(pressed["p1"], events)
            if action == "fight":
                self.context.arena_key = self.arena_screen.arena_key
                self.profile.selected_arena = self.context.arena_key
                self.save_manager.save()
                self._start_match()
                self.audio.play("select")
            elif action == "back":
                self.state = "menu"
        elif self.state == "fight":
            self._update_fight(dt, controls, pressed)
        elif self.state == "pause":
            self._update_pause(pressed, events)
        elif self.state == "match_over":
            if self.phase_timer > 0:
                self.phase_timer -= dt
            if self.phase_timer <= 0 and accept_pressed_any(pressed["p1"]):
                if self._has_next_ladder_match():
                    self.context.ladder_index += 1
                    self.context.p2_key = self.context.ladder[self.context.ladder_index]
                    self._start_match(reset_ladder=False)
                else:
                    self.state = "menu"

    def _handle_menu_action(self, action: str | None) -> None:
        if action is None:
            return
        self.audio.play("select")
        if action == "quit":
            self.running = False
        elif action == "settings":
            self.state = "settings"
        elif action == "shop":
            self.state = "shop"
        elif action == "collection":
            self.state = "collection"
        elif action == "stats":
            self.state = "stats"
        elif action == "arena":
            self.arena_screen = ArenaSelectScreen(self.profile.selected_arena)
            self.state = "arena_select"
        elif action in ("story", "arcade", "tournament", "vs", "training"):
            self.context = MatchContext(mode=action)
            if action in ("story", "arcade", "tournament"):
                self.context.ladder = self._build_ladder(self.profile.selected_fighter)
                self.context.ladder_index = 0
                if self.context.ladder:
                    self.context.p2_key = self.context.ladder[0]
            self.character_screen = CharacterSelectScreen(
                mode=action,
                p1_key=self.profile.selected_fighter,
                p2_key=self.context.p2_key,
            )
            self.state = "character_select"

    def _build_ladder(self, p1_key: str) -> list[str]:
        keys = [key for key in FIGHTER_DEFINITIONS if key != p1_key]
        random.shuffle(keys)
        return keys

    def _start_match(self, reset_ladder: bool = True) -> None:
        if reset_ladder and self.context.mode in ("story", "arcade", "tournament"):
            self.context.ladder = self._build_ladder(self.context.p1_key)
            if self.context.p2_key in self.context.ladder:
                self.context.ladder.remove(self.context.p2_key)
            self.context.ladder.insert(0, self.context.p2_key)
            self.context.ladder_index = 0

        p1 = Fighter(FIGHTER_DEFINITIONS[self.context.p1_key], 0, (350, GROUND_Y))
        p2 = Fighter(FIGHTER_DEFINITIONS[self.context.p2_key], 1, (930, GROUND_Y))
        self.fighters = [p1, p2]
        self.ai = None
        if self.context.mode in ("story", "arcade", "tournament"):
            difficulty = self.settings.gameplay.difficulty
            if self.context.mode == "story":
                difficulty = "normal"
            elif self.context.mode == "tournament" and self.context.ladder_index >= 1:
                difficulty = "hard"
            self.ai = FighterAI(difficulty)

        self.round_index = 1
        self.round_timer = (
            999 if self.context.mode == "training" else self.settings.gameplay.round_seconds
        )
        self.round_phase = "intro"
        self.phase_timer = 1.6
        self.match_winner_index = None
        self.pending_finisher = None
        self.finisher.reset()
        self.particles = ParticleSystem()
        self.camera = Camera()
        self.state = "fight"

    def _update_fight(
        self,
        dt: float,
        controls: dict[str, dict[str, bool]],
        pressed: dict[str, dict[str, bool]],
    ) -> None:
        if not self.fighters:
            self.state = "menu"
            return

        if pressed["p1"].get("pause") or pressed["p2"].get("pause"):
            self.state = "pause"
            return

        p1_controls, p1_pressed = controls["p1"], pressed["p1"]
        if self.ai:
            p2_controls, p2_pressed = self.ai.update(dt, self.fighters[1], self.fighters[0])
        else:
            p2_controls, p2_pressed = controls["p2"], pressed["p2"]

        if self.round_phase == "intro":
            self.phase_timer -= dt
            self._update_fighters(dt, p1_controls, p1_pressed, p2_controls, p2_pressed, allow_control=False)
            if self.phase_timer <= 0:
                self.round_phase = "fight"
            return

        if self.round_phase == "round_over":
            self.phase_timer -= dt
            self._update_fighters(dt, p1_controls, p1_pressed, p2_controls, p2_pressed, allow_control=False)
            if self.phase_timer <= 0:
                self._next_round()
            return

        if self.round_phase == "finisher":
            self._update_finisher(dt, p1_controls, p1_pressed, p2_controls, p2_pressed)
            return

        self.round_timer -= dt
        self._update_fighters(dt, p1_controls, p1_pressed, p2_controls, p2_pressed, allow_control=True)
        self._resolve_combat()
        self._check_round_end()

        if self.context.mode == "training":
            for fighter in self.fighters:
                if fighter.health <= 0:
                    fighter.health = fighter.max_health
                    fighter.dead = False
                    fighter.energy = MAX_ENERGY
                    fighter.pos.y = GROUND_Y
                    fighter.vel.update(0, 0)

    def _update_fighters(
        self,
        dt: float,
        p1_controls: dict[str, bool],
        p1_pressed: dict[str, bool],
        p2_controls: dict[str, bool],
        p2_pressed: dict[str, bool],
        allow_control: bool,
    ) -> None:
        p1, p2 = self.fighters
        p1.update_facing(p2.pos.x)
        p2.update_facing(p1.pos.x)
        training_energy = self.context.mode == "training" and self.settings.gameplay.training_infinite_energy
        p1.update(dt, p1_controls, p1_pressed, self.time, allow_control, training_energy)
        p2.update(dt, p2_controls, p2_pressed, self.time, allow_control and self.context.mode != "training", training_energy)

        left_push, right_push = resolve_body_overlap(p1.body_rect(), p2.body_rect())
        p1.pos.x = clamp(p1.pos.x + left_push, LEFT_WALL, RIGHT_WALL)
        p2.pos.x = clamp(p2.pos.x + right_push, LEFT_WALL, RIGHT_WALL)

        focus = (p1.pos.x + p2.pos.x) / 2
        self.camera.update(dt, focus)
        if self.settings.video.particles:
            self.particles.ambient(dt)
            self.particles.update(dt)

    def _resolve_combat(self) -> None:
        self._resolve_attack(self.fighters[0], self.fighters[1])
        self._resolve_attack(self.fighters[1], self.fighters[0])

    def _resolve_attack(self, attacker: Fighter, defender: Fighter) -> None:
        attack = attacker.current_attack
        rect = attacker.attack_rect()
        if attack is None or rect is None or attacker.attack_has_hit or not defender.can_be_hit():
            return
        if not rect.colliderect(defender.hurtbox()):
            return
        result = defender.receive_hit(attack, attacker.pos.x, attacker.facing)
        attacker.attack_has_hit = True
        if result == "hit":
            attacker.grant_hit_reward(attack)
            color = attacker.definition.palette[1]
            self.audio.play("hit")
            if self.settings.video.camera_shake:
                self.camera.shake(11 if attack.damage < 150 else 18)
            if self.settings.video.particles:
                self.particles.burst(pygame.Vector2(rect.center), color, count=22, power=520)
        else:
            self.audio.play("block")
            if self.settings.video.camera_shake:
                self.camera.shake(5)
            if self.settings.video.particles:
                self.particles.burst(pygame.Vector2(rect.center), COLORS["cyan"], count=10, power=260)

    def _check_round_end(self) -> None:
        if self.context.mode == "training":
            return
        if self.round_timer <= 0:
            if self.fighters[0].health == self.fighters[1].health:
                winner_index = random.choice((0, 1))
            else:
                winner_index = 0 if self.fighters[0].health > self.fighters[1].health else 1
            self._end_round(winner_index, timeout=True)
            return

        for index, fighter in enumerate(self.fighters):
            if fighter.health <= 0:
                self._end_round(1 - index, timeout=False)
                return

    def _end_round(self, winner_index: int, timeout: bool) -> None:
        winner = self.fighters[winner_index]
        loser = self.fighters[1 - winner_index]
        winner.round_wins += 1
        final_round = winner.round_wins >= self.settings.gameplay.rounds_to_win
        self.audio.play("ko")
        if final_round and not timeout:
            self.round_phase = "finisher"
            self.phase_timer = 4.0
            self.match_winner_index = winner_index
            self.finisher.start(winner_index, 1 - winner_index)
            loser.dead = True
        elif final_round:
            self.match_winner_index = winner_index
            self._finish_match("victory")
        else:
            self.round_phase = "round_over"
            self.phase_timer = 2.1
            self.match_message = f"{winner.display_name} wins the round"

    def _update_finisher(
        self,
        dt: float,
        p1_controls: dict[str, bool],
        p1_pressed: dict[str, bool],
        p2_controls: dict[str, bool],
        p2_pressed: dict[str, bool],
    ) -> None:
        winner_index = self.finisher.winner_index
        winner = self.fighters[winner_index]
        loser = self.fighters[self.finisher.loser_index]
        winner_controls = p1_controls if winner_index == 0 else p2_controls
        winner_pressed = p1_pressed if winner_index == 0 else p2_pressed
        finisher = detect_finisher(winner, loser, winner_pressed, LEFT_WALL, RIGHT_WALL)
        if finisher:
            self.finisher.select(finisher)
            self.pending_finisher = finisher
            if self.settings.video.particles:
                self.particles.burst(loser.pos + pygame.Vector2(0, -100), COLORS["red"], count=42, power=700)
            if self.settings.video.camera_shake:
                self.camera.shake(26, 0.45)

        self._update_fighters(
            dt,
            p1_controls,
            p1_pressed,
            p2_controls,
            p2_pressed,
            allow_control=False,
        )
        if winner_controls.get("left") or winner_controls.get("right"):
            winner.vel.x *= 0.8

        selected = self.finisher.update(dt)
        if selected:
            self.phase_timer -= dt
            if self.phase_timer <= 0:
                self._finish_match(self.finisher.chosen or "victory")

    def _finish_match(self, finisher: str | None) -> None:
        winner_index = self.match_winner_index if self.match_winner_index is not None else 0
        winner = self.fighters[winner_index]
        player_won = winner_index == 0
        perfect = player_won and self.fighters[0].health == self.fighters[0].max_health
        if player_won:
            self.save_manager.record_win(finisher, perfect)
            self.save_manager.award_currency(150 if self.context.mode == "vs" else 250)
            if self.context.mode == "arcade" and not self._has_next_ladder_match():
                self.profile.arcade_clears += 1
                self.save_manager.unlock("glass_court", "arena")
                self.save_manager.award_currency(500)
            if self.context.mode == "story":
                self.profile.story_chapter = max(self.profile.story_chapter, self.context.ladder_index + 2)
                self.save_manager.award_currency(300)
        else:
            self.save_manager.record_loss()

        if player_won and self._has_next_ladder_match():
            next_key = self.context.ladder[self.context.ladder_index + 1]
            self.match_message = f"{winner.display_name} advances. Next: {FIGHTER_DEFINITIONS[next_key].name}"
        elif player_won:
            self.match_message = f"{winner.display_name} conquers the ladder"
        else:
            self.match_message = f"{winner.display_name} wins the match"
        self.state = "match_over"
        self.round_phase = "match_over"
        self.phase_timer = 0.8
        self.finisher.reset()
        self.save_manager.save()

    def _has_next_ladder_match(self) -> bool:
        return (
            self.context.mode in ("story", "arcade", "tournament")
            and self.context.ladder is not None
            and self.context.ladder_index + 1 < len(self.context.ladder)
            and self.match_winner_index == 0
        )

    def _next_round(self) -> None:
        self.round_index += 1
        self.round_timer = self.settings.gameplay.round_seconds
        self.round_phase = "intro"
        self.phase_timer = 1.2
        self.match_message = ""
        self.fighters[0].reset_round(350, 1)
        self.fighters[1].reset_round(930, -1)

    def _update_pause(self, pressed: dict[str, dict[str, bool]], events: list[pygame.event.Event]) -> None:
        p1 = pressed.get("p1", {})
        p2 = pressed.get("p2", {})

        if self.pending_quit:
            if p1.get("light_punch") or p1.get("heavy_punch") or p1.get("energy") or p2.get("light_punch") or p2.get("heavy_punch") or p2.get("energy"):
                self.running = False
            elif p1.get("block") or p2.get("block"):
                self.pending_quit = False
            return

        self.pause_button_rects = []
        mouse_pos = self._screen_to_virtual(pygame.mouse.get_pos())
        for index, (label, _) in enumerate(self.pause_items):
            y = 298 + index * 46
            rect = pygame.Rect(490, y - 12, 300, 30)
            self.pause_button_rects.append(rect)
            if rect.collidepoint(mouse_pos):
                self.pause_selected = index
                self.pause_hover_index = index
                break
        else:
            self.pause_hover_index = None

        if p1.get("down") or p2.get("down"):
            self.pause_selected = (self.pause_selected + 1) % len(self.pause_items)
        if p1.get("up") or p2.get("up"):
            self.pause_selected = (self.pause_selected - 1) % len(self.pause_items)
        if p1.get("pause") or p2.get("pause"):
            self.state = "fight"
            return
        if p1.get("block") or p2.get("block"):
            self.state = "fight"
            return
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, rect in enumerate(self.pause_button_rects):
                    if rect.collidepoint(mouse_pos):
                        self._activate_pause_action(self.pause_items[index][1])
                        return
        if p1.get("light_punch") or p1.get("heavy_punch") or p1.get("energy") or p2.get("light_punch") or p2.get("heavy_punch") or p2.get("energy"):
            self._activate_pause_action(self.pause_items[self.pause_selected][1])

    def _activate_pause_action(self, action: str) -> None:
        if action == "resume":
            self.state = "fight"
        elif action == "settings":
            self.round_phase = "paused_settings"
            self.state = "settings"
        elif action == "restart":
            self._start_match(reset_ladder=False)
            self.state = "fight"
        elif action == "menu":
            self.fighters = []
            self.state = "menu"
        elif action == "quit_game":
            self.pending_quit = True

    def _screen_to_virtual(self, pos: tuple[int, int]) -> tuple[int, int]:
        screen_w, screen_h = self.screen.get_size()
        if screen_w <= 0 or screen_h <= 0:
            return pos
        if (screen_w, screen_h) == (VIRTUAL_WIDTH, VIRTUAL_HEIGHT):
            return pos
        return (
            int(pos[0] * VIRTUAL_WIDTH / screen_w),
            int(pos[1] * VIRTUAL_HEIGHT / screen_h),
        )

    def _draw(self) -> None:
        if self.state == "menu":
            self.menu_screen.draw(self.canvas, self.fonts, self.time)
        elif self.state == "settings":
            self.settings_screen.draw(self.canvas, self.fonts, self.time)
        elif self.state == "shop":
            self.shop_screen.draw(self.canvas, self.fonts, self.time, self.profile)
        elif self.state == "collection":
            self.collection_screen.draw(self.canvas, self.fonts, self.time)
        elif self.state == "stats":
            self.stats_screen.draw(self.canvas, self.fonts, self.time)
        elif self.state == "character_select" and self.character_screen:
            self.character_screen.draw(self.canvas, self.fonts, self.time)
        elif self.state == "arena_select" and self.arena_screen:
            self.arena_screen.draw(self.canvas, self.fonts, self.time)
        elif self.state in ("fight", "pause", "match_over"):
            self._draw_fight()
            if self.state == "pause":
                self._draw_pause()
            elif self.state == "match_over":
                self._draw_match_over()

    def _draw_fight(self) -> None:
        self._draw_arena()
        offset = self.camera.offset
        for fighter in sorted(self.fighters, key=lambda f: f.pos.y):
            fighter.draw(self.canvas, offset, debug_boxes=self.debug_boxes)
        if self.settings.video.particles:
            self.particles.draw(self.canvas, offset)
        self._draw_hud()
        if self.round_phase == "intro":
            label = "ФИНАЛЬНЫЙ РАУНД" if self.round_index >= self.settings.gameplay.rounds_to_win * 2 - 1 else f"РАУНД {self.round_index}"
            draw_text(self.canvas, self.fonts["title"], label, (VIRTUAL_WIDTH // 2, 196), COLORS["gold"], center=True)
            draw_text(self.canvas, self.fonts["menu"], "БОЙ", (VIRTUAL_WIDTH // 2, 272), COLORS["white"], center=True)
        elif self.round_phase == "round_over":
            draw_text(self.canvas, self.fonts["menu"], self.match_message, (VIRTUAL_WIDTH // 2, 210), COLORS["gold"], center=True)
        elif self.round_phase == "finisher":
            draw_finisher_overlay(self.canvas, self.fonts["title"], self.fonts["small"], self.finisher)

    def _draw_arena(self) -> None:
        arena = ARENAS[self.context.arena_key]
        base, primary, accent = arena.palette
        self.canvas.fill(base)
        for y in range(VIRTUAL_HEIGHT):
            blend = y / VIRTUAL_HEIGHT
            color = (
                int(base[0] + blend * 18),
                int(base[1] + blend * 18),
                int(base[2] + blend * 24),
            )
            pygame.draw.line(self.canvas, color, (0, y), (VIRTUAL_WIDTH, y))

        parallax = int(self.camera.offset.x * 0.24)
        for i in range(13):
            x = i * 130 - 70 - parallax
            h = 150 + (i % 5) * 46
            rect = pygame.Rect(x, GROUND_Y - h - 50, 90, h)
            pygame.draw.rect(self.canvas, (14, 17, 22), rect)
            pygame.draw.line(self.canvas, primary, (rect.left, rect.top + 14), (rect.right, rect.top + 14), 2)

        if arena.key == "neon_foundry":
            self._draw_foundry(primary, accent)
        elif arena.key == "storm_pier":
            self._draw_pier(primary, accent)
        elif arena.key == "glass_court":
            self._draw_glass_court(primary, accent)
        elif arena.key == "great_wall":
            self._draw_great_wall(primary, accent)
        elif arena.key == "dragon_mountains":
            self._draw_dragon_mountains(primary, accent)
        else:
            self._draw_pagoda_ridge(primary, accent)

        pygame.draw.rect(self.canvas, (20, 22, 24), (0, GROUND_Y, VIRTUAL_WIDTH, VIRTUAL_HEIGHT - GROUND_Y))
        for x in range(-120, VIRTUAL_WIDTH + 160, 72):
            sx = x - int(self.camera.offset.x * 0.15)
            pygame.draw.line(self.canvas, (48, 52, 55), (sx, GROUND_Y), (sx + 90, VIRTUAL_HEIGHT), 1)
        pygame.draw.line(self.canvas, accent, (0, GROUND_Y), (VIRTUAL_WIDTH, GROUND_Y), 4)
        pygame.draw.rect(self.canvas, (9, 10, 12), (0, GROUND_Y + 94, VIRTUAL_WIDTH, 60))

    def _draw_foundry(self, primary, accent) -> None:
        glow = int(80 + math.sin(self.time * 2.2) * 30)
        pygame.draw.circle(self.canvas, (*primary,), (1040, 210), 76, 3)
        pygame.draw.rect(self.canvas, (48, 20, 18), (830, 430, 280, 28), border_radius=8)
        pygame.draw.rect(self.canvas, (glow + 80, 64, 32), (860, 446, 220, 34), border_radius=8)
        for x in range(160, 540, 72):
            pygame.draw.line(self.canvas, accent, (x, 210), (x + 26, 510), 2)

    def _draw_pier(self, primary, accent) -> None:
        water_y = GROUND_Y - 45
        for x in range(0, VIRTUAL_WIDTH, 90):
            wave = math.sin(self.time * 2 + x * 0.02) * 8
            pygame.draw.arc(self.canvas, primary, (x, water_y + wave, 90, 32), 0, math.pi, 2)
        pygame.draw.circle(self.canvas, accent, (1030, 118), 54)
        pygame.draw.line(self.canvas, (190, 190, 170), (220, 230), (1020, 300), 2)

    def _draw_glass_court(self, primary, accent) -> None:
        for i in range(11):
            x = 100 + i * 105
            y = 160 + math.sin(self.time + i) * 12
            points = [(x, y), (x + 52, y + 34), (x + 12, y + 98)]
            pygame.draw.polygon(self.canvas, (42, 44, 58), points)
            pygame.draw.polygon(self.canvas, accent if i % 2 else primary, points, 2)
        pygame.draw.rect(self.canvas, (33, 29, 44), (250, 430, 780, 54), border_radius=10)

    def _draw_great_wall(self, primary, accent) -> None:
        for i in range(8):
            x = 110 + i * 120
            height = 140 + (i % 3) * 24
            pygame.draw.rect(self.canvas, (92, 76, 54), (x, GROUND_Y - height - 56, 70, height), border_radius=6)
            pygame.draw.rect(self.canvas, accent, (x + 8, GROUND_Y - height - 46, 54, height - 10), border_radius=4)
        pygame.draw.rect(self.canvas, primary, (140, 390, 980, 18), border_radius=4)

    def _draw_dragon_mountains(self, primary, accent) -> None:
        for i, x in enumerate((180, 440, 770, 1050)):
            points = [(x - 130, GROUND_Y), (x - 60, 260 + i * 20), (x, 200), (x + 70, 270 + i * 18), (x + 140, GROUND_Y)]
            pygame.draw.polygon(self.canvas, (22, 36, 34), points)
            pygame.draw.polygon(self.canvas, accent if i % 2 else primary, points, 3)
        pygame.draw.circle(self.canvas, (242, 202, 132), (980, 128), 26)

    def _draw_pagoda_ridge(self, primary, accent) -> None:
        for i in range(6):
            x = 120 + i * 180
            pygame.draw.rect(self.canvas, (74, 52, 60), (x, 418, 58, 90), border_radius=8)
            pygame.draw.rect(self.canvas, accent, (x + 10, 404, 38, 24), border_radius=4)
            pygame.draw.line(self.canvas, primary, (x + 6, 468), (x + 52, 468), 3)
        pygame.draw.circle(self.canvas, accent, (980, 144), 34)

    def _draw_hud(self) -> None:
        p1, p2 = self.fighters
        self._draw_bar(74, 42, 470, 28, p1.health / p1.max_health, COLORS["red"], flip=False)
        self._draw_bar(736, 42, 470, 28, p2.health / p2.max_health, COLORS["red"], flip=True)
        self._draw_bar(74, 82, 360, 16, p1.energy / MAX_ENERGY, COLORS["cyan"], flip=False)
        self._draw_bar(846, 82, 360, 16, p2.energy / MAX_ENERGY, COLORS["cyan"], flip=True)
        draw_text(self.canvas, self.fonts["body"], p1.display_name, (78, 12), COLORS["white"])
        name = self.fonts["body"].render(p2.display_name, True, COLORS["white"])
        self.canvas.blit(name, name.get_rect(topright=(1206, 12)))

        timer_value = "∞" if self.context.mode == "training" else str(max(0, int(self.round_timer) + 1))
        pygame.draw.rect(self.canvas, COLORS["panel"], (591, 28, 98, 78), border_radius=8)
        pygame.draw.rect(self.canvas, COLORS["gold"], (591, 28, 98, 78), 2, border_radius=8)
        draw_text(self.canvas, self.fonts["menu"], timer_value, (640, 54), COLORS["gold"], center=True)

        self._draw_round_marks(78, 106, p1.round_wins)
        self._draw_round_marks(1144, 106, p2.round_wins, flip=True)

        for fighter, x in ((p1, 78), (p2, 930)):
            if fighter.combo_hits >= 2 and fighter.combo_timer > 0:
                draw_text(
                    self.canvas,
                    self.fonts["small"],
                    f"{fighter.combo_hits} КОМБО",
                    (x, 126),
                    COLORS["gold"],
                )
            if fighter.last_attack_name and fighter.current_attack:
                draw_text(self.canvas, self.fonts["tiny"], fighter.last_attack_name, (x, 148), COLORS["muted"])

    def _draw_bar(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        ratio: float,
        color: tuple[int, int, int],
        flip: bool,
    ) -> None:
        ratio = clamp(ratio, 0.0, 1.0)
        pygame.draw.rect(self.canvas, COLORS["panel"], (x, y, width, height), border_radius=5)
        fill_width = int(width * ratio)
        fill_x = x + width - fill_width if flip else x
        pygame.draw.rect(self.canvas, color, (fill_x, y, fill_width, height), border_radius=5)
        pygame.draw.rect(self.canvas, COLORS["white"], (x, y, width, height), 2, border_radius=5)

    def _draw_round_marks(self, x: int, y: int, wins: int, flip: bool = False) -> None:
        direction = -1 if flip else 1
        for i in range(self.settings.gameplay.rounds_to_win):
            cx = x + i * 22 * direction
            color = COLORS["gold"] if i < wins else COLORS["panel_light"]
            pygame.draw.circle(self.canvas, color, (cx, y), 7)

    def _draw_pause(self) -> None:
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.canvas.blit(overlay, (0, 0))
        panel = pygame.Rect(466, 184, 348, 310)
        pygame.draw.rect(self.canvas, COLORS["panel"], panel, border_radius=8)
        pygame.draw.rect(self.canvas, COLORS["gold"], panel, 2, border_radius=8)
        draw_text(self.canvas, self.fonts["menu"], "Пауза", (640, 226), COLORS["gold"], center=True)
        if self.pending_quit:
            draw_text(self.canvas, self.fonts["body"], "Подтвердить выход?", (640, 286), COLORS["red"], center=True)
            draw_text(self.canvas, self.fonts["small"], "Атака — да, блок — нет", (640, 324), COLORS["white"], center=True)
            return
        for index, (label, _) in enumerate(self.pause_items):
            y = 298 + index * 46
            selected = index == self.pause_selected
            color = COLORS["gold"] if selected else COLORS["white"]
            if selected:
                pygame.draw.rect(self.canvas, (42, 48, 57), pygame.Rect(486, y - 18, 308, 36), border_radius=6)
                pygame.draw.line(self.canvas, COLORS["red"], (490, y + 12), (790, y + 12), 2)
            draw_text(self.canvas, self.fonts["body"], label, (640, y), color, center=True)

    def _draw_match_over(self) -> None:
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 168))
        self.canvas.blit(overlay, (0, 0))
        draw_text(self.canvas, self.fonts["title"], "Матч завершён", (640, 250), COLORS["gold"], center=True)
        draw_text(self.canvas, self.fonts["menu"], self.match_message, (640, 330), COLORS["white"], center=True)
        prompt = "Нажмите атаку, чтобы продолжить"
        draw_text(self.canvas, self.fonts["body"], prompt, (640, 404), COLORS["muted"], center=True)

    def _present(self) -> None:
        screen_size = self.screen.get_size()
        if screen_size == (VIRTUAL_WIDTH, VIRTUAL_HEIGHT):
            self.screen.blit(self.canvas, (0, 0))
        else:
            scaled = pygame.transform.smoothscale(self.canvas, screen_size)
            self.screen.blit(scaled, (0, 0))
        pygame.display.flip()


def accept_pressed_any(pressed: dict[str, bool]) -> bool:
    return any(
        pressed.get(command, False)
        for command in ("light_punch", "heavy_punch", "light_kick", "heavy_kick", "energy", "pause")
    )

