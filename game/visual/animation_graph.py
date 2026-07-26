from __future__ import annotations

from ..definitions import FighterVisualDefinition


class AnimationGraph:
    STATE_CLIPS = {
        "IDLE": "idle_clip",
        "WALK_FORWARD": "walk_clip",
        "WALK_BACKWARD": "walk_clip",
        "CROUCH": "idle_clip",
        "AIRBORNE": "idle_clip",
        "BLOCK_HIGH": "idle_clip",
        "BLOCK_LOW": "idle_clip",
        "BLOCK_STUN": "idle_clip",
        "HIT_STUN": "defeat_clip",
        "KNOCKDOWN": "defeat_clip",
        "VICTORY": "victory_clip",
        "DEFEAT": "defeat_clip",
        "DEAD": "defeat_clip",
    }

    def clip_for_snapshot(self, visual: FighterVisualDefinition, snapshot) -> str:
        if getattr(snapshot, "attack_id", ""):
            return visual.attack_clip
        field = self.STATE_CLIPS.get(getattr(snapshot, "state", "IDLE"), "idle_clip")
        return getattr(visual, field)
