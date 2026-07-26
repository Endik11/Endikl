from .modal import Modal
class ConfirmationDialog(Modal):
    def __init__(self,id,widgets,on_confirm=None,on_cancel=None):super().__init__(id,widgets,False,True);self.on_confirm=on_confirm;self.on_cancel=on_cancel
