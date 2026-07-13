import sys
import logging
import threading
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, Signal, QObject

from core.state import AppState
from ui.floating_pill import FloatingPill
from ui.expanded_panel import ExpandedPanel
from services.audio_recorder import AudioRecorder
from services.speech_engine import WhisperCppEngine

logger = logging.getLogger(__name__)


class SignalBridge(QObject):
    """Bridge for thread-safe signals from background threads to UI."""
    transcription_done = Signal(str)
    insertion_done = Signal()
    state_change = Signal(int)  # AppState value


class Voice2TextApp:
    """Main application controller. Manages state and wires components."""

    def __init__(self, qt_app: QApplication):
        self.qt_app = qt_app
        self._state = AppState.IDLE

        # Signal bridge for thread safety
        self._bridge = SignalBridge()
        self._bridge.transcription_done.connect(self._on_transcription_done)
        self._bridge.insertion_done.connect(self._on_insertion_done)
        self._bridge.state_change.connect(self._on_state_change)

        # Timer to return to IDLE after SUCCESS
        self._success_timer = QTimer()
        self._success_timer.setSingleShot(True)
        self._success_timer.timeout.connect(lambda: self.set_state(AppState.IDLE))

        # Services
        self.recorder = AudioRecorder()
        self.engine = WhisperCppEngine()
        self.text_inserter = None

        # Load text inserter (Windows only for now)
        if sys.platform == "win32":
            from backends.windows.text_inserter import WindowsTextInserter
            self.text_inserter = WindowsTextInserter()

        # UI
        self.pill = FloatingPill()
        self.pill.clicked.connect(self._on_pill_clicked)
        self.pill.exit_clicked.connect(self._on_exit)
        self.pill.settings_clicked.connect(self._on_settings)
        self.pill.copy_error_clicked.connect(self._on_copy_error)

        # Expanded panel
        self.panel = ExpandedPanel()
        self.panel.closed.connect(self._on_panel_closed)
        self.panel.model_changed.connect(self._on_model_changed)
        self.panel.language_changed.connect(self._on_language_changed)
        self._panel_visible = False

    @property
    def state(self) -> AppState:
        return self._state

    def set_state(self, state: AppState):
        self._state = state
        self.pill.set_state(state)
        logger.info(f"State -> {state.name}")

        if state == AppState.SUCCESS:
            self._success_timer.start(1500)

    def _on_state_change(self, state_val: int):
        self.set_state(AppState(state_val))

    def _on_pill_clicked(self):
        if self._state == AppState.IDLE:
            self._start_recording()
        elif self._state == AppState.RECORDING:
            self._stop_recording()
        elif self._state == AppState.SUCCESS:
            self._success_timer.stop()
            self._start_recording()
        elif self._state == AppState.ERROR:
            # Click on error returns to idle
            self.set_state(AppState.IDLE)

    def _start_recording(self):
        self.recorder.start_recording()
        self.set_state(AppState.RECORDING)

    def _stop_recording(self):
        audio = self.recorder.stop_recording()
        duration = len(audio) / 16000
        logger.info(f"Captured {duration:.1f}s of audio")

        self.set_state(AppState.PROCESSING)

        # Transcribe in background thread
        thread = threading.Thread(target=self._transcribe, args=(audio,), daemon=True)
        thread.start()

    def _transcribe(self, audio):
        """Run transcription in background thread."""
        try:
            text = self.engine.transcribe(audio)
            if text:
                self._bridge.transcription_done.emit(text)
            else:
                logger.warning("Transcription returned empty text")
                self._bridge.state_change.emit(AppState.ERROR.value)
        except Exception as e:
            logger.error(f"Transcription thread error: {e}")
            self._bridge.state_change.emit(AppState.ERROR.value)

    def _on_transcription_done(self, text: str):
        logger.info(f"Transcribed: {text[:80]}...")

        # Insert text at cursor in background thread
        if self.text_inserter:
            thread = threading.Thread(
                target=self._insert_text, args=(text,), daemon=True
            )
            thread.start()
        else:
            logger.info(f"[No inserter] Text: {text}")
            self.set_state(AppState.SUCCESS)

    def _insert_text(self, text: str):
        """Run text insertion in background to not block UI."""
        import time
        time.sleep(0.3)  # Brief delay to let focus stay on target app
        logger.info(f"Inserting text ({len(text)} chars)...")
        success = self.text_inserter.insert(text)
        if success:
            logger.info("Text inserted successfully")
            self._bridge.insertion_done.emit()
        else:
            logger.error("Text insertion failed")
            self._bridge.state_change.emit(AppState.ERROR.value)

    def _on_insertion_done(self):
        self.set_state(AppState.SUCCESS)

    def _on_copy_error(self):
        """Copy error logs to clipboard."""
        import subprocess
        log_text = "Voice2Text Error Log\n" + "-" * 40 + "\nTranscription failed. Check whisper-server status."
        try:
            process = subprocess.Popen(
                ["clip.exe"],
                stdin=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            process.communicate(input=log_text.encode("utf-16-le"))
            logger.info("Error logs copied to clipboard")
        except Exception as e:
            logger.error(f"Failed to copy error logs: {e}")

    def _on_exit(self):
        """Shutdown everything and quit."""
        logger.info("Exit requested")
        if self.recorder.is_recording:
            self.recorder.stop_recording()
        self.engine.shutdown()
        self.qt_app.quit()

    def _on_settings(self):
        """Toggle settings panel."""
        if self._panel_visible:
            self.panel.hide()
            self._panel_visible = False
        else:
            self.panel.show_below(self.pill)
            self._panel_visible = True

    def _on_panel_closed(self):
        self._panel_visible = False

    def _on_model_changed(self, model_name: str):
        logger.info(f"Model changed to: {model_name}")
        # Would need to restart server with new model — for now just log
        import os
        from app.constants import MODELS_DIR
        new_path = os.path.join(MODELS_DIR, model_name)
        logger.info(f"Model path: {new_path} (restart required to apply)")

    def _on_language_changed(self, lang_code: str):
        logger.info(f"Language changed to: {lang_code}")

    def run(self):
        # Start whisper server
        logger.info("Starting whisper engine...")
        if not self.engine.start():
            logger.error("Failed to start whisper engine. Exiting.")
            return 1

        logger.info("Engine ready. Showing UI.")
        self.pill.show()

        # Run Qt event loop
        exit_code = self.qt_app.exec()

        # Cleanup
        logger.info("Shutting down...")
        if self.recorder.is_recording:
            self.recorder.stop_recording()
        self.engine.shutdown()

        return exit_code
