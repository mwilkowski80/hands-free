# handsfree/__main__.py
import logging
import threading
import sys
import time
import re  # <-- nowy import do obsługi zamiany białych znaków

from .config import load_config
from .hotkey import GlobalHotkeyListener
from .recorder import Recorder
from .transcriber import transcribe_audio
from . import utils
from .gui import HandsfreeGUI

def main():
    config = load_config()

    logging.basicConfig(
        level=config["LOG_LEVEL"],
        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s"
    )
    logger = logging.getLogger("handsfree")
    logger.info("Starting handsfree application...")

    recorder = Recorder(max_seconds=config["MAX_RECORD_SECONDS"])
    recorder.save_recordings = config["SAVE_RECORDINGS"]

    is_recording = False
    gui = HandsfreeGUI()
    gui.set_status("IDLE")

    def on_hotkey_triggered():
        nonlocal is_recording

        if not is_recording:
            logger.debug("Hotkey pressed -> START recording.")
            utils.play_sound(config["SOUND_START"])
            recorder.start_recording()
            is_recording = True
            gui.set_status("RECORDING")
        else:
            logger.debug("Hotkey pressed -> STOP recording.")
            audio_data = recorder.stop_recording()
            utils.play_sound(config["SOUND_STOP"])
            is_recording = False
            gui.set_status("PROCESSING")

            def worker():
                transcription = transcribe_audio(
                    audio_data,
                    config["WHISPER_URL"],
                    config["API_KEY"],
                    model=config["MODEL"],
                    language=config["LANGUAGE"]
                )

                # 1. Najpierw strip() - usuwa białe znaki z początku i końca
                transcription = transcription.strip()

                # 2. Jeśli flaga w configu włączona – zamieniamy WSZYSTKIE białe znaki na pojedynczą spację
                if config["REPLACE_ALL_WHITESPACE_WITH_SPACE"]:
                    transcription = re.sub(r"\s+", " ", transcription)

                logger.debug(f"Final transcription after transformations: '{transcription}'")

                # (opcjonalne) opóźnienie przed wpisaniem (TYPE_START_DELAY), jeśli używasz
                delay = config["TYPE_START_DELAY"]
                if delay > 0:
                    logger.debug(f"Sleeping {delay}s before typing text.")
                    time.sleep(delay)

                # 3. Wpisanie tekstu (na Linuksie xdotool, na innych pyautogui)
                utils.type_text(transcription)

                gui.set_status("IDLE")

            threading.Thread(target=worker, daemon=True).start()

    listener = GlobalHotkeyListener(
        shortcut=config["KEYBOARD_SHORTCUT"],
        on_activate=on_hotkey_triggered
    )
    hotkey_thread = threading.Thread(target=listener.start, daemon=True)
    hotkey_thread.start()

    def on_close():
        logger.info("Exiting handsfree...")
        if is_recording:
            recorder.stop_recording()
        recorder.terminate()
        listener.stop()
        gui.close()
        sys.exit(0)

    gui.set_on_close_callback(on_close)
    gui.run()

if __name__ == "__main__":
    main()
