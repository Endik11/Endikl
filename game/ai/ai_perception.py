from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AIPerception:
    self_fighter: object
    opponent: object
    distance: float
    opponent_attacking: bool
    opponent_airborne: bool
    projectile_incoming: bool
    in_corner: bool
    own_state: str
    opponent_state: str
    own_meter: int


def perceive(snapshot, fighter_id: str, left_boundary: float = 80, right_boundary: float = 1200) -> AIPerception:
    own, other = snapshot.fighter_one, snapshot.fighter_two
    if own.fighter_id != fighter_id and getattr(own, "combat_id", "") != fighter_id:
        own, other = other, own
    distance = abs(other.x - own.x)
    incoming = any((item[1] != fighter_id and abs(item[2] - own.x) < 300) for item in snapshot.projectiles)
    return AIPerception(own, other, distance, bool(other.attack_id), other.y < own.y - 35, incoming, own.x < left_boundary + 90 or own.x > right_boundary - 90, own.state, other.state, own.meter)
