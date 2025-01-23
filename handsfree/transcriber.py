# handsfree/transcriber.py
import re
import requests
import logging
import os
import subprocess
import tempfile

logger = logging.getLogger(__name__)

def transcribe_audio(
    audio_data,
    whisper_url,
    api_key,
    model="whisper-1",
    language="en",
    mode="api",
    cli_command="whisper",
    cli_args=""
):
    """
    :param audio_data: bytes (WAV)
    :param whisper_url: e.g. http://localhost:8000/inference if mode=api
    :param api_key: token if needed
    :param model: relevant for API or fallback
    :param language: relevant for API or fallback
    :param mode: "api" or "cli"
    :param cli_command: e.g. "x 127 x /path/to/whisper-cli"
    :param cli_args: e.g. "-l pl -nt -m /path/to/model.bin"
    :return: recognized text (str)
    """

    if mode == "api":
        # -- REST API mode --
        files = {
            "file": ("recording.wav", audio_data, "audio/wav")
        }
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        data = {
            "model": model,
            "language": language
        }

        try:
            resp = requests.post(whisper_url, headers=headers, files=files, data=data, timeout=120)
            resp.raise_for_status()
            result = resp.json()
            transcription = result.get("transcription") or result.get("text") or ""
            logger.info(f"Transcription (API) result: {transcription}")
            return transcription
        except requests.exceptions.RequestException as e:
            logger.exception(f"Error sending audio to Whisper server: {e}")
            return ""

    elif mode == "cli":
        # -- Local CLI mode --
        # 1. Write WAV to a temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            tmp_wav.write(audio_data)
            tmp_wav.flush()
            tmp_wav_path = tmp_wav.name

        logger.debug(f"Created temp WAV file at {tmp_wav_path}")

        # 2. Build the command
        command_parts = cli_command.split()     # e.g. ["x","127","x","/media/.../whisper-cli"]
        extra_args = cli_args.split()           # e.g. ["-l","pl","-nt","-m","/path/to/model.bin"]
        full_cmd = command_parts + extra_args + [tmp_wav_path]

        logger.info(f"Running local whisper CLI: {' '.join(full_cmd)} (stderr -> /dev/null)")

        try:
            # We cannot use capture_output=True with a custom stderr=... 
            # So we do explicit stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            result = subprocess.run(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=True
            )
            transcription = re.sub(pattern=r'^-\s*', repl='', string=result.stdout.strip())
            logger.info(f"Transcription (CLI) result: {transcription}")
            return transcription

        except FileNotFoundError:
            logger.exception(f"Whisper CLI tool not found. Command: {cli_command}")
            return ""
        except subprocess.CalledProcessError as e:
            logger.exception(f"Whisper CLI returned error: {e}")
            return ""
        finally:
            # 3. Clean up temp file
            try:
                os.remove(tmp_wav_path)
            except OSError:
                pass

    else:
        logger.error(f"Unknown mode: {mode}")
        return ""
