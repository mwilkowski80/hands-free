# Handsfree

**Handsfree** is a cross-platform Python application that lets you record audio on the fly (via a hotkey), **optionally send it to a Whisper server** for speech-to-text transcription, or **invoke a local Whisper CLI**. It then automatically types the recognized text into the currently active window. It is designed primarily for Linux, but can also run on macOS and Windows with certain limitations or adjustments (especially regarding global hotkeys and text simulation).

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Linux Tray Icon (optional)](#linux-tray-icon-optional)
- [Running a Whisper Server](#running-a-whisper-server)
  - [Remote vLLM endpoint (PGX2)](#remote-vllm-endpoint-pgx2)
  - [Local self-hosted endpoint](#local-self-hosted-endpoint)
  - [OpenAI Whisper endpoint](#openai-whisper-endpoint)
- [Using a Local Whisper CLI](#using-a-local-whisper-cli)
- [FAQ / Troubleshooting](#faq--troubleshooting)
- [License](#license)

---

## Features
- **Global hotkey** to start/stop recording (configurable via `.env`, e.g. `CTRL+ALT+F5`).
- **Audio capture** using [PyAudio](https://pypi.org/project/PyAudio/).  
- **Automatic speech-to-text** recognition via:
  - A **local or remote Whisper server** over HTTP, or
  - A **local Whisper CLI** tool (e.g. `whisper.cpp`, `whisper-cli`).
- **Automatic text typing** of the recognized text into the active window (using `pyautogui` or `xdotool` on Linux).
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
4. **Whisper usage**:
   - If you use a **server** approach, you need a local or remote endpoint.  
   - If you use a **CLI** approach, you need a working Whisper command-line tool (e.g. `whisper.cpp`, `whisper-cli`, or similar).

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

All configuration is done via a `.env` file placed in the **same directory** you run the app from. A fully documented template lives in [`env.dist`](env.dist) — copy it and fill in your local values (notably `API_KEY`):

```bash
cp env.dist .env
# then edit .env
```

`.env` is gitignored and MUST NOT be committed — keep secrets only there. The example below mirrors `env.dist`; see that file for the authoritative, commented list of every variable.

Example `.env`:

```dotenv
# Turn on debug logs
DEBUG=true

# Choose between "api" (use HTTP server) or "cli" (use local Whisper CLI):
WHISPER_MODE=api

# --- API mode ---
# Recommended: remote whisper-large-v3 on PGX2 (vLLM, OpenAI-compatible).
WHISPER_URL=http://192.168.5.196:29473/v1/audio/transcriptions
WHISPER_MODEL=openai/whisper-large-v3
API_KEY=                 # Bearer token (required for PGX2 / OpenAI)
WHISPER_LANGUAGE=pl      # ISO language hint (pl, en, ...)

# --- CLI mode (only when WHISPER_MODE=cli) ---
WHISPER_CLI_COMMAND=/path/to/whisper-cli
WHISPER_CLI_ARGS=-l pl -nt -m /path/to/model.bin

# Max recording duration (seconds)
MAX_RECORD_SECONDS=600

# Trigger: double-tap mode (window > 0) or single shortcut (window = 0)
DOUBLE_PRESS_WINDOW_MS=800
DOUBLE_PRESS_KEY=ctrl_r
KEYBOARD_SHORTCUT=alt+f3

# Whether to save recordings (WAV) in recordings/
SAVE_RECORDINGS=false

# Paths to the notification sounds
SOUND_START=handsfree/sounds/start.wav
SOUND_STOP=handsfree/sounds/stop.wav

# Optional: delay (in seconds) before typing recognized text
TYPE_START_DELAY=1.0

# Whether to replace all whitespace with a single space
REPLACE_ALL_WHITESPACE_WITH_SPACE=true
```

**Key options**:

- `WHISPER_MODE`: 
  - `api` (default) means the app **posts** audio data to `WHISPER_URL`.  
  - `cli` means the app calls a **local** whisper command (see [Using a Local Whisper CLI](#using-a-local-whisper-cli)).
- `WHISPER_URL`: The HTTP endpoint to which audio is uploaded if `WHISPER_MODE=api`. Default points at the [remote PGX2 vLLM endpoint](#remote-vllm-endpoint-pgx2).
- `WHISPER_CLI_COMMAND` / `WHISPER_CLI_ARGS`: The CLI command and arguments if `WHISPER_MODE=cli`.
- `API_KEY`: Bearer token if your Whisper server requires one (the PGX2 service and OpenAI both do).
- `WHISPER_MODEL` and `WHISPER_LANGUAGE`: Model id (must match what the server serves, e.g. `openai/whisper-large-v3`) and spoken-language hint.
- `MAX_RECORD_SECONDS`: Recording will auto-stop after this time.
- `DOUBLE_PRESS_WINDOW_MS` / `DOUBLE_PRESS_KEY`: When the window is `> 0`, two quick presses of `DOUBLE_PRESS_KEY` toggle recording (and `KEYBOARD_SHORTCUT` is ignored).
- `KEYBOARD_SHORTCUT`: Single combo used only when `DOUBLE_PRESS_WINDOW_MS=0`, e.g. `alt+f3` or `ctrl+alt+f5`.
- `SAVE_RECORDINGS`: If `true`, WAV files are saved in `recordings/`.
- `TYPE_START_DELAY`: A float specifying a delay **before** typing text (to release Ctrl/Alt or switch windows).
- `REPLACE_ALL_WHITESPACE_WITH_SPACE`: If `true`, all whitespace (including newlines) is replaced by single spaces.

---

## Usage

1. **Ensure** you have either:
   - A Whisper server running (see [Running a Whisper Server](#running-a-whisper-server)), **or**
   - A local Whisper CLI if you’re using `WHISPER_MODE=cli`.
2. **Run** the application:
   ```bash
   python -m handsfree
   ```
3. The program launches a small **Tkinter** window showing a `Status: IDLE`.  
   - On **Linux**, if you have `AppIndicator3` installed and a compatible tray, you should also see a tray icon.
4. Press the **global hotkey** (e.g. `CTRL+ALT+F5`) to **start** recording (status changes to `RECORDING`, and you should hear a beep if configured).
5. Press the **global hotkey** again to **stop** recording (you should hear the stop sound). The audio is sent to Whisper (via REST or CLI).
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

### Remote vLLM endpoint (PGX2)

This is the **default, recommended** setup: instead of running Whisper locally,
the app offloads transcription to `whisper-large-v3` served by **vLLM on the
PGX2 GB10 box** over the LAN. It exposes the OpenAI-compatible
`POST /v1/audio/transcriptions` endpoint (multipart `file` + `model` +
`language`, returns JSON with a `text` field), so no client code changes are
needed.

Your `.env`:
```dotenv
WHISPER_MODE=api
WHISPER_URL=http://192.168.5.196:29473/v1/audio/transcriptions
WHISPER_MODEL=openai/whisper-large-v3
API_KEY=<bearer-token>     # required; matches PGX_WHISPER_API_KEY on PGX2
WHISPER_LANGUAGE=pl
```

The server itself (Docker Compose + vLLM + systemd auto-start) is defined and
documented in the PGX operations repo at
`ai-shared-settings/pgx/vllm-whisper-large/` — see its `README.md` for the port,
model id, auth, and deploy steps. The `WHISPER_MODEL` here must match the model
served there.

Quick sanity check that the endpoint is reachable and the token is valid:
```bash
curl -s http://192.168.5.196:29473/v1/audio/transcriptions \
  -H "Authorization: Bearer $API_KEY" \
  -F "file=@sample.wav;type=audio/wav" \
  -F "model=openai/whisper-large-v3" -F "language=pl"
# -> {"text":" ...transcription...","usage":{...}}
```

### Local self-hosted endpoint
If you run a local instance of Whisper (for example, a Docker container or a script that accepts a `multipart/form-data` request), you might have an endpoint like:

```
http://localhost:8000/inference
```

Your `.env` would then include:
```dotenv
WHISPER_MODE=api
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
WHISPER_MODE=api
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

## Using a Local Whisper CLI

If you **don’t** want to rely on an HTTP server for transcription, you can set:

```dotenv
WHISPER_MODE=cli
WHISPER_CLI_COMMAND=/path/to/whisper-cli
WHISPER_CLI_ARGS=-l pl -nt -m /path/to/model.bin
```

When the recording ends, **Handsfree** will:
1. Save the recorded audio to a **temporary WAV file** (in `/tmp` or another system temp folder).
2. Call a command line similar to:
   ```
   /path/to/whisper-cli -l pl -nt -m /path/to/model.bin /path/to/temp.wav
   ```
   discarding any `stderr`.
3. Capture the **transcribed text** from `stdout`.

You might use [whisper.cpp](https://github.com/ggerganov/whisper.cpp) (which provides `whisper-cli`), or any other Whisper-based CLI tool. Make sure the command produces a plain-text transcription on `stdout`, which Handsfree can read.

**Example**:
```dotenv
WHISPER_MODE=cli
WHISPER_CLI_COMMAND=x 127 x /media/mw/Storage/whisper.cpp/build/bin/whisper-cli
WHISPER_CLI_ARGS=-l pl -nt -m /media/mw/Storage/whisper.cpp/models/ggml-large-v3.bin
```
This will run something like:
```
x 127 x /media/mw/Storage/whisper.cpp/build/bin/whisper-cli -l pl -nt \
  -m /media/mw/Storage/whisper.cpp/models/ggml-large-v3.bin \
  /tmp/tempfile.wav
```
when you stop the recording.

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
6. **API vs. CLI**:  
   - If `WHISPER_MODE=api`, the application does a `POST` to `WHISPER_URL`.  
   - If `WHISPER_MODE=cli`, the application calls `WHISPER_CLI_COMMAND` with `WHISPER_CLI_ARGS` and a temp WAV file.
7. **OpenAI vs. local**:  
   - Make sure your `.env` has the correct `WHISPER_URL`, `API_KEY`, or CLI paths.  

---

## License

This project is distributed under the [MIT License](https://opensource.org/licenses/MIT).

## Known issues
1. Icons are not ready.
2. Application is so far tested only on Linux.
3. More documentation needed for advanced Whisper usage.

---

**Enjoy using Handsfree!** If you have any questions or issues, please open an issue or reach out.
