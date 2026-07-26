import pytest
from game.combat.constants import FIXED_DT,MAX_FRAME_SKIP
from game.combat.simulation_clock import SimulationClock
def test_sixty_steps_per_second():
    c=SimulationClock();assert sum(c.consume(FIXED_DT) for _ in range(60))==60
@pytest.mark.parametrize("fps",[30,60,120,144])
def test_render_rates_produce_same_steps(fps):
    c=SimulationClock();assert sum(c.consume(1/fps) for _ in range(fps)) in (59,60)
def test_frame_skip_and_alpha_are_bounded():
    c=SimulationClock();assert c.consume(10)==MAX_FRAME_SKIP;assert 0<=c.alpha<=1
