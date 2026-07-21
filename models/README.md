# Whisper Models

This folder should contain at least one GGML Whisper model file.

## Download Instructions

Download one or more models from HuggingFace:

| Model | Size | Quality | Link |
|-------|------|---------|------|
| **ggml-base.bin** (recommended) | ~148 MB | Good balance of speed and accuracy | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin) |
| ggml-tiny.bin | ~75 MB | Fastest, lower accuracy | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin) |
| ggml-small.bin | ~466 MB | Better accuracy, slower | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin) |
| ggml-medium.bin | ~1.5 GB | High accuracy, much slower | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin) |

## Quick Start

For most users, download **ggml-base.bin** and place it here:

```
models/ggml-base.bin
```

## Notes

- Model files are not committed to git (they're in .gitignore)
- The app defaults to `ggml-base.bin` — you can switch models in the settings panel
- Larger models are more accurate but require more RAM and are slower to transcribe
