# Whisper Models

This folder should contain at least one GGML Whisper model file.

## Download Instructions

Download one or more models from HuggingFace:

| Model | Size | Quality | Link |
|-------|------|---------|------|
| **ggml-small.en.bin** (recommended) | ~488 MB | Best accuracy/speed trade-off, English only | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin) |
| ggml-base.bin | ~148 MB | Faster, multilingual, less accurate | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin) |
| ggml-tiny.bin | ~75 MB | Fastest, lowest accuracy | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin) |
| ggml-small.bin | ~466 MB | Like small.en but multilingual | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin) |
| ggml-medium.bin | ~1.5 GB | High accuracy, much slower | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin) |

## Quick Start

For most users, download **ggml-small.en.bin** and place it here:

```
models/ggml-small.en.bin
```

## Notes

- Model files are not committed to git (they're in .gitignore)
- The app defaults to `ggml-small.en.bin`, and falls back to any `.bin` found here
- Select a specific model with the `HUM_MODEL` environment variable, e.g.
  `HUM_MODEL=ggml-base.bin python main.py`
- Larger models are more accurate but require more RAM and are slower to transcribe
- On CPU-only machines, models above `small` can run slower than realtime — see the
  measured comparison in the main README
