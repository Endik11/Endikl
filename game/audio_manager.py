from __future__ import annotations

import math
from array import array
from pathlib import Path

import pygame

from .debug import log_warning


class ToneBank:
    """Generated fallback sounds retained for backward compatibility."""

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
        except pygame.error as exc:
            log_warning("Audio device unavailable; generated tones disabled: %s", exc)

    def _tone(self, frequency: float, seconds: float, volume: float) -> pygame.mixer.Sound:
        sample_rate = 44100
        count = int(sample_rate * seconds)
        samples = array("h")
        for index in range(count):
            envelope = 1.0 - index / max(1, count)
            value = int(
                math.sin(index * math.tau * frequency / sample_rate)
                * 24000
                * volume
                * envelope
            )
            samples.append(value)
        return pygame.mixer.Sound(buffer=samples)

    def play(self, name: str) -> None:
        if self.enabled and name in self.sounds:
            self.sounds[name].play()


class AudioManager:
    def __init__(self, settings) -> None:
        self.settings = settings
        audio = settings.audio
        self.master_volume = audio.master_volume
        self.music_volume = audio.music_volume
        self.sfx_volume = audio.sfx_volume
        self.ui_volume = audio.interface_volume
        self.muted = audio.mute
        effective_sfx = 0.0 if self.muted else self.master_volume * self.sfx_volume
        self.tones = ToneBank(effective_sfx)
        self._warned: set[str] = set()

    def play(self, name: str) -> None:
        self.play_sfx(name)

    def play_ui(self, name: str = "select") -> None:
        if not self.muted:
            self.tones.play(name)

    def play_sfx(self, name: str) -> None:
        if not self.muted:
            self.tones.play(name)

    def play_music(self, path: str | Path, loops: int = -1) -> bool:
        music_path = Path(path)
        if self.muted:
            return False
        if not music_path.is_file():
            self._warn_once(f"missing:{music_path}", f"Music file is missing: {music_path}")
            return False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.master_volume * self.music_volume)
            pygame.mixer.music.play(loops)
        except (OSError, pygame.error) as exc:
            self._warn_once(
                f"unreadable:{music_path}",
                f"Unable to play music {music_path}: {exc}",
            )
            return False
        return True

    def stop_music(self) -> None:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def shutdown(self) -> None:
        self.stop_music()

    def _warn_once(self, key: str, message: str) -> None:
        if key not in self._warned:
            self._warned.add(key)
            log_warning(message)

