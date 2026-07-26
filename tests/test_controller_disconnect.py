from game.controls.device_manager import DeviceManager
def test_disconnect_reports_affected_player_without_ending_match():
    devices=DeviceManager();devices.assign("p1","pad-1");devices.connected_device("pad-1");affected=devices.disconnected_device("pad-1");assert affected==["p1"] and devices.assignments["p1"]=="pad-1"
