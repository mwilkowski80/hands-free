# handsfree/config.py
import os
import logging
from dotenv import load_dotenv

def load_config():
    load_dotenv()  # loads variables from .env, if present

    debug_str = os.getenv("DEBUG", "false").lower()
    log_level = logging.DEBUG if debug_str == "true" else logging.INFO

    return {
        "LOG_LEVEL": log_level,

        # For API mode
        "API_KEY": os.getenv("API_KEY", ""),
        "WHISPER_URL": os.getenv("WHISPER_URL", "http://localhost:8000/inference"),

        # For both
        "WHISPER_MODEL": os.getenv("WHISPER_MODEL", "whisper-1"),
        "WHISPER_LANGUAGE": os.getenv("WHISPER_LANGUAGE", "en"),

        # CLI vs. API
        "WHISPER_MODE": os.getenv("WHISPER_MODE", "api"),
        "WHISPER_CLI_COMMAND": os.getenv("WHISPER_CLI_COMMAND", "whisper"),
        "WHISPER_CLI_ARGS": os.getenv("WHISPER_CLI_ARGS", ""),

        "KEYBOARD_SHORTCUT": os.getenv("KEYBOARD_SHORTCUT", "ctrl+alt+f5"),
        "MAX_RECORD_SECONDS": int(os.getenv("MAX_RECORD_SECONDS", "30")),
        "SAVE_RECORDINGS": os.getenv("SAVE_RECORDINGS", "false").lower() == "true",

        "SOUND_START": os.getenv("SOUND_START", "handsfree/sounds/start.wav"),
        "SOUND_STOP": os.getenv("SOUND_STOP", "handsfree/sounds/stop.wav"),

        "TYPE_START_DELAY": float(os.getenv("TYPE_START_DELAY", "0.0")),
        "REPLACE_ALL_WHITESPACE_WITH_SPACE": os.getenv("REPLACE_ALL_WHITESPACE_WITH_SPACE", "false").lower() == "true",
    }
