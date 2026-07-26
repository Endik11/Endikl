from enum import Enum, auto

class FighterState(Enum):
    IDLE=auto(); WALK_FORWARD=auto(); WALK_BACKWARD=auto(); DASH_FORWARD=auto(); DASH_BACKWARD=auto(); CROUCH=auto(); JUMP_START=auto(); AIRBORNE=auto(); LANDING=auto(); ATTACK_STARTUP=auto(); ATTACK_ACTIVE=auto(); ATTACK_RECOVERY=auto(); BLOCK_HIGH=auto(); BLOCK_LOW=auto(); BLOCK_STUN=auto(); HIT_STUN=auto(); LAUNCHED=auto(); KNOCKDOWN=auto(); WAKE_UP=auto(); THROW_STARTUP=auto(); THROWING=auto(); THROWN=auto(); PROJECTILE_CAST=auto(); SUPER=auto(); VICTORY=auto(); DEFEAT=auto(); DEAD=auto()
class AttackLevel(Enum): HIGH=auto(); MID=auto(); LOW=auto(); OVERHEAD=auto(); THROW=auto(); UNBLOCKABLE=auto()
class HitResult(Enum): MISS=auto(); HIT=auto(); BLOCKED=auto(); ARMOR=auto(); INVULNERABLE=auto(); THROW_TECH=auto(); CLASH=auto()
class DamageSourceType(Enum): STRIKE=auto(); PROJECTILE=auto(); THROW=auto(); SUPER=auto(); ENVIRONMENT=auto()
class CombatEventType(Enum): ATTACK_STARTED=auto(); ATTACK_HIT=auto(); ATTACK_BLOCKED=auto(); COMBO_STARTED=auto(); COMBO_ENDED=auto(); THROW_STARTED=auto(); THROW_CONNECTED=auto(); THROW_TECHED=auto(); THROW_WHIFFED=auto(); THROW_DAMAGE_APPLIED=auto(); PROJECTILE_CREATED=auto(); PROJECTILE_HIT=auto(); PROJECTILE_BLOCKED=auto(); PROJECTILE_DESTROYED=auto(); PROJECTILE_CLASH=auto(); ARMOR_ABSORBED=auto(); INVULNERABLE=auto(); ROUND_ENDED=auto(); ROUND_DRAW=auto(); ROUND_DOUBLE_KO=auto()
class AttackPhase(Enum): STARTUP=auto(); ACTIVE=auto(); RECOVERY=auto(); COMPLETE=auto()

def parse_fighter_state(value):
    if isinstance(value, FighterState): return value
    if isinstance(value, str):
        aliases={"idle":FighterState.IDLE,"walk":FighterState.WALK_FORWARD,"jump":FighterState.AIRBORNE,"attack":FighterState.ATTACK_ACTIVE,"hit":FighterState.HIT_STUN,"block":FighterState.BLOCK_HIGH,"crouch":FighterState.CROUCH,"down":FighterState.KNOCKDOWN}
        if value.lower() in aliases: return aliases[value.lower()]
        try: return FighterState[value.upper()]
        except KeyError as exc: raise ValueError(f"Unknown fighter state: {value}") from exc
    raise TypeError("fighter state must be FighterState or str")
