#!/usr/bin/env bash
# Set up Hum on Linux: build the whisper.cpp server and fetch a model.
#
# Usage:
#   ./scripts/setup_linux.sh              # builds server + downloads ggml-base.bin
#   MODEL=ggml-tiny.bin ./scripts/setup_linux.sh
#
# Re-running is safe: existing artifacts are left alone.

set -euo pipefail

MODEL="${MODEL:-ggml-base.bin}"
WHISPER_REPO="${WHISPER_REPO:-https://github.com/ggml-org/whisper.cpp}"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER_BIN="$PROJECT_ROOT/whisper_cpp/whisper-server"
MODEL_PATH="$PROJECT_ROOT/models/$MODEL"

echo "==> Hum Linux setup"
echo "    project: $PROJECT_ROOT"

# --- whisper.cpp server ------------------------------------------------------
if [ -x "$SERVER_BIN" ]; then
    echo "==> whisper-server already present, skipping build"
else
    for tool in git c++ cmake; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            echo "!! Missing '$tool'." >&2
            echo "   Install build tools, e.g.:" >&2
            echo "     sudo apt install -y build-essential cmake git" >&2
            echo "   (no root? 'pip install cmake' provides cmake)" >&2
            exit 1
        fi
    done

    BUILD_DIR="$(mktemp -d)"
    trap 'rm -rf "$BUILD_DIR"' EXIT

    echo "==> Cloning whisper.cpp"
    git clone --depth 1 "$WHISPER_REPO" "$BUILD_DIR/whisper.cpp"

    echo "==> Building whisper-server (static)"
    # BUILD_SHARED_LIBS=OFF keeps the binary self-contained, so it does not
    # depend on .so files left behind in a temporary build directory.
    cmake -S "$BUILD_DIR/whisper.cpp" -B "$BUILD_DIR/build" \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_SHARED_LIBS=OFF \
        -DWHISPER_BUILD_TESTS=OFF
    cmake --build "$BUILD_DIR/build" -j"$(nproc)" --target whisper-server

    mkdir -p "$PROJECT_ROOT/whisper_cpp"
    cp "$BUILD_DIR/build/bin/whisper-server" "$SERVER_BIN"
    chmod +x "$SERVER_BIN"
    echo "==> Installed $SERVER_BIN"
fi

# --- model -------------------------------------------------------------------
if [ -f "$MODEL_PATH" ]; then
    echo "==> Model already present: $MODEL_PATH"
else
    echo "==> Downloading $MODEL (this may take a while)"
    mkdir -p "$PROJECT_ROOT/models"
    curl -L --fail -o "$MODEL_PATH" \
        "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/$MODEL"
    echo "==> Installed $MODEL_PATH"
fi

# --- runtime dependency hints ------------------------------------------------
if ! command -v xclip >/dev/null 2>&1 && ! command -v wl-copy >/dev/null 2>&1; then
    echo "!! No clipboard tool found. Install one:"
    echo "     sudo apt install -y xclip        # X11"
    echo "     sudo apt install -y wl-clipboard # Wayland"
fi

echo ""
echo "==> Setup complete. Install Python deps and run:"
echo "      pip install -r requirements.txt"
echo "      python main.py"
