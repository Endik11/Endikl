from game.combat.hitbox import Hitbox,intersects
from game.combat.pushbox import Pushbox
def test_intersection_miss_flip_and_pushbox():
    h=Hitbox(10,-20,30,20);assert intersects(h.rect(100,100,1),(110,80,40,40));assert not intersects(h.rect(100,100,1),(500,500,2,2));assert h.rect(100,100,-1)[0]==60;assert Pushbox().rect(100,584)[2:]==(90,218)
