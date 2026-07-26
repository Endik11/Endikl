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
        state = getattr(snapshot, "state", "IDLE")
        # These authored clips are shared by every fighter and keep the
        # procedural combat rig readable while its hitboxes stay simulation-owned.
        state_clips = {
            "BLOCK_HIGH": "block_high",
            "BLOCK_LOW": "block_high",
            "BLOCK_STUN": "block_high",
            "CROUCH": "crouch",
            "AIRBORNE": "airborne",
            "JUMP_START": "airborne",
            "LAUNCHED": "airborne",
            "THROWN": visual.defeat_clip,
        }
        if state in state_clips:
            return state_clips[state]
        field = self.STATE_CLIPS.get(state, "idle_clip")
        return getattr(visual, field)
