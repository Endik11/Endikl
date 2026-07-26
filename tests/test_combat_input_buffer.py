from game.combat.command_parser import CommandParser
from game.combat.input_buffer import InputBuffer,InputFrame
def test_directions_buttons_and_consumption():
    b=InputBuffer();b.push(InputFrame(down=True,frame_number=1));b.push(InputFrame(down=True,right=True,frame_number=2));b.push(InputFrame(right=True,light_punch=True,pressed=frozenset({"light_punch"}),frame_number=3));cmd={"id":"qcf","inputs":[{"direction":"down"},{"direction":"down_forward"},{"direction":"forward"},{"button":"light_punch"}]}
    assert CommandParser().match(b,cmd,1);assert not CommandParser().match(b,cmd,1)
    assert InputFrame(left=True).direction(1)==4 and InputFrame(left=True).direction(-1)==6
def test_pressed_released_held_survive_buffer():
    f=InputFrame(pressed=frozenset({"throw"}),released=frozenset({"block"}),held=frozenset({"throw"}),frame_number=4);b=InputBuffer(14);b.push(f);assert b.frames[-1]==f

def test_hold_release_charge_and_simultaneous_inputs():
    parser=CommandParser();b=InputBuffer()
    for n in range(3):b.push(InputFrame(left=True,held=frozenset({"block"}),block=True,frame_number=n))
    b.push(InputFrame(right=True,frame_number=3));b.push(InputFrame(heavy_punch=True,heavy_kick=True,pressed=frozenset({"heavy_punch","heavy_kick"}),frame_number=4))
    command={"id":"charge","inputs":[{"direction":"back","hold_frames":3},{"direction":"forward"},{"buttons":["heavy_punch","heavy_kick"]}],"tolerance":0}
    assert parser.match(b,command,1)
    release=InputBuffer();release.push(InputFrame(block=True,held=frozenset({"block"}),frame_number=1));release.push(InputFrame(released=frozenset({"block"}),frame_number=2))
    assert parser.match(release,{"id":"release","inputs":[{"button":"block","release":True}]})
    assert not parser.match(InputBuffer(frames=[InputFrame(released=frozenset({"block"}))]),{"id":"bad-release","inputs":[{"button":"block","release":True}]})

def test_hold_is_rejected_when_too_short_and_direction_button_can_share_frame():
    parser=CommandParser();b=InputBuffer();b.push(InputFrame(left=True,frame_number=1));b.push(InputFrame(left=True,frame_number=2))
    assert not parser.match(b,{"id":"hold","inputs":[{"direction":"back","hold_frames":3}]})
    same=InputBuffer();same.push(InputFrame(down=True,right=True,light_punch=True,pressed=frozenset({"light_punch"}),frame_number=1))
    assert parser.match(same,{"id":"same","inputs":[{"direction":"down_forward","button":"light_punch"}]})

def test_consumed_command_frames_cannot_trigger_a_different_command():
    b=InputBuffer();b.push(InputFrame(right=True,light_punch=True,pressed=frozenset({"light_punch"}),frame_number=10));parser=CommandParser()
    assert parser.match(b,{"id":"special","inputs":[{"direction":"forward","button":"light_punch"}]})
    assert not parser.match(b,{"id":"normal","inputs":[{"button":"light_punch"}]})

def test_command_conflict_uses_priority_then_affordable_meter():
    from types import SimpleNamespace
    from game.combat.fighter_controller import FighterController
    def combo(i,priority,cost):return SimpleNamespace(id=i,enabled=True,owner_id="common",meter_cost=cost,priority=priority,inputs=("light_punch",),resulting_attack_id=i,max_gap_frames=10)
    registry=SimpleNamespace(combos={"normal":combo("normal",0,0),"special":combo("special",10,100)})
    def fighter(meter):
        buffer=InputBuffer();buffer.push(InputFrame(light_punch=True,pressed=frozenset({"light_punch"}),frame_number=1));return SimpleNamespace(fighter_id="kael",meter=meter,facing=1,input_buffer=buffer)
    assert FighterController(registry)._matched_combo(fighter(100)).id=="special"
    assert FighterController(registry)._matched_combo(fighter(50)).id=="normal"
