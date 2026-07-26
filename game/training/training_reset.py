from ..combat.enums import FighterState


def reset_training_world(world,settings,swap_sides=False):
    world.projectiles.clear();world.hit_stop.remaining=0
    positions=(930,350) if swap_sides else (350,930)
    for fighter,x in zip((world.fighter_one,world.fighter_two),positions):
        fighter.x=x;fighter.y=world.ground_y;fighter.active_attack=None;fighter.velocity_x=fighter.velocity_y=0;fighter.hit_stun_remaining=fighter.block_stun_remaining=fighter.knockdown_remaining=0;fighter.state=FighterState.IDLE;fighter.combo_tracker.reset();fighter.input_buffer.clear()
        if settings.health_mode=="infinite":fighter.health=fighter.max_health
        if settings.meter_mode=="infinite":fighter.meter=1000
        elif settings.meter_mode=="fixed":fighter.meter=max(0,min(1000,settings.meter_value))
