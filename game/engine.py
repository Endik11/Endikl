from __future__ import annotations

import pygame

from .audio_manager import AudioManager
from .combat_match_runtime import CombatMatchRuntime
from .content_registry import get_default_registry
from .debug import configure_logging, log_critical, log_event, log_runtime_info, shutdown_logging
from .display_manager import DisplayManager
from .enums import GameState, MatchMode
from .input_manager import InputManager
from .resources import inspect_optional_assets
from .save import SaveManager
from .screen_context import ScreenContext
from .screens.arena_select_screen import ArenaSelectScreen
from .screens.character_select_screen import CharacterSelectScreen
from .screens.collection_screen import CollectionScreen
from .screens.fight_screen import FightScreen
from .screens.main_menu_screen import MainMenuScreen
from .screens.pause_screen import PauseScreen
from .screens.result_screen import ResultScreen
from .screens.settings_screen import SettingsScreen
from .screens.shop_screen import ShopScreen
from .screens.stats_screen import StatsScreen
from .screens.mode_select_screen import ModeSelectScreen
from .screens.arcade_ladder_screen import ArcadeLadderScreen
from .screens.story_select_screen import StorySelectScreen
from .screens.story_screen import StoryScreen
from .screens.dialogue_screen import DialogueScreen
from .screens.tournament_screen import TournamentScreen
from .screens.tournament_bracket_screen import TournamentBracketScreen
from .screens.training_settings_screen import TrainingSettingsScreen
from .statistics_manager import StatisticsManager
from .reward_manager import RewardManager
from .match_statistics import MatchStatistics
from .progress_manager import ProgressManager
from .modes.arcade_session import ArcadeSession
from .modes.story_session import StorySession
from .modes.tournament_session import TournamentSession
from .modes.training_session import TrainingSession
from .session import GameSession
from .settings import GAME_TITLE, SettingsManager
from .state_manager import StateManager


