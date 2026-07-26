from __future__ import annotations

from .animation_clip import AnimationClip
from .pose import Pose


class AnimationPlayer:
    def __init__(self, clips: dict[str, AnimationClip], default_clip: str = "idle") -> None:
        self.clips = clips
        self.current_clip = default_clip if default_clip in clips else next(iter(clips))
        self.frame = 0.0
        self.speed_scale = 1.0

    def play(self, clip_id: str, *, restart: bool | None = None) -> None:
        if clip_id not in self.clips:
            return
        definition = self.clips[clip_id].definition
        should_restart = definition.restart if restart is None else restart
        if clip_id != self.current_clip or should_restart:
            self.current_clip = clip_id
            self.frame = 0.0

    def update(self, frames: float = 1.0, *, hit_stop: bool = False) -> None:
        clip = self.clips[self.current_clip]
        if hit_stop and clip.definition.freeze_on_hit_stop:
            return
        self.frame += frames * clip.definition.playback_speed * self.speed_scale

    def sample(self, *, facing: int = 1) -> Pose:
        return self.clips[self.current_clip].sample(self.frame, facing=facing)
