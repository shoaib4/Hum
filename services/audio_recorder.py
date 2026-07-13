import threading
import numpy as np
import sounddevice as sd

from core.interfaces import AudioRecorderInterface
from app.constants import SAMPLE_RATE


class AudioRecorder(AudioRecorderInterface):
    """Records from mic when told to, stores audio locally."""

    def __init__(self, device_index=None):
        self.device_index = device_index
        self.sample_rate = SAMPLE_RATE
        self._buffer = []
        self._lock = threading.Lock()
        self._stream = None
        self._recording = False

    def start_recording(self) -> None:
        self._buffer = []
        self._recording = True
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            device=self.device_index,
            dtype="float32",
            channels=1,
            callback=self._audio_callback,
            blocksize=int(self.sample_rate * 0.1),
        )
        self._stream.start()

    def stop_recording(self) -> np.ndarray:
        self._recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            if self._buffer:
                audio = np.concatenate(self._buffer)
            else:
                audio = np.array([], dtype=np.float32)
            self._buffer = []

        return audio

    def _audio_callback(self, indata, frames, time_info, status):
        if self._recording:
            with self._lock:
                self._buffer.append(indata[:, 0].copy())

    @property
    def is_recording(self) -> bool:
        return self._recording