class GameEngine:
    """Composition root; combat rules live exclusively in CombatWorld/runtime."""

    def __init__(self) -> None:
        configure_logging()
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load()
        self.content = get_default_registry()
        self.save_manager = SaveManager(
            fighter_keys=set(self.content.fighters),
            arena_keys=set(self.content.arenas),
        )
        self.profile = self.save_manager.load()
        self.statistics = StatisticsManager(self.profile.statistics, self.profile.processed_result_ids)
        self.rewards = RewardManager(self.profile.received_reward_ids, self.profile.processed_result_ids)
        self.progress = ProgressManager(self.profile)
        self._repair_profile_content_ids()
        self.display = DisplayManager(self.settings)
        self.screen = self.display.create_display()
        self.canvas = self.display.get_virtual_surface()
        self.clock = pygame.time.Clock()
        self.fonts = self._load_fonts()
        self.input = InputManager(self.settings)
        self.audio = AudioManager(self.settings)
        self.running = True
        self.session = GameSession()
        self.resource_report = inspect_optional_assets(
            allow_unverified_assets=self.settings.video.allow_unverified_assets,
        )
        self.state_manager = StateManager()
        self.match_runtime = CombatMatchRuntime(
            self.content,
            self.input,
            self.audio,
            self.settings,
            on_match_result=self._on_match_result,
        )
        self.screen_context = ScreenContext(
            state_manager=self.state_manager,
            settings=self.settings_manager,
            saves=self.save_manager,
            resources=self.resource_report,
            audio=self.audio,
            display=self.display,
            request_exit=self.request_exit,
            session=self.session,
            match_runtime=self.match_runtime,
            input=self.input,
            content=self.content,
            localization=self.content.localization,
        )
        self._register_screens()
        self.state_manager.request_change(GameState.MAIN_MENU, remember_current=False)
        self.state_manager.apply_pending_change()
        log_runtime_info(self.screen.get_size(), self.state.name)

    @property
    def state(self) -> GameState:
        return self.state_manager.current_state

    def request_exit(self) -> None:
        self.running = False

    def _on_match_result(self) -> None:
        result = self.session.last_match_result or {}
        result_id = result.get("result_id")
        if result_id:
            outcome = "win" if result.get("result") == "PLAYER_1" else "loss" if result.get("result") == "PLAYER_2" else "draw"
            stats = MatchStatistics.from_events(result_id, self.session.player_one_fighter or "", self.session.player_two_fighter or "", self.session.selected_arena or "", outcome, result.get("events", ()))
            self.statistics.process(stats)
            self._advance_mode_result(result_id, outcome == "win")
            self.profile.statistics = dict(self.statistics.data)
            self.profile.processed_result_ids = sorted(self.statistics.processed_result_ids | self.rewards.processed_result_ids)
            self.profile.received_reward_ids = sorted(self.rewards.received_reward_ids)
            self.save_manager.save()
        if self.state is GameState.FIGHT and not self.state_manager.has_pending_change:
            self.state_manager.request_change(GameState.RESULT)

    def _advance_mode_result(self, result_id: str, won: bool) -> None:
        mode = self.session.selected_mode
        active = self.session.mode_session
        if mode is MatchMode.ARCADE and isinstance(active, ArcadeSession):
            if active.record_result(result_id, won):
                self.progress.store_arcade(active)
                if active.completed:
                    self.rewards.grant("arcade_complete", result_id, self.profile, "currency", 500)
                    self.statistics.mode_complete("arcade")
                elif won:
                    self.session.player_two_fighter = active.current_opponent
                    self.session.match_options["difficulty"] = active.current_difficulty
        elif mode is MatchMode.TOURNAMENT and isinstance(active, TournamentSession):
            match = next((item for item in active.matches if not item.winner and self.session.player_one_fighter in {item.fighter_one, item.fighter_two}), None)
            if match is not None:
                winner = self.session.player_one_fighter if won else self.session.player_two_fighter
                active.record_result(match.id, result_id, winner)
                self.progress.store_tournament(active)
                if active.completed and active.champion == active.player_id:
                    self.rewards.grant("tournament_win", result_id, self.profile, "currency", 400)
                    self.statistics.mode_complete("tournament")
        elif mode is MatchMode.STORY and isinstance(active, StorySession):
            from pathlib import Path
            from .modes.story_runner import StoryRegistry
            stories = StoryRegistry(Path(__file__).parents[1] / "data"); stories.load(set(self.content.fighters)); story = stories.stories[active.story_id]
            if active.node(story).type == "battle" and active.record_battle(story, result_id, won):
                self.progress.store_story(active)
        elif mode is MatchMode.TRAINING and isinstance(active, TrainingSession):
            self.progress.store_training(active)

    def _repair_profile_content_ids(self) -> None:
        fighters = list(self.content.fighters)
        arenas = list(self.content.arenas)
        if self.profile.selected_fighter not in self.content.fighters:
            self.profile.selected_fighter = fighters[0]
        if self.profile.selected_arena not in self.content.arenas:
            self.profile.selected_arena = arenas[0]
        self.profile.unlocked_fighters = [x for x in self.profile.unlocked_fighters if x in self.content.fighters] or [x for x,d in self.content.fighters.items() if d.unlocked_by_default]
        self.profile.unlocked_arenas = [x for x in self.profile.unlocked_arenas if x in self.content.arenas] or [x for x,d in self.content.arenas.items() if d.unlocked_by_default]

    def _register_screens(self) -> None:
        screens = {
            GameState.MAIN_MENU: MainMenuScreen(self.screen_context),
            GameState.MODE_SELECT: ModeSelectScreen(self.screen_context),
            GameState.ARCADE_SELECT: ArcadeLadderScreen(self.screen_context),
            GameState.ARCADE_LADDER: ArcadeLadderScreen(self.screen_context),
            GameState.STORY_SELECT: StorySelectScreen(self.screen_context),
            GameState.STORY_DIALOGUE: DialogueScreen(self.screen_context),
            GameState.STORY_PROGRESS: StoryScreen(self.screen_context),
            GameState.TOURNAMENT_SETUP: TournamentScreen(self.screen_context),
            GameState.TOURNAMENT_BRACKET: TournamentBracketScreen(self.screen_context),
            GameState.TRAINING_SETUP: TrainingSettingsScreen(self.screen_context),
            GameState.TRAINING: FightScreen(self.screen_context),
            GameState.MODE_RESULT: ResultScreen(self.screen_context),
            GameState.SETTINGS: SettingsScreen(context=self.screen_context),
            GameState.CHARACTER_SELECT: CharacterSelectScreen(context=self.screen_context),
            GameState.ARENA_SELECT: ArenaSelectScreen(self.profile.selected_arena, context=self.screen_context),
            GameState.COLLECTION: CollectionScreen(context=self.screen_context),
            GameState.STATS: StatsScreen(context=self.screen_context),
            GameState.SHOP: ShopScreen(self.screen_context),
            GameState.FIGHT: FightScreen(self.screen_context),
            GameState.PAUSE: PauseScreen(self.screen_context),
            GameState.RESULT: ResultScreen(self.screen_context),
        }
        for state, screen in screens.items():
            screen.fonts = self.fonts
            self.state_manager.register(state, screen)

    def _load_fonts(self):
        return {
            "title": pygame.font.SysFont("Segoe UI", 72, bold=True),
            "subtitle": pygame.font.SysFont("Segoe UI", 42, bold=True),
            "menu": pygame.font.SysFont("Segoe UI", 32, bold=True),
            "body": pygame.font.SysFont("Segoe UI", 24),
            "small": pygame.font.SysFont("Segoe UI", 19),
            "tiny": pygame.font.SysFont("Segoe UI", 15),
        }

    def run(self) -> None:
        try:
            while self.running:
                dt = min(self.clock.tick(self.settings.video.fps_limit) / 1000.0, 0.25)
                _, _, quit_requested, events = self.input.poll()
                if quit_requested:
                    self.running = False
                for event in events:
                    if event.type == pygame.VIDEORESIZE:
                        self.display.handle_resize(event.size)
                        self.screen = self.display.screen
                        self.state_manager.current_screen.on_resize(event.size)
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_F5 and event.mod & pygame.KMOD_CTRL:
                        if self.state in {GameState.FIGHT, GameState.PAUSE, GameState.RESULT}:
                            log_event("content_reload_ignored active_state=%s", self.state.name)
                        elif self.content.reload():
                            self.state_manager.current_screen.enter({"content_reloaded": True})
                    elif event.type != pygame.QUIT:
                        self.state_manager.current_screen.handle_event(event)
                if self.running:
                    self.state_manager.current_screen.update(dt)
                    self.state_manager.apply_pending_change()
                    self.state_manager.current_screen.draw(self.canvas)
                    self.display.present()
        except Exception as exc:
            log_critical(f"Fatal game loop error state={self.state.name}", exc)
            raise
        finally:
            self.settings_manager.settings = self.settings
            self.settings_manager.save()
            self.save_manager.save()
            self.match_runtime.stop_match()
            self.audio.shutdown()
            pygame.quit()
            log_event("shutdown state=%s", self.state.name)
            shutdown_logging()
