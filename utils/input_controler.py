import time
import flet as ft

class InputSequenceMonitor:
    def __init__(self, page):
        self.page = page
        self.last_press_time = 0
        self.press_count = 0
        self.sequence_timeout = 0.5 
        self.observers = []
    
    def register_observer(self, callback):
        self.observers.append(callback)
    
    def handle_key_event(self, e):
        if e.key == "Tab":
            current_time = time.time()
            time_diff = current_time - self.last_press_time
            if time_diff < self.sequence_timeout:
                self.press_count += 1
            else:
                self.press_count = 1
            
            self.last_press_time = current_time
            
            if self.press_count == 2:
                self._notify_observers()
                self.press_count = 0 
    
    def _notify_observers(self):
        for callback in self.observers:
            try:
                callback()
            except Exception:
                pass 