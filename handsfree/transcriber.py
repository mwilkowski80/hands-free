# handsfree/transcriber.py
import requests
import logging

logger = logging.getLogger(__name__)

def transcribe_audio(audio_data, whisper_url, api_key, model="whisper-1", language="en"):
    """
    audio_data: bytes z nagraniem w formacie WAV
    whisper_url: np. http://localhost:7777/inference
    api_key: jeśli jest wymagany
    model, language: ewentualne parametry
    """
    files = {
        "file": ("recording.wav", audio_data, "audio/wav")
    }
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    data = {
        'response_format': 'text',
        'language': language,
        'model': model,
    }

    try:
        resp = requests.post(whisper_url, headers=headers, files=files, data=data, timeout=120)
        resp.raise_for_status()
        transcription = resp.text
        logger.info(f"Transcription result: {transcription}")
        return transcription
    except requests.exceptions.RequestException as e:
        logger.exception(f"Error sending audio to Whisper server: {e}")
        return ""
