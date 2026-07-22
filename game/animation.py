from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnimationClip:
    name: str
    frames: int
    fps: float
    loop: bool = True

    @property
    def duration(self) -> float:
        return self.frames / self.fps if self.fps > 0 else 0.0


DEFAULT_CLIPS = {
    "idle": AnimationClip("idle", frames=8, fps=8),
    "walk": AnimationClip("walk", frames=8, fps=12),
    "jump": AnimationClip("jump", frames=4, fps=10, loop=False),
    "crouch": AnimationClip("crouch", frames=2, fps=8, loop=False),
    "block": AnimationClip("block", frames=3, fps=10, loop=True),
    "attack": AnimationClip("attack", frames=5, fps=16, loop=False),
    "hit": AnimationClip("hit", frames=4, fps=12, loop=False),
    "down": AnimationClip("down", frames=4, fps=8, loop=False),
    "victory": AnimationClip("victory", frames=6, fps=8, loop=True),
}


class Animator:
    def __init__(self) -> None:
        self.clip = DEFAULT_CLIPS["idle"]
        self.time = 0.0
        self.frame = 0

    def play(self, name: str) -> None:
        next_clip = DEFAULT_CLIPS.get(name, DEFAULT_CLIPS["idle"])
        if next_clip.name != self.clip.name:
            self.clip = next_clip
            self.time = 0.0
            self.frame = 0

    def update(self, dt: float) -> None:
        if self.clip.frames <= 1:
            self.frame = 0
            return
        self.time += dt
        raw = int(self.time * self.clip.fps)
        if self.clip.loop:
            self.frame = raw % self.clip.frames
        else:
            self.frame = min(self.clip.frames - 1, raw)

    @property
    def phase(self) -> float:
        if self.clip.frames <= 1:
            return 0.0
        return self.frame / max(1, self.clip.frames - 1)

