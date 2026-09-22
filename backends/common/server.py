import os
import subprocess
import sys
import time
import logging
import urllib.request
import urllib.error

from app.constants import SERVER_EXE, MODEL_PATH, PORT, LANGUAGE, THREADS

logger = logging.getLogger(__name__)


def _missing_server_hint() -> str:
    if sys.platform == "win32":
        return (
            "Download it from https://github.com/ggml-org/whisper.cpp/releases "
            "and place it in the whisper_cpp/ folder."
        )
    return (
        "Build it by running scripts/setup_linux.sh, or follow the instructions "
        "in whisper_cpp/README.md."
    )


class WhisperServer:
    """Manages the whisper.cpp server lifecycle.

    Platform-neutral: the binary name is resolved in app.constants, and the
    Windows-only process flags are applied conditionally.
    """

    def __init__(self, model_path: str = None):
        self.model_path = model_path or MODEL_PATH
        self.process = None

    def start(self) -> bool:
        if not os.path.isfile(SERVER_EXE):
            logger.error(
                f"whisper.cpp server not found at: {SERVER_EXE}\n"
                f"{_missing_server_hint()}"
            )
            return False

        if not os.path.isfile(self.model_path):
            logger.error(
                f"Whisper model not found at: {self.model_path}\n"
                "Please download a model from "
                "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin "
                "and place it in the models/ folder."
            )
            return False

        cmd = [
            SERVER_EXE,
            "--port", str(PORT),
            "--inference-path", "/audio/transcriptions",
            "--threads", str(THREADS),
            "--model", self.model_path,
            "--no-timestamps",
            "--max-context", "8",
            "--entropy-thold", "2.8",
            "--suppress-nst",
            "--language", LANGUAGE,
        ]

        logger.info(f"Starting whisper-server: {' '.join(cmd)}")

        try:
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                shell=False,
                creationflags=creation_flags,
            )
        except Exception as e:
            logger.error(f"Failed to start whisper-server: {e}")
            return False

        return self._wait_for_ready(timeout=30)

    def _wait_for_ready(self, timeout: int) -> bool:
        start = time.time()
        url = f"http://127.0.0.1:{PORT}/health"

        while time.time() - start < timeout:
            if self.process.poll() is not None:
                stderr = self.process.stderr.read().decode(errors="replace")
                logger.error(f"whisper-server exited early: {stderr}")
                return False

            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=2):
                    logger.info("whisper-server is ready")
                    return True
            except (urllib.error.URLError, OSError):
                time.sleep(0.5)

        logger.error("whisper-server did not become ready in time")
        return False

    @property
    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def shutdown(self):
        if self.process and self.process.poll() is None:
            logger.info("Shutting down whisper-server")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
