from game.combat.combo_tracker import ComboTracker
from game.combat.damage_scaling import DamageScaling
def test_scaling_table_defense_minimum_and_reset():
    assert DamageScaling.factor(1)==1 and DamageScaling.factor(2)==.95 and DamageScaling.factor(8)==.5;assert DamageScaling.factor(99,.4)>=.4;assert DamageScaling.damage(100,1,2)==50;assert DamageScaling.damage(0,1)==1
    c=ComboTracker();c.add(20,1,"a","b",1);assert c.total_damage==20;c.reset();assert c.hit_count==0
