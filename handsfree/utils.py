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
    text = text or ""
    if not text.strip():
        return

    if IS_LINUX:
        # Attempt xdotool
        try:
            logger.debug(f"Using xdotool to type text (length={len(text)}).")
            subprocess.run(["xdotool", "type", "--clearmodifiers", text], check=True)
        except FileNotFoundError:
            logger.warning("xdotool not found! Falling back to pyautogui.")
            pyautogui.typewrite(text)
        except subprocess.CalledProcessError as e:
            logger.warning(f"xdotool error: {e}")
    else:
        logger.debug(f"Using pyautogui to type text (length={len(text)}).")
        pyautogui.typewrite(text)
