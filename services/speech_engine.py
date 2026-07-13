import io
import wave
import logging
import numpy as np
from openai import OpenAI

from core.interfaces import SpeechEngineInterface
from app.constants import PORT, LANGUAGE
from backends.windows.server import WhisperServer

logger = logging.getLogger(__name__)


class WhisperCppEngine(SpeechEngineInterface):
    """Speech engine backed by local whisper.cpp server."""

    def __init__(self, model_path: str = None):
        self._server = WhisperServer(model_path=model_path)
        self._client = None

    def start(self) -> bool:
        if not self._server.start():
            return False
        self._client = OpenAI(
            api_key="not-used",
            base_url=f"http://127.0.0.1:{PORT}",
            timeout=120.0,
            max_retries=0,
        )
        return True

    @property
    def is_ready(self) -> bool:
        return self._server.is_running

    def transcribe(self, audio: np.ndarray) -> str:
        logger.info(f"transcribe() called: {len(audio)} samples, {len(audio)/16000:.1f}s")
        if len(audio) < 8000:  # Less than 0.5s
            logger.info("Audio too short, skipping")
            return ""

        # Split into 30s chunks
        chunk_size = 30 * 16000
        chunks = [audio[i:i + chunk_size] for i in range(0, len(audio), chunk_size)]

        full_text = []
        prompt = ""

        for chunk in chunks:
            text = self._transcribe_chunk(chunk, prompt)
            if text:
                full_text.append(text)
                prompt = text

        return " ".join(full_text).strip()

    def _transcribe_chunk(self, audio_chunk: np.ndarray, prompt: str) -> str:
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        logger.info(f"Chunk RMS: {rms:.6f}, samples: {len(audio_chunk)}")
        if rms < 0.001:
            logger.info("Chunk too quiet, skipping")
            return ""

        pcm_data = (audio_chunk * 32767).astype(np.int16).tobytes()

        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(pcm_data)

        wav_buffer.seek(0)
        wav_buffer.name = "audio.wav"

        try:
            transcript = self._client.audio.transcriptions.create(
                model="whisper-1",
                file=wav_buffer,
                response_format="json",
                language=LANGUAGE,
                prompt=prompt,
            )

            text = ""
            if hasattr(transcript, "model_extra") and transcript.model_extra.get("segments"):
                text = " ".join(
                    seg["text"] for seg in transcript.model_extra["segments"]
                )
            else:
                text = transcript.text

            text = text.strip()
            if text in ("[BLANK_AUDIO]", "(silence)"):
                return ""
            return text

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""

    def shutdown(self) -> None:
        self._server.shutdown()
