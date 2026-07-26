from .enums import AttackLevel
class BlockSystem:
    @staticmethod
    def is_blocking(defender,attacker_x,level,input_frame):
        if level in {AttackLevel.THROW,AttackLevel.UNBLOCKABLE}:return False
        back=input_frame.left if attacker_x>defender.x else input_frame.right
        if not back or not input_frame.block:return False
        if level is AttackLevel.HIGH:return not defender.crouching
        if level is AttackLevel.LOW:return defender.crouching
        if level is AttackLevel.OVERHEAD:return not defender.crouching
        return True
    @staticmethod
    def chip_health(health,chip,can_kill=False):return max(0 if can_kill else 1,health-chip)
