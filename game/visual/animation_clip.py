from __future__ import annotations

from collections import defaultdict

from ..definitions import AnimationDefinition, AnimationKeyframeDefinition
from .pose import BonePose, Pose


class AnimationClip:
    def __init__(self, definition: AnimationDefinition) -> None:
        self.definition = definition
        self._by_bone: dict[str, list[AnimationKeyframeDefinition]] = defaultdict(list)
        for keyframe in definition.keyframes:
            self._by_bone[keyframe.bone_id].append(keyframe)

    @property
    def duration(self) -> int:
        return self.definition.duration_frames

    def sample(self, frame: float, *, facing: int = 1) -> Pose:
        duration = max(1, self.definition.duration_frames)
        if self.definition.loop:
            frame = frame % duration
        else:
            frame = min(frame, duration - 1)
        poses = {}
        for bone_id, rows in self._by_bone.items():
            rows = sorted(rows, key=lambda row: row.frame)
            previous = rows[0]
            following = rows[-1]
            for index, row in enumerate(rows):
                if row.frame <= frame:
                    previous = row
                if row.frame >= frame:
                    following = row
                    break
                if index == len(rows) - 1:
                    following = row
            span = max(1, following.frame - previous.frame)
            amount = 0.0 if following is previous else (frame - previous.frame) / span
            pose = _pose_from_keyframe(previous).blend(_pose_from_keyframe(following), amount)
            if facing < 0:
                pose = BonePose((-pose.translation[0], pose.translation[1]), -pose.rotation, pose.scale, pose.alpha)
            poses[bone_id] = pose
        return Pose(poses)


def _pose_from_keyframe(keyframe: AnimationKeyframeDefinition) -> BonePose:
    return BonePose(keyframe.translation, keyframe.rotation, keyframe.scale, keyframe.alpha)
