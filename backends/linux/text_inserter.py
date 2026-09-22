import os
import shutil
import subprocess
import logging

from core.interfaces import TextInserterInterface

logger = logging.getLogger(__name__)

# Set HUM_NO_AUTOTYPE=1 to fall back to clipboard-only behaviour.
_AUTOTYPE_ENABLED = os.environ.get("HUM_NO_AUTOTYPE", "") not in ("1", "true", "yes")


def _pick_clipboard_cmd():
    """Prefer the tool matching the session type, fall back to whatever exists."""
    candidates = [
        ("wl-copy", ["wl-copy"]),
        ("xclip", ["xclip", "-selection", "clipboard"]),
    ]
    if not os.environ.get("WAYLAND_DISPLAY"):
        candidates.reverse()

    for exe, cmd in candidates:
        if shutil.which(exe):
            return cmd
    return None


class LinuxTextInserter(TextInserterInterface):
    """Types text at the cursor via XTEST, and always mirrors it to the clipboard.

    The clipboard copy is unconditional so Ctrl+V stays available as a fallback
    when typing is unavailable or lands in the wrong window.
    """

    def __init__(self):
        self._cmd = _pick_clipboard_cmd()
        if self._cmd is None:
            logger.warning(
                "No clipboard tool found. Install wl-clipboard (Wayland) or xclip (X11)."
            )

        self._keyboard = None
        if not _AUTOTYPE_ENABLED:
            logger.info("Auto-type disabled via HUM_NO_AUTOTYPE; using clipboard only")
            return

        try:
            from pynput.keyboard import Controller

            self._keyboard = Controller()
        except Exception as e:
            logger.warning(f"Auto-type unavailable, using clipboard only: {e}")
            return

        if os.environ.get("WAYLAND_DISPLAY"):
            # pynput drives the X11 XTEST extension. Under a Wayland compositor
            # it only reaches XWayland clients, if anything at all.
            logger.warning(
                "Wayland session detected: auto-type is X11-only and may not "
                "reach native Wayland windows. Ctrl+V always works."
            )

    def insert(self, text: str) -> bool:
        if not text:
            return False

        copied = self.copy(text)
        typed = self._type(text)

        if typed:
            logger.info(f"Typed {len(text)} chars at cursor")
        elif copied:
            logger.info("Text copied to clipboard — press Ctrl+V to paste")

        return typed or copied

    def copy(self, text: str) -> bool:
        if not text or self._cmd is None:
            return False

        try:
            process = subprocess.Popen(self._cmd, stdin=subprocess.PIPE)
            process.communicate(input=text.encode("utf-8"))
            if process.returncode != 0:
                logger.error(f"{self._cmd[0]} exited with code {process.returncode}")
                return False
            return True
        except Exception as e:
            logger.error(f"Clipboard copy failed: {e}")
            return False

    def _type(self, text: str) -> bool:
        if self._keyboard is None:
            return False

        try:
            self._keyboard.type(text)
            return True
        except Exception as e:
            logger.error(f"Auto-type failed: {e}")
            return False
