class FocusManager:
    _remembered={}
    def __init__(self,screen_id="default"):self.screen_id=screen_id;self.widgets=[];self.current_id=self._remembered.get(screen_id);self.modal_widgets=None
    def set_widgets(self,widgets):self.widgets=list(widgets);self._repair()
    def open_modal(self,widgets):self.modal_widgets=list(widgets);self.current_id=None;self._repair()
    def close_modal(self):self.modal_widgets=None;self.current_id=self._remembered.get(self.screen_id);self._repair()
    def _active(self):return self.modal_widgets if self.modal_widgets is not None else self.widgets
    def _repair(self):
        focusable=[w for w in self._active() if w.focusable]
        if not any(w.id==self.current_id for w in focusable):self.current_id=focusable[0].id if focusable else None
        self._select()
    def _select(self):
        for w in self.widgets:w.selected=w.id==self.current_id
        for w in self.modal_widgets or ():w.selected=w.id==self.current_id
        if self.modal_widgets is None and self.current_id:self._remembered[self.screen_id]=self.current_id
    def move(self,delta):
        items=[w for w in self._active() if w.focusable]
        if not items:self.current_id=None;return None
        index=next((i for i,w in enumerate(items) if w.id==self.current_id),0);self.current_id=items[(index+delta)%len(items)].id;self._select();return self.current_id
    def point(self,pos):
        target=next((w for w in self._active() if w.focusable and w.contains(pos)),None)
        if target:self.current_id=target.id;self._select()
        return self.current_id
    def focused(self):return next((w for w in self._active() if w.id==self.current_id),None)
