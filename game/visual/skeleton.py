from __future__ import annotations

import math
from dataclasses import dataclass

from ..definitions import RigDefinition
from .bone import BoneTransform
from .pose import Pose


@dataclass(slots=True)
class Skeleton:
    rig: RigDefinition

    def world_transforms(self, pose: Pose, origin: tuple[float, float], facing: int = 1, scale: float = 1.0) -> dict[str, BoneTransform]:
        by_id = {bone.id: bone for bone in self.rig.bones}
        transforms: dict[str, BoneTransform] = {}
        pending = list(self.rig.bones)
        while pending:
            progressed = False
            for bone in pending[:]:
                if bone.parent and bone.parent not in transforms:
                    continue
                local = pose.bone(bone.id)
                parent = transforms.get(bone.parent)
                base_x = bone.local_position[0] + local.translation[0]
                base_y = bone.local_position[1] + local.translation[1]
                if facing < 0:
                    base_x = -base_x
                rotation = bone.rotation + local.rotation
                if parent:
                    radians = math.radians(parent.rotation)
                    x = parent.x + (base_x * math.cos(radians) - base_y * math.sin(radians)) * scale
                    y = parent.y + (base_x * math.sin(radians) + base_y * math.cos(radians)) * scale
                    rotation += parent.rotation
                else:
                    x = origin[0] + base_x * scale
                    y = origin[1] + base_y * scale
                transforms[bone.id] = BoneTransform(
                    bone.id,
                    x,
                    y,
                    rotation * facing,
                    (bone.scale[0] * local.scale[0] * scale, bone.scale[1] * local.scale[1] * scale),
                    bone.length * scale,
                    bone.thickness * scale,
                    bone.shape,
                    bone.palette_role,
                    bone.draw_order,
                    local.alpha,
                )
                pending.remove(bone)
                progressed = True
            if not progressed:
                missing = ", ".join(bone.id for bone in pending)
                raise ValueError(f"Rig contains an unresolved hierarchy: {missing}; known={sorted(by_id)}")
        return transforms
