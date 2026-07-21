import math
import os
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QPoint, QTimer, Signal, QRect, QRectF
from PySide6.QtGui import (
    QPainter, QColor, QPainterPath, QFont, QPen, QBrush,
    QLinearGradient, QRadialGradient, QPixmap
)
from PySide6.QtSvg import QSvgRenderer

from core.state import AppState

# Load SVG icons
_ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")


def _load_svg(name: str) -> QSvgRenderer:
    path = os.path.join(_ICONS_DIR, f"{name}.svg")
    return QSvgRenderer(path)


def _load_png(name: str) -> QPixmap:
    path = os.path.join(_ICONS_DIR, f"{name}.png")
    return QPixmap(path)


# Colors from reference HTML
class Colors:
    BG = QColor(30, 32, 44)           # rgba(30, 32, 44, 0.78)
    BORDER_IDLE = QColor(100, 116, 139, 102)    # rgba(100,116,139,0.4)
    BORDER_RECORDING = QColor(59, 130, 246, 153)  # rgba(59,130,246,0.6)
    BORDER_PROCESSING = QColor(155, 105, 255, 153)  # rgba(155,105,255,0.6)
    BORDER_SUCCESS = QColor(34, 197, 94, 153)    # rgba(34,197,94,0.6)

    MIC_GRAD_TOP_IDLE = QColor(71, 85, 105)
    MIC_GRAD_BOT_IDLE = QColor(30, 41, 59)
    MIC_GRAD_TOP_REC = QColor(37, 99, 235)
    MIC_GRAD_BOT_REC = QColor(30, 64, 175)
    MIC_GRAD_TOP_PROC = QColor(78, 47, 212)
    MIC_GRAD_BOT_PROC = QColor(43, 22, 111)
    MIC_GRAD_TOP_SUCCESS = QColor(22, 163, 74)
    MIC_GRAD_BOT_SUCCESS = QColor(20, 83, 45)

    TEXT_WHITE = QColor(255, 255, 255)
    TEXT_MUTED = QColor(100, 116, 139)
    TEXT_BLUE = QColor(96, 165, 250)
    TEXT_PURPLE = QColor(184, 150, 255)
    TEXT_GREEN = QColor(74, 222, 128)

    WAVE_BLUE = QColor(96, 165, 250)
    WAVE_PURPLE = QColor(156, 115, 255)
    DOT_PURPLE = QColor(186, 157, 255)

    GEAR_COLOR = QColor(125, 211, 252)    # #7dd3fc blue
    POWER_COLOR = QColor(248, 113, 113)   # #f87171 red
    SPINNER_BG = QColor(255, 255, 255, 10)

    # Error state
    BORDER_ERROR = QColor(248, 113, 113, 153)
    MIC_GRAD_TOP_ERROR = QColor(220, 38, 38)
    MIC_GRAD_BOT_ERROR = QColor(127, 29, 29)
    TEXT_RED = QColor(248, 113, 113)
    TEXT_RED_LIGHT = QColor(252, 165, 165)


PILL_WIDTH = 340
PILL_HEIGHT = 72
PILL_RADIUS = 36
MIC_SIZE = 44
MIC_RADIUS = 14


