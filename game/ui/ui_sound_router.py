class UISoundRouter:
    def __init__(self,audio):self.audio=audio
    def focus(self):self.audio.play_ui()
    def confirm(self):self.audio.play_ui()
    def cancel(self):self.audio.play_ui()
