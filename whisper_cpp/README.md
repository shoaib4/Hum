# Whisper.cpp Server

This folder holds the local speech recognition server used by Hum.

## Included

- **whisper-server.exe** — Pre-built Windows binary from the [whisper.cpp](https://github.com/ggml-org/whisper.cpp) project by Georgi Gerganov.

Hum picks the binary for the current platform automatically:

| Platform | Binary | Source |
|----------|--------|--------|
| Windows | `whisper-server.exe` | bundled in this folder |
| Linux | `whisper-server` | built locally (not committed) |

If no bundled binary is present, Hum falls back to a `whisper-server` found on your `PATH`.

## Linux

The easiest route is the setup script, which builds the server and downloads a model:

```bash
./scripts/setup_linux.sh
```

To build manually:

```bash
git clone --depth 1 https://github.com/ggml-org/whisper.cpp
cd whisper.cpp
cmake -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF
cmake --build build -j"$(nproc)" --target whisper-server
cp build/bin/whisper-server ../whisper_cpp/
```

`-DBUILD_SHARED_LIBS=OFF` matters: the default build links the server against
`libwhisper.so` / `libggml*.so` in its build tree, so copying only the executable
produces a binary that breaks once that directory is removed.

## Updating (Windows)

1. Go to the whisper.cpp releases page:
   **https://github.com/ggml-org/whisper.cpp/releases**

2. Download the latest Windows release (look for `whisper-server-*-bin-x64.zip` or similar)

3. Extract `whisper-server.exe` and replace the one in this folder

## Server flags

Hum launches the server from `backends/common/server.py` with a fixed flag set
(`--inference-path`, `--no-timestamps`, `--max-context`, `--entropy-thold`,
`--suppress-nst`, …) and polls `GET /health` to detect readiness. If you swap in a
much older or newer build that renamed a flag or dropped `/health`, startup will
fail with `whisper-server exited early` or a readiness timeout — adjust the flags
in that file to match your build.

## License

The whisper.cpp binaries are from the [whisper.cpp](https://github.com/ggml-org/whisper.cpp)
project, licensed under the MIT License.
