# Handsfree

**Handsfree** is a cross-platform Python application that lets you record audio on the fly (via a hotkey), send it to a Whisper server for speech-to-text transcription, and then automatically type the recognized text into any active window. It is designed primarily for Linux, but can also run on macOS and Windows with certain limitations or adjustments (especially regarding global hotkeys and text simulation).

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Linux Tray Icon (optional)](#linux-tray-icon-optional)
- [Running a Whisper Server](#running-a-whisper-server)
  - [Local self-hosted endpoint](#local-self-hosted-endpoint)
  - [OpenAI Whisper endpoint](#openai-whisper-endpoint)
- [FAQ / Troubleshooting](#faq--troubleshooting)
- [License](#license)

---

## Features
- **Global hotkey** to start/stop recording (configurable via `.env`, e.g. `CTRL+ALT+F5`).
- **Audio capture** using [PyAudio](https://pypi.org/project/PyAudio/).  
- **Automatic sending** of the audio to a Whisper server (local or remote).
- **Speech-to-text** recognition via Whisper.
- **Automatic text typing** of the transcription into the currently active window.
- **Configurable behaviors** via `.env`:
  - Maximum recording time,
  - Save recordings or not,
  - Strip or replace whitespace,
  - Optional delay before typing,
  - And more!
- **Optional tray icon** on Linux to show whether the app is idle or recording.

---

## Requirements

1. **Python 3.7+** (tested with Python 3.8+).
2. **PortAudio** (required by PyAudio).
   - On Ubuntu/Debian: `sudo apt-get install portaudio19-dev`
   - On macOS: `brew install portaudio`
   - On Windows: install via the [official binaries](http://www.portaudio.com/download.html) or use `pipwin install pyaudio`.
3. **Python packages** (listed in `requirements.txt`):
   - `python-dotenv`
   - `pynput`
   - `pyaudio`
   - `playsound`
   - `requests`
   - `pyautogui`
   - (Optional, recommended on Linux) `PyGObject` + `libappindicator` for tray icon:  
     - Ubuntu/Debian: `sudo apt-get install python3-gi gir1.2-appindicator3-0.1`
   - (Optional, for Linux only) `xdotool` if you need to type special characters (Polish, etc.) reliably.
4. **Whisper server** (local or remote) – or the OpenAI Whisper API endpoint.

---

## Installation

1. **Clone** this repository or copy the files into your project folder.
   ```bash
   git clone https://github.com/your-username/handsfree.git
   cd handsfree
   ```
2. **Create a virtual environment** (recommended) and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or on Windows: .\venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **(Linux only)** If you want the tray icon, install `libappindicator` and PyGObject:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-gi gir1.2-appindicator3-0.1
   ```
   Also ensure you have a system tray that supports AppIndicator (in GNOME Shell, you may need the AppIndicator extension).

---

## Configuration

All configuration is done via a `.env` file placed in the **same directory** as the `handsfree/` folder (or in your current working directory when you run the app).

Example `.env`:

```dotenv
# Turn on debug logs
DEBUG=true

# Whisper server details
WHISPER_URL=http://localhost:8000/inference
API_KEY=

# Whisper parameters
MODEL=whisper-1
LANGUAGE=en

# Max recording duration (seconds)
MAX_RECORD_SECONDS=30

# Global hotkey for start/stop recording
KEYBOARD_SHORTCUT=ctrl+alt+f5

# Whether to save recordings (WAV) in handsfree/recordings/
SAVE_RECORDINGS=false

# Paths to the notification sounds
SOUND_START=handsfree/sounds/start.wav
SOUND_STOP=handsfree/sounds/stop.wav

# Optional: delay (in seconds) before typing recognized text
TYPE_START_DELAY=1.5

# Whether to replace all whitespace with a single space
REPLACE_ALL_WHITESPACE_WITH_SPACE=true
```

**Key options**:
- `DEBUG`: If `true`, logs are more verbose.
- `WHISPER_URL`: The endpoint to which audio will be uploaded. For local usage, it might be something like `http://localhost:8000/inference`. For OpenAI’s public API, see [OpenAI Whisper endpoint](#openai-whisper-endpoint).
- `API_KEY`: If your Whisper server requires a token, or if using OpenAI’s API.
- `MODEL` and `LANGUAGE`: Adjust according to your Whisper setup.
- `MAX_RECORD_SECONDS`: Recording will auto-stop after this time.
- `KEYBOARD_SHORTCUT`: e.g. `ctrl+alt+f5` or `ctrl+shift+r`.
- `SAVE_RECORDINGS`: If `true`, WAV files are saved in `handsfree/recordings/`.
- `TYPE_START_DELAY`: A float specifying a delay **before** typing text (to release Ctrl/Alt or switch windows).
- `REPLACE_ALL_WHITESPACE_WITH_SPACE`: If `true`, all whitespace (including newlines) is replaced by single spaces.  

---

## Usage

1. **Ensure** you have a Whisper server running (see [Running a Whisper Server](#running-a-whisper-server)) or have a valid `WHISPER_URL` pointing to an external service (e.g. OpenAI).
2. **Run** the application:
   ```bash
   python -m handsfree
   ```
3. The program launches a small **Tkinter** window showing a `Status: IDLE`.  
   - On **Linux**, if you have `AppIndicator3` installed and a compatible tray, you should also see a tray icon.
4. Press the **global hotkey** (e.g. `CTRL+ALT+F5`) to **start** recording (status changes to `RECORDING`, and you should hear a beep if configured).
5. Press the **global hotkey** again to **stop** recording (you should hear the stop sound). The audio is sent to Whisper.
6. After receiving the **transcribed text**, the application will:
   - Wait the optional `TYPE_START_DELAY` seconds,
   - Then **type** the recognized text in the active window (or using `xdotool` on Linux).
7. **Close** the Tkinter window (or tray icon menu) to exit the application.

---

## Linux Tray Icon (optional)

On Linux, the application can show a **tray icon** (idle vs. recording). This requires:

1. Installing libraries:
   ```bash
   sudo apt-get install python3-gi gir1.2-appindicator3-0.1
   ```
2. Having a tray system that supports AppIndicator (e.g. KDE, Xfce, MATE, Ubuntu Unity).  
   - On GNOME Shell, you might need the [AppIndicator extension](https://extensions.gnome.org/extension/615/appindicator-support/).

Two images (`idle.png` and `recording.png`) should be located in `handsfree/icons/`. Their paths are referenced in the `HandsfreeGUI` code. You can customize or rename them, but keep the references consistent.

---

## Running a Whisper Server

### Local self-hosted endpoint
If you run a local instance of Whisper (for example, a Docker container or a script that accepts a `multipart/form-data` request), you might have an endpoint like:

```
http://localhost:8000/inference
```

Your `.env` would then include:
```dotenv
WHISPER_URL=http://localhost:8000/inference
API_KEY=
```

where the server expects POST requests with:
- `file` as a WAV file in multipart/form-data,
- optional parameters like `model`, `language`,
- returns a JSON with a `transcription` field.

### OpenAI Whisper endpoint
If you want to use **OpenAI’s hosted Whisper** API, set:
```dotenv
WHISPER_URL=https://api.openai.com/v1/audio/transcriptions
API_KEY=sk-xxxxxxx  # Your OpenAI API key
```

And ensure your `transcriber.py` or equivalent uses the correct parameters. For example:

```bash
curl --request POST \
  --url https://api.openai.com/v1/audio/transcriptions \
  --header "Authorization: Bearer $OPENAI_API_KEY" \
  --header "Content-Type: multipart/form-data" \
  --form file=@/path/to/file/audio.mp3 \
  --form model=whisper-1
```

Your application code must send data in the same format. If you are using the `requests` library in Python, it might look like this:

```python
files = {
    "file": ("recording.wav", audio_data, "audio/wav")
}
headers = {
    "Authorization": f"Bearer {api_key}"
}
data = {
    "model": "whisper-1"
}
response = requests.post("https://api.openai.com/v1/audio/transcriptions",
                         headers=headers, files=files, data=data)
result = response.json()
transcription = result.get("text", "")
```

In this case, note that **OpenAI** returns the transcribed text under `"text"` rather than `"transcription"`.

---

## FAQ / Troubleshooting

1. **Global hotkey doesn't work**:  
   - On Linux/Wayland, global key listening can be restricted. Try X11 or run as `root`.  
   - Some shortcuts might be reserved by your desktop environment.
2. **PyAudio / PortAudio errors**:  
   - Ensure you installed `portaudio` on your system.  
   - Reinstall `pyaudio` with `pip install pyaudio` or `pipwin install pyaudio` on Windows.
3. **No sound playback (`playsound` error)**:  
   - Check that you have GStreamer/`python3-gi` installed.  
   - Consider using alternative libraries like `simpleaudio` or `pydub` if issues persist.
4. **Polish characters (or other special chars) don’t type**:  
   - On Linux, the app attempts to use `xdotool` if available. Install `xdotool`:
     ```bash
     sudo apt-get install xdotool
     ```
5. **Tray icon doesn’t appear**:  
   - GNOME Shell users might need the AppIndicator extension.  
   - Check that you installed the correct appindicator packages.
6. **OpenAI vs. local Whisper**:  
   - Make sure your `WHISPER_URL` and `API_KEY` match the correct endpoint.  
   - Local endpoint might be `http://localhost:8000/inference`, while OpenAI’s is `https://api.openai.com/v1/audio/transcriptions`.

---

## License

This project is distributed under your preferred [license](https://choosealicense.com/).  
Feel free to replace this section with the actual license text if needed.

---

**Enjoy using Handsfree!** If you have any questions or issues, please open an issue or reach out.