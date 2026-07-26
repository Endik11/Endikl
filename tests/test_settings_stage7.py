from game.settings import SettingsManager
from game.display_settings import DisplaySettingsSession

class Display:
    def __init__(self,fail=False):self.fail=fail;self.calls=0
    def apply_settings(self):
        self.calls+=1
        if self.fail and self.calls==1:raise RuntimeError
def test_extended_settings_validate_and_migrate(tmp_path):
    path=tmp_path/"settings.json";path.write_text('{"gameplay":{"language":"xx"},"accessibility":{"large_text":true,"screen_shake_strength":9},"video":{"render_scale":0.1},"audio":{"announcer_volume":2}}',encoding="utf-8");settings=SettingsManager(path).load();assert settings.version==2 and settings.gameplay.language=="ru" and settings.accessibility.large_text and settings.accessibility.screen_shake_strength==1 and settings.video.render_scale==.5 and settings.audio.announcer_volume==1
def test_display_confirmation_timeout_and_failure_fallback():
    manager=SettingsManager();settings=manager.settings;display=Display();session=DisplaySettingsSession(display,settings,1);assert session.apply_temporary(1920,1080,"fullscreen");session.update(2);assert settings.video.width==1280 and not settings.video.fullscreen
    failing=Display(True);session=DisplaySettingsSession(failing,settings);assert not session.apply_temporary(9999,9999,"fullscreen") and settings.video.width==1280 and failing.calls==2
