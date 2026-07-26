from types import SimpleNamespace
from game.combat.block_system import BlockSystem
from game.combat.enums import AttackLevel
from game.combat.input_buffer import InputFrame
def defender(crouch=False,x=500):return SimpleNamespace(crouching=crouch,x=x)
def test_levels_direction_and_chip():
    back=InputFrame(right=True,block=True);assert BlockSystem.is_blocking(defender(),400,AttackLevel.HIGH,back);assert not BlockSystem.is_blocking(defender(True),400,AttackLevel.HIGH,back);assert BlockSystem.is_blocking(defender(True),400,AttackLevel.LOW,back);assert not BlockSystem.is_blocking(defender(),400,AttackLevel.LOW,back);assert not BlockSystem.is_blocking(defender(),400,AttackLevel.THROW,back);assert not BlockSystem.is_blocking(defender(),400,AttackLevel.UNBLOCKABLE,back);assert BlockSystem.chip_health(5,10)==1