class FloatingPill(QWidget):
    """Compact floating pill widget matching the HTML reference design."""

    clicked = Signal()
    settings_clicked = Signal()
    exit_clicked = Signal()
    copy_error_clicked = Signal()

    def __init__(self):
        super().__init__()
        self._state = AppState.IDLE
        self._drag_pos = QPoint()
        self._drag_started = False
        self._recording_seconds = 0
        self._recording_timer = QTimer()
        self._recording_timer.timeout.connect(self._tick_timer)
        self._anim_offset = 0
        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._animate)

        # Load SVG icons
        self._svg_settings = _load_svg("settings")
        self._svg_power = _load_svg("power")
        self._svg_copy = _load_svg("copy")

        # Load state PNG icons for the left-side button
        self._icon_idle = _load_png("hum_idle")
        self._icon_listening = _load_png("hum_listening")
        self._icon_processing = _load_png("hum_processing")
        self._icon_success = _load_png("hum_success")
        self._icon_error = _load_png("hum_error")

        self._setup_window()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedSize(PILL_WIDTH, PILL_HEIGHT)

        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - PILL_WIDTH) // 2
        y = screen.height() - PILL_HEIGHT - 80
        self.move(x, y)

    @property
    def state(self) -> AppState:
        return self._state

    def set_state(self, state: AppState):
        self._state = state

        if state == AppState.RECORDING:
            self._recording_seconds = 0
            self._recording_timer.start(1000)
            self._anim_timer.start(50)
        elif state == AppState.PROCESSING:
            self._recording_timer.stop()
            self._anim_timer.start(50)
        else:
            self._recording_timer.stop()
            self._anim_timer.stop()

        self.update()

    def _tick_timer(self):
        self._recording_seconds += 1
        self.update()

    def _animate(self):
        self._anim_offset += 1
        self.update()

    # --- Hit zones ---
    def _settings_rect(self) -> QRect:
        # gear_x = right_x - btn_size - 6 = (PILL_WIDTH-44-12) - 44 - 6
        return QRect(PILL_WIDTH - 106, (PILL_HEIGHT - 44) // 2, 44, 44)

    def _power_rect(self) -> QRect:
        # close_x = right_x = PILL_WIDTH - 44 - 12
        return QRect(PILL_WIDTH - 56, (PILL_HEIGHT - 44) // 2, 44, 44)

    def _copy_rect(self) -> QRect:
        return QRect(PILL_WIDTH - 52, (PILL_HEIGHT - 32) // 2, 36, 36)

    # --- Paint ---
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Pill shape
        path = QPainterPath()
        path.addRoundedRect(QRectF(1, 1, self.width() - 2, self.height() - 2),
                           PILL_RADIUS, PILL_RADIUS)

        # Border color based on state
        border_color = Colors.BORDER_IDLE
        if self._state == AppState.RECORDING:
            border_color = Colors.BORDER_RECORDING
        elif self._state == AppState.PROCESSING:
            border_color = Colors.BORDER_PROCESSING
        elif self._state == AppState.SUCCESS:
            border_color = Colors.BORDER_SUCCESS
        elif self._state == AppState.ERROR:
            border_color = Colors.BORDER_ERROR

        p.setPen(QPen(border_color, 2))
        p.setBrush(QBrush(Colors.BG))
        p.drawPath(path)

        # Mic icon area
        mic_x = 12
        mic_y = (PILL_HEIGHT - MIC_SIZE) // 2
        self._paint_mic_icon(p, mic_x, mic_y)

        # State content
        text_x = mic_x + MIC_SIZE + 14
        if self._state == AppState.IDLE:
            self._paint_idle_content(p, text_x)
        elif self._state == AppState.RECORDING:
            self._paint_recording_content(p, text_x)
        elif self._state == AppState.PROCESSING:
            self._paint_processing_content(p, text_x)
        elif self._state == AppState.SUCCESS:
            self._paint_success_content(p, text_x)
        elif self._state == AppState.ERROR:
            self._paint_error_content(p, text_x)

        # Right side button area
        self._paint_right_button(p)

        p.end()

    def _paint_mic_icon(self, p: QPainter, x: int, y: int):
        """Draw the state-specific icon from PNG assets."""
        if self._state == AppState.IDLE:
            pixmap = self._icon_idle
        elif self._state == AppState.RECORDING:
            pixmap = self._icon_listening
        elif self._state == AppState.PROCESSING:
            pixmap = self._icon_processing
        elif self._state == AppState.SUCCESS:
            pixmap = self._icon_success
        else:
            pixmap = self._icon_error

        # Scale the icon to fit the MIC_SIZE area
        scaled = pixmap.scaled(
            MIC_SIZE, MIC_SIZE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        # Center the scaled icon in the MIC_SIZE box
        offset_x = x + (MIC_SIZE - scaled.width()) // 2
        offset_y = y + (MIC_SIZE - scaled.height()) // 2
        p.drawPixmap(offset_x, offset_y, scaled)

    def _paint_idle_content(self, p: QPainter, x: int):
        # Title
        p.setPen(Colors.TEXT_WHITE)
        font = QFont("Segoe UI", 12)
        font.setWeight(QFont.Weight.DemiBold)
        p.setFont(font)
        p.drawText(x, 20, 150, 20, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Ready")

        # Subtitle
        p.setPen(Colors.TEXT_MUTED)
        font.setPointSize(9)
        font.setWeight(QFont.Weight.Normal)
        p.setFont(font)
        p.drawText(x, 40, 150, 16, Qt.AlignmentFlag.AlignLeft, "Click to start")

    def _paint_recording_content(self, p: QPainter, x: int):
        # Title + timer
        p.setPen(Colors.TEXT_WHITE)
        font = QFont("Segoe UI", 12)
        font.setWeight(QFont.Weight.DemiBold)
        p.setFont(font)
        p.drawText(x, 14, 120, 20, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Listening...")

        mins = self._recording_seconds // 60
        secs = self._recording_seconds % 60
        p.setPen(Colors.TEXT_BLUE)
        font.setPointSize(10)
        p.setFont(font)
        p.drawText(x + 120, 14, 60, 20, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"{mins:02d}:{secs:02d}")

        # Waveform bars
        p.setPen(Qt.PenStyle.NoPen)
        bar_y_center = 50
        for i in range(20):
            bx = x + i * 7
            if bx > PILL_WIDTH - 60:
                break
            height = 4 + 12 * abs(math.sin((i + self._anim_offset * 0.15) * 0.6))
            by = bar_y_center - height / 2
            p.setBrush(QBrush(Colors.WAVE_BLUE))
            p.drawRoundedRect(QRectF(bx, by, 3, height), 1.5, 1.5)

    def _paint_processing_content(self, p: QPainter, x: int):
        # Title + timer
        p.setPen(Colors.TEXT_WHITE)
        font = QFont("Segoe UI", 12)
        font.setWeight(QFont.Weight.DemiBold)
        p.setFont(font)
        p.drawText(x, 14, 150, 20, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Transcribing...")

        mins = self._recording_seconds // 60
        secs = self._recording_seconds % 60
        p.setPen(Colors.TEXT_PURPLE)
        font.setPointSize(10)
        p.setFont(font)
        p.drawText(x + 130, 14, 60, 20, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"{mins:02d}:{secs:02d}")

        # Moving dots
        p.setPen(Qt.PenStyle.NoPen)
        dot_y = 50
        for i in range(20):
            dx = x + i * 8
            if dx > PILL_WIDTH - 60:
                break
            phase = (self._anim_offset * 0.08 + i * 0.3)
            scale = 0.5 + 0.7 * max(0, math.sin(phase))
            alpha = int(76 + 179 * max(0, math.sin(phase)))
            color = QColor(Colors.DOT_PURPLE)
            color.setAlpha(alpha)
            p.setBrush(QBrush(color))
            size = 5 * scale
            p.drawEllipse(QRectF(dx, dot_y - size / 2, size, size))

    def _paint_success_content(self, p: QPainter, x: int):
        # Title
        p.setPen(Colors.TEXT_WHITE)
        font = QFont("Segoe UI", 12)
        font.setWeight(QFont.Weight.DemiBold)
        p.setFont(font)
        p.drawText(x, 20, 180, 20, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Inserted")

        # Subtitle
        p.setPen(Colors.TEXT_GREEN)
        font.setPointSize(9)
        font.setWeight(QFont.Weight.Normal)
        p.setFont(font)
        p.drawText(x, 40, 180, 16, Qt.AlignmentFlag.AlignLeft, "Copied to clipboard")

    def _paint_error_content(self, p: QPainter, x: int):
        # Title
        p.setPen(Colors.TEXT_RED)
        font = QFont("Segoe UI", 12)
        font.setWeight(QFont.Weight.DemiBold)
        p.setFont(font)
        p.drawText(x, 20, 180, 20, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Error")

        # Subtitle
        p.setPen(Colors.TEXT_RED_LIGHT)
        font.setPointSize(9)
        font.setWeight(QFont.Weight.Normal)
        p.setFont(font)
        p.drawText(x, 40, 180, 16, Qt.AlignmentFlag.AlignLeft, "Transcription failed")

    def _paint_right_button(self, p: QPainter):
        """Draw right-side buttons. 44px to match HTML widget-spinner (mic is 48px)."""
        btn_size = 44
        btn_y = (PILL_HEIGHT - btn_size) // 2
        # Right edge position — aligns X with pause button in recording state
        right_x = PILL_WIDTH - btn_size - 12

        if self._state == AppState.IDLE:
            # Two buttons: settings gear + X close
            close_x = right_x
            gear_x = close_x - btn_size - 6

            # Settings gear background + SVG icon
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(Colors.SPINNER_BG))
            p.drawEllipse(QRectF(gear_x, btn_y, btn_size, btn_size))

            # Render settings SVG (inset by 10px for padding)
            icon_pad = 10
            icon_rect = QRectF(gear_x + icon_pad, btn_y + icon_pad,
                              btn_size - icon_pad * 2, btn_size - icon_pad * 2)
            self._svg_settings.render(p, icon_rect)

            # Power/shutdown background + SVG icon
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(Colors.SPINNER_BG))
            p.drawEllipse(QRectF(close_x, btn_y, btn_size, btn_size))

            # Render power SVG
            icon_rect = QRectF(close_x + icon_pad, btn_y + icon_pad,
                              btn_size - icon_pad * 2, btn_size - icon_pad * 2)
            self._svg_power.render(p, icon_rect)

        elif self._state == AppState.RECORDING:
            # Pause icon
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(Colors.SPINNER_BG))
            p.drawEllipse(QRectF(right_x, btn_y, btn_size, btn_size))
            cx, cy = right_x + btn_size // 2, btn_y + btn_size // 2
            p.setBrush(QBrush(Colors.WAVE_BLUE))
            p.drawRoundedRect(QRectF(cx - 7, cy - 9, 5, 18), 1.5, 1.5)
            p.drawRoundedRect(QRectF(cx + 2, cy - 9, 5, 18), 1.5, 1.5)

        elif self._state == AppState.PROCESSING:
            # Spinning loader
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(Colors.SPINNER_BG))
            p.drawEllipse(QRectF(right_x, btn_y, btn_size, btn_size))
            cx, cy = right_x + btn_size // 2, btn_y + btn_size // 2
            p.setPen(QPen(Colors.DOT_PURPLE, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.setBrush(Qt.BrushStyle.NoBrush)
            start_angle = int(self._anim_offset * 12) * 16
            p.drawArc(QRect(cx - 10, cy - 10, 20, 20), start_angle, 220 * 16)

        elif self._state == AppState.SUCCESS:
            pass  # No right button

        elif self._state == AppState.ERROR:
            # Copy icon
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(Colors.SPINNER_BG))
            p.drawEllipse(QRectF(right_x, btn_y, btn_size, btn_size))
            icon_pad = 10
            icon_rect = QRectF(right_x + icon_pad, btn_y + icon_pad,
                              btn_size - icon_pad * 2, btn_size - icon_pad * 2)
            self._svg_copy.render(p, icon_rect)

    # --- Interaction ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._drag_started = False
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self._drag_started = True
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self._drag_started:
            pos = event.position().toPoint()

            if self._state == AppState.IDLE:
                if self._power_rect().contains(pos):
                    self.exit_clicked.emit()
                    return
                if self._settings_rect().contains(pos):
                    self.settings_clicked.emit()
                    return
            elif self._state == AppState.ERROR:
                if self._copy_rect().contains(pos):
                    self.copy_error_clicked.emit()
                    return

            self.clicked.emit()
            event.accept()
