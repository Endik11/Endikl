from game.controls import *
from game.controls.conflict_detector import ConflictDetector
from game.controls.controls_manager import default_profile,ControlsManager
from game.controls.device_manager import DeviceManager
from game.controls.gamepad_manager import GamepadManager

def test_rebinding_detects_conflict_replaces_or_cancels():
    profile=default_profile();action=ControlAction.LIGHT_PUNCH;existing=profile.bindings[ControlAction.HEAVY_PUNCH];session=RebindingSession(profile);session.begin(action);assert not session.capture(existing);assert not session.apply();assert session.apply(True);assert profile.bindings[action]==existing
def test_profile_rejects_missing_required_and_corrupt_file(tmp_path):
    profile=ControlProfile("p1",{});
    try:profile.validate()
    except ValueError:pass
    else:assert False
    path=tmp_path/"controls.json";path.write_text("bad",encoding="utf-8");assert ControlsManager(path).load()["p1"].validate()
def test_axis_rumble_and_disconnect_are_safe():
    pads=GamepadManager(.4);assert pads.axis(.2)==0 and pads.axis(-.8)==-1
    assert not pads.rumble(object());devices=DeviceManager();devices.assign("p1","pad");devices.connected_device("pad");assert devices.disconnected_device("pad")==["p1"]
