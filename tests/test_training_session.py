from game.content_registry import get_default_registry
from game.combat.combat_world import CombatWorld
from game.modes.training_session import TrainingSession
from game.training import TrainingDummyController,TrainingSettings
from game.training.training_reset import reset_training_world


def test_reset_health_meter_projectiles_combo_and_side():
    world=CombatWorld(get_default_registry(),"kael","sable","neon_foundry");world.fighter_one.health=3;world.fighter_one.meter=0;world.projectiles.append(object());world.fighter_one.combo_tracker.hit_count=3
    reset_training_world(world,TrainingSettings(),True)
    assert not world.projectiles and world.fighter_one.health==world.fighter_one.max_health and world.fighter_one.meter==1000 and world.fighter_one.x==930 and world.fighter_one.combo_tracker.hit_count==0


def test_dummy_controller_only_returns_input_and_session_restores():
    world=CombatWorld(get_default_registry(),"kael","sable","neon_foundry");before=world.snapshot().digest();controller=TrainingDummyController("block_low")
    frame=controller.build_input(world.snapshot(),"sable",0);assert frame.block and frame.down and world.snapshot().digest()==before
    session=TrainingSession("kael","sable","neon_foundry");session.tick();assert TrainingSession.from_dict(session.to_dict()).frames==1
