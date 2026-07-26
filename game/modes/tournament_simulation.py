from __future__ import annotations
from ..ai import AIController,AIProfile
from ..combat.combat_world import CombatWorld


def simulate_ai_match(registry,fighter_one,fighter_two,arena_id,seed,max_frames=20000):
    world=CombatWorld(registry,fighter_one,fighter_two,arena_id,seed,30,1)
    controllers=[]
    for index,fighter_id in enumerate((fighter_one,fighter_two)):
        definition=registry.get_fighter(fighter_id);controller=AIController(AIProfile.from_dict(fighter_id,definition.ai_profile),"medium",definition.attack_ids);controller.reset(seed+index);controllers.append(controller)
    for _ in range(max_frames):
        snapshot=world.snapshot();world.simulate_frame(controllers[0].build_input(snapshot,fighter_one,world.frame_number),controllers[1].build_input(snapshot,fighter_two,world.frame_number))
        if world.round_controller.result:return world.round_controller.result,world.snapshot().digest()
    winner=fighter_one if world.fighter_one.health>=world.fighter_two.health else fighter_two
    return winner,world.snapshot().digest()
