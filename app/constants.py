import os

APP_NAME = "Hum"
APP_VERSION = "0.1.0"

# Paths (Windows defaults)
SERVER_EXE = r"C:\Users\m.siddiquie\AppData\Local\Programs\Buzz\_internal\buzz\whisper_cpp\whisper-server.exe"
MODELS_DIR = r"C:\Users\m.siddiquie\AppData\Local\Buzz\Buzz\Cache\models\models--ggerganov--whisper.cpp\snapshots\main"
DEFAULT_MODEL = "ggml-base.bin"
MODEL_PATH = os.path.join(MODELS_DIR, DEFAULT_MODEL)

# Server
PORT = 3003
LANGUAGE = "en"
THREADS = max(1, (os.cpu_count() or 8) // 2)

# Audio
SAMPLE_RATE = 16000
