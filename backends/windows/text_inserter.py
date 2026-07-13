import subprocess
import logging

from core.interfaces import TextInserterInterface

logger = logging.getLogger(__name__)


class WindowsTextInserter(TextInserterInterface):
    """Copies text to clipboard. User pastes manually with Ctrl+V."""

    def insert(self, text: str) -> bool:
        if not text:
            return False

        try:
            # Use clip.exe to set clipboard (built into Windows)
            process = subprocess.Popen(
                ["clip.exe"],
                stdin=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            process.communicate(input=text.encode("utf-16-le"))
            logger.info("Text copied to clipboard")
            return True
        except Exception as e:
            logger.error(f"Clipboard copy failed: {e}")
            return False
