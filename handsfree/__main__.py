# handsfree/__main__.py
import logging
import sys
import threading
import time
import re

from .config import load_config
from .hotkey import GlobalHotkeyListener
from .recorder import Recorder
from .transcriber import transcribe_audio
from . import utils
from .gui import HandsfreeGUI

def main():
    # 1. Load config from .env
    config = load_config()

    # 2. Logging setup
    logging.basicConfig(
        level=config["LOG_LEVEL"],
        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s"
    )
    logger = logging.getLogger("handsfree")
    logger.info("Starting handsfree application...")

    # 3. Initialize Recorder
    recorder = Recorder(max_seconds=config["MAX_RECORD_SECONDS"])
    recorder.save_recordings = config["SAVE_RECORDINGS"]

    is_recording = False

    # 4. Create GUI (Tk + optional tray icon on Linux)
    gui = HandsfreeGUI()
    gui.set_status("IDLE")

    # 5. Callback for global hotkey (start/stop recording)
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
                try:
                    # 1. Call transcriber
                    transcription = transcribe_audio(
                        audio_data,
                        whisper_url=config["WHISPER_URL"],
                        api_key=config["API_KEY"],
                        model=config["WHISPER_MODEL"],
                        language=config["WHISPER_LANGUAGE"],
                        mode=config["WHISPER_MODE"],
                        cli_command=config["WHISPER_CLI_COMMAND"],
                        cli_args=config["WHISPER_CLI_ARGS"]
                    )

                    # 2. Post-process the text
                    transcription = transcription.strip()
                    if config["REPLACE_ALL_WHITESPACE_WITH_SPACE"]:
                        transcription = re.sub(r"\s+", " ", transcription)

                    logger.debug(f"Final transcription after transformations: '{transcription}'")

                    # 3. Optional delay
                    delay = config["TYPE_START_DELAY"]
                    if delay > 0:
                        logger.debug(f"Sleeping {delay}s before typing text.")
                        time.sleep(delay)

                    # 4. Type the text
                    utils.type_text(transcription)

                except Exception as e:
                    # If something goes wrong, log it
                    logger.exception(f"Transcription worker error: {e}")

                finally:
                    # Always go back to IDLE, even if there's an error
                    gui.set_status("IDLE")

            # Run the worker in a separate thread
            threading.Thread(target=worker, daemon=True).start()

    # 6. Start the global hotkey listener in a thread
    listener = GlobalHotkeyListener(
        shortcut=config["KEYBOARD_SHORTCUT"],
        on_activate=on_hotkey_triggered
    )
    hotkey_thread = threading.Thread(target=listener.start, daemon=True)
    hotkey_thread.start()

    # 7. Clean shutdown callback
    def on_close():
        logger.info("Exiting handsfree...")
        if is_recording:
            recorder.stop_recording()
        recorder.terminate()
        listener.stop()
        gui.close()
        sys.exit(0)

    gui.set_on_close_callback(on_close)

    # 8. Run the GUI main loop
    gui.run()

if __name__ == "__main__":
    main()
