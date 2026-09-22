import os
import shutil
import sys

APP_NAME = "Hum"
APP_VERSION = "0.1.0"

# Determine project root (works both in dev and when packaged with PyInstaller)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths — resolved relative to project/executable root


def _resolve_server_binary() -> str:
    """Prefer the bundled binary, then any whisper-server found on PATH.

    Returns the bundled path even when nothing exists, so callers can report it.
    """
    name = "whisper-server.exe" if sys.platform == "win32" else "whisper-server"
    bundled = os.path.join(BASE_DIR, "whisper_cpp", name)
    if os.path.isfile(bundled):
        return bundled
    return shutil.which(name) or bundled


SERVER_EXE = _resolve_server_binary()
MODELS_DIR = os.path.join(BASE_DIR, "models")
DEFAULT_MODEL = "ggml-base.bin"
MODEL_PATH = os.path.join(MODELS_DIR, DEFAULT_MODEL)

# Server
PORT = 3003
LANGUAGE = "en"
THREADS = max(1, (os.cpu_count() or 8) // 2)

# Audio
SAMPLE_RATE = 16000
