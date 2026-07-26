from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BonePose:
    translation: tuple[float, float] = (0.0, 0.0)
    rotation: float = 0.0
    scale: tuple[float, float] = (1.0, 1.0)
    alpha: float = 1.0

    def blend(self, other: "BonePose", amount: float) -> "BonePose":
        t = max(0.0, min(1.0, amount))
        return BonePose(
            (_lerp(self.translation[0], other.translation[0], t), _lerp(self.translation[1], other.translation[1], t)),
            _lerp(self.rotation, other.rotation, t),
            (_lerp(self.scale[0], other.scale[0], t), _lerp(self.scale[1], other.scale[1], t)),
            _lerp(self.alpha, other.alpha, t),
        )


@dataclass(frozen=True, slots=True)
class Pose:
    bones: dict[str, BonePose]

    def bone(self, bone_id: str) -> BonePose:
        return self.bones.get(bone_id, BonePose())

    def blend(self, other: "Pose", amount: float) -> "Pose":
        keys = set(self.bones) | set(other.bones)
        return Pose({key: self.bone(key).blend(other.bone(key), amount) for key in keys})


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t
