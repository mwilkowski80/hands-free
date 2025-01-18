# handsfree/utils.py
import pyautogui
import logging
import playsound
import threading
import platform
import subprocess

logger = logging.getLogger(__name__)

IS_LINUX = (platform.system().lower() == "linux")

def play_sound(sound_path):
    def worker():
        try:
            playsound.playsound(sound_path, block=True)
        except Exception as e:
            logger.warning(f"Unable to play sound {sound_path}: {e}")

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return t

def type_text(text):
    """
    Wprowadza tekst do aktywnego okna.
    - Na Linuxie próbuje xdotool (lepiej radzi sobie z polskimi znakami).
    - Na pozostałych systemach (Windows/macOS) używa pyautogui.
    
    UWAGA: Zakładamy, że xdotool jest zainstalowany na Linuxie.
          Jeśli nie jest, można dodać fallback do pyautogui
          albo wyświetlić komunikat o błędzie.
    """
    text = text or ""  # zabezpieczenie przed None
    if not text.strip():
        return  # nic nie wpisujemy, jeśli pusto/whitespace

    if IS_LINUX:
        # Próbujemy xdotool
        try:
            logger.debug(f"Using xdotool to type text (length={len(text)} chars).")
            # Używamy --clearmodifiers, by uniknąć wciśniętych Ctrl/Alt
            # i "type" do wpisania całego stringa naraz
            subprocess.run(["xdotool", "type", "--clearmodifiers", text], check=True)
        except FileNotFoundError:
            # Jeśli xdotool nie jest dostępny, fallback do pyautogui
            logger.warning("xdotool not found! Falling back to pyautogui.")
            pyautogui.typewrite(text)
        except subprocess.CalledProcessError as e:
            logger.warning(f"xdotool returned error: {e}")
    else:
        # Na Windows/macOS - pyautogui wystarczy
        logger.debug(f"Using pyautogui to type text (length={len(text)} chars).")
        pyautogui.typewrite(text)
