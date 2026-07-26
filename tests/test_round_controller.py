from game.combat.round_controller import RoundController
def test_ko_time_draw_double_ko_and_sudden_death():
    r=RoundController(10);assert r.evaluate(10,0)=="PLAYER_1";r=RoundController(0);assert r.evaluate(10,5)=="PLAYER_1";r=RoundController(0);assert r.evaluate(5,5)=="DRAW";r=RoundController(10);assert r.evaluate(0,0)=="DOUBLE_KO"
    r=RoundController(0,maximum_draw_retries=0);r.evaluate(5,5);assert r.sudden_death_active
