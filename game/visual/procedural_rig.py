from __future__ import annotations

from ..definitions import RigDefinition
from .pose import Pose
from .skeleton import Skeleton


def build_skeleton(rig: RigDefinition) -> Skeleton:
    return Skeleton(rig)


def neutral_pose(rig: RigDefinition) -> Pose:
    return Pose({bone.id: Pose({}).bone(bone.id) for bone in rig.bones})
