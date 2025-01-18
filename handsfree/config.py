# handsfree/config.py
import os
import logging
from dotenv import load_dotenv

def load_config():
    load_dotenv()  # wczyta zmienne z pliku .env

    debug_str = os.getenv("DEBUG", "false").lower()
    log_level = logging.DEBUG if debug_str == "true" else logging.INFO

    return {
        "LOG_LEVEL": log_level,
        "API_KEY": os.getenv("API_KEY", ""),
        "WHISPER_URL": os.getenv("WHISPER_URL", "http://localhost:8000/transcribe"),
        "MODEL": os.getenv("MODEL", "whisper-1"),
        "LANGUAGE": os.getenv("LANGUAGE", "en"),
        "KEYBOARD_SHORTCUT": os.getenv("KEYBOARD_SHORTCUT", "ctrl+alt+f5"),
        "MAX_RECORD_SECONDS": int(os.getenv("MAX_RECORD_SECONDS", "30")),
        "SAVE_RECORDINGS": os.getenv("SAVE_RECORDINGS", "false").lower() == "true",

        # Ścieżki do plików dźwiękowych
        "SOUND_START": os.getenv("SOUND_START", "handsfree/sounds/start.wav"),
        "SOUND_STOP": os.getenv("SOUND_STOP", "handsfree/sounds/stop.wav"),

        # Jednorazowe opóźnienie przed wpisaniem (jeśli masz, domyślnie 0.0)
        "TYPE_START_DELAY": float(os.getenv("TYPE_START_DELAY", "0.0")),

        # NOWA FLAGA – czy zamieniać wszystkie białe znaki na spację
        "REPLACE_ALL_WHITESPACE_WITH_SPACE": os.getenv("REPLACE_ALL_WHITESPACE_WITH_SPACE", "false").lower() == "true",
    }
