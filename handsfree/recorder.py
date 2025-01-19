# handsfree/recorder.py
import pyaudio
import wave
import time
import logging
import io
import os
from threading import Thread

logger = logging.getLogger(__name__)

class Recorder:
    def __init__(self, max_seconds=30):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.max_seconds = max_seconds

        self._pyaudio = pyaudio.PyAudio()
        self._stream = None
        self._frames = []
        self._is_recording = False
        self._recording_thread = None

        self.save_recordings = False

    def start_recording(self):
        if self._is_recording:
            logger.debug("Already recording!")
            return

        logger.info("Starting recording...")
        self._frames = []
        self._stream = self._pyaudio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        self._is_recording = True
        self._recording_thread = Thread(target=self._record)
        self._recording_thread.start()

    def _record(self):
        start_time = time.time()
        while self._is_recording:
            data = self._stream.read(self.chunk, exception_on_overflow=False)
            self._frames.append(data)
            if (time.time() - start_time) >= self.max_seconds:
                logger.info("Reached max recording time, stopping automatically.")
                self.stop_recording()
                break

    def stop_recording(self):
        if not self._is_recording:
            logger.debug("Not recording right now.")
            return None

        logger.info("Stopping recording...")
        self._is_recording = False
        if self._recording_thread:
            self._recording_thread.join()

        self._stream.stop_stream()
        self._stream.close()

        wav_data = self._generate_wav_bytes(self._frames)
        if self.save_recordings:
            self._save_to_file(wav_data)

        return wav_data

    def _generate_wav_bytes(self, frames):
        wav_buffer = io.BytesIO()
        wf = wave.open(wav_buffer, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self._pyaudio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        wav_buffer.seek(0)
        return wav_buffer.read()

    def _save_to_file(self, wav_data):
        timestamp = int(time.time())
        filename = f"recording_{timestamp}.wav"
        folder = os.path.join(os.path.dirname(__file__), "recordings")
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)
        with open(filepath, "wb") as f:
            f.write(wav_data)
        logger.info(f"Saved recording to {filepath}")

    def terminate(self):
        self._pyaudio.terminate()
