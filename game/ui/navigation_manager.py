class NavigationManager:
    def __init__(self,focus):self.focus=focus
    def update(self,actions):
        if actions.get("navigate_down") or actions.get("navigate_right") or actions.get("tab"):return self.focus.move(1)
        if actions.get("navigate_up") or actions.get("navigate_left") or actions.get("shift_tab"):return self.focus.move(-1)
        if actions.get("confirm"):
            item=self.focus.focused();return item.id if item and item.activate() else None
        return None
