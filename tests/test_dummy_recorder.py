from game.training.dummy_recorder import DummyRecorder
from game.combat.input_buffer import InputFrame


def test_record_play_loop_delay_and_relative_facing():
    recorder=DummyRecorder(2);recorder.start();recorder.record(InputFrame(right=True,held=frozenset({"right"})),1);recorder.stop();recorder.play(10,loop=True,delay=2)
    assert not recorder.build_input(11,-1).held
    played=recorder.build_input(12,-1);assert played.left and not played.right
    assert recorder.build_input(13,-1).left
