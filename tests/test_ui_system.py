import pygame
from game.ui import Widget,FocusManager,NavigationManager,Modal,ToastManager,UITheme
from game.ui.scroll_view import ScrollView
from game.ui.notification import Notification

def widgets():return [Widget("a",pygame.Rect(0,0,20,20),"A"),Widget("off",pygame.Rect(0,30,20,20),"Off",enabled=False),Widget("b",pygame.Rect(0,60,20,20),"B")]
def test_focus_skips_disabled_restores_and_survives_resize():
    focus=FocusManager("screen");items=widgets();focus.set_widgets(items);assert focus.current_id=="a";focus.move(1);assert focus.current_id=="b";items[1].rect.width=100;focus.set_widgets(items);assert focus.current_id=="b"
def test_modal_traps_focus_and_navigation_activates():
    focus=FocusManager();focus.set_widgets(widgets());modal=Modal("m",[Widget("yes",pygame.Rect(0,0,2,2),"Yes")]);modal.show(focus);assert NavigationManager(focus).update({"confirm":True})=="yes";modal.close(focus);assert focus.current_id=="a"
def test_mouse_scroll_toast_and_accessibility():
    focus=FocusManager();focus.set_widgets(widgets());assert focus.point((1,61))=="b";assert ScrollView(1000,200).scroll(999)==800
    toast=ToastManager(2);toast.push(Notification("a","toast.a"));assert toast.update(.1).id=="a"
    settings=type("S",(),{"high_contrast":True,"large_text":True,"reduced_motion":True})();theme=UITheme.accessible(settings);assert theme.background==(0,0,0) and theme.text_scale>1 and theme.transition_seconds==0
