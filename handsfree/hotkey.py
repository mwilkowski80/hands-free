# handsfree/hotkey.py
import logging
from pynput import keyboard

logger = logging.getLogger(__name__)

# Mapowanie stringów na obiekty `pynput.keyboard.Key`
SPECIAL_KEYS = {
    "alt": keyboard.Key.alt,
    "ctrl": keyboard.Key.ctrl,
    "shift": keyboard.Key.shift,
    "cmd": keyboard.Key.cmd,
    "windows": keyboard.Key.cmd,  # alias
    "win": keyboard.Key.cmd,      # alias
    "super": keyboard.Key.cmd,    # alias
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
    """
    Zwraca set lub listę obiektów Key/KeyCode odpowiadających
    ciągowi np. "ctrl+alt+f5".
    """
    parts = shortcut_str.lower().split("+")
    keys = []
    for part in parts:
        part = part.strip()
        if part in SPECIAL_KEYS:
            keys.append(SPECIAL_KEYS[part])
        else:
            # Zakładamy, że to zwykły klawisz (np. 'a', 'b', '5') 
            # Używamy KeyCode do liter/cyfr
            if len(part) == 1:
                keys.append(keyboard.KeyCode.from_char(part))
            else:
                # np. "f5" => Key.f5 w SPECIAL_KEYS, 
                # ale jeśli nie ma tam, to fallback
                # może user podał "ctrl+alt+g" => 'g'
                keys.append(keyboard.KeyCode.from_char(part))
    return frozenset(keys)

class GlobalHotkeyListener:
    """
    Nasłuchuje jednej kombinacji klawiszy (globalnie) i
    wywołuje callback on_activate() po jej wciśnięciu.
    """
    def __init__(self, shortcut, on_activate):
        self.on_activate = on_activate
        # Parsujemy shortcut do zestawu klawiszy
        combo = parse_shortcut(shortcut)

        # Inicjalizujemy obiekt HotKey z pynput
        self.hotkey = keyboard.HotKey(
            combo,
            self._on_hotkey_triggered
        )
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )

    def start(self):
        """
        Startuje nasłuchiwanie. To metoda blokująca,
        dopóki nie przerwiemy listenera (stop).
        """
        logger.debug("Starting global hotkey listener...")
        self.listener.start()
        self.listener.join()

    def stop(self):
        logger.debug("Stopping global hotkey listener...")
        self.listener.stop()

    def on_press(self, key):
        # forward do hotkey.press
        self.hotkey.press(key)

    def on_release(self, key):
        # forward do hotkey.release
        self.hotkey.release(key)

    def _on_hotkey_triggered(self):
        """
        Wywoływane automatycznie przez pynput przy rozpoznaniu skrótu.
        """
        logger.debug("Global hotkey triggered.")
        if self.on_activate:
            self.on_activate()
