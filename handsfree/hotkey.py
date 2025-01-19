# handsfree/hotkey.py
import logging
from pynput import keyboard

logger = logging.getLogger(__name__)

SPECIAL_KEYS = {
    "alt": keyboard.Key.alt,
    "ctrl": keyboard.Key.ctrl,
    "shift": keyboard.Key.shift,
    "cmd": keyboard.Key.cmd,
    "windows": keyboard.Key.cmd,
    "win": keyboard.Key.cmd,
    "super": keyboard.Key.cmd,
    "alt_gr": keyboard.Key.alt_gr,
    "esc": keyboard.Key.esc,
    "tab": keyboard.Key.tab,
    "space": keyboard.Key.space,
    "enter": keyboard.Key.enter,
    "f1": keyboard.Key.f1,
    "f2": keyboard.Key.f2,
    "f3": keyboard.Key.f3,
    "f4": keyboard.Key.f4,
    "f5": keyboard.Key.f5,
    "f6": keyboard.Key.f6,
    "f7": keyboard.Key.f7,
    "f8": keyboard.Key.f8,
    "f9": keyboard.Key.f9,
    "f10": keyboard.Key.f10,
    "f11": keyboard.Key.f11,
    "f12": keyboard.Key.f12,
    "home": keyboard.Key.home,
    "end": keyboard.Key.end,
    "page_up": keyboard.Key.page_up,
    "page_down": keyboard.Key.page_down,
}

def parse_shortcut(shortcut_str):
    parts = shortcut_str.lower().split("+")
    keys = []
    for part in parts:
        part = part.strip()
        if part in SPECIAL_KEYS:
            keys.append(SPECIAL_KEYS[part])
        else:
            if len(part) == 1:
                keys.append(keyboard.KeyCode.from_char(part))
            else:
                keys.append(keyboard.KeyCode.from_char(part))
    return frozenset(keys)

class GlobalHotkeyListener:
    def __init__(self, shortcut, on_activate):
        self.on_activate = on_activate
        combo = parse_shortcut(shortcut)
        self.hotkey = keyboard.HotKey(combo, self._on_hotkey_triggered)
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )

    def start(self):
        logger.debug("Starting global hotkey listener...")
        self.listener.start()
        self.listener.join()

    def stop(self):
        logger.debug("Stopping global hotkey listener...")
        self.listener.stop()

    def on_press(self, key):
        self.hotkey.press(key)

    def on_release(self, key):
        self.hotkey.release(key)

    def _on_hotkey_triggered(self):
        logger.debug("Global hotkey triggered.")
        if self.on_activate:
            self.on_activate()
