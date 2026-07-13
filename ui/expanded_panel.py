import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QFrame, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from ui import theme
from app.constants import MODELS_DIR


class ExpandedPanel(QWidget):
    """Expanded settings panel that drops below the pill, encapsulating it."""

    model_changed = Signal(str)
    language_changed = Signal(str)
    closed = Signal()

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_ui()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedWidth(360)
        self.setStyleSheet(self._stylesheet())

    def _stylesheet(self):
        return f"""
        QWidget#panel {{
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 16px;
        }}
        QLabel {{
            color: {theme.TEXT_PRIMARY};
            font-family: "{theme.FONT_FAMILY}";
            background: transparent;
        }}
        QLabel#sectionLabel {{
            color: #64748b;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        QComboBox {{
            background-color: #0f172a;
            color: {theme.TEXT_PRIMARY};
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 8px 12px;
            font-family: "{theme.FONT_FAMILY}";
            font-size: 13px;
        }}
        QComboBox:focus {{
            border-color: #3b82f6;
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox QAbstractItemView {{
            background-color: #0f172a;
            color: {theme.TEXT_PRIMARY};
            border: 1px solid #334155;
            selection-background-color: #1e293b;
        }}
        QFrame#separator {{
            background-color: #334155;
        }}
        QLabel#hint {{
            color: #475569;
            font-size: 11px;
        }}
        """

    def _setup_ui(self):
        container = QWidget(self)
        container.setObjectName("panel")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # Model section
        model_label = QLabel("MODEL")
        model_label.setObjectName("sectionLabel")
        layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self._populate_models()
        self.model_combo.currentTextChanged.connect(self.model_changed.emit)
        layout.addWidget(self.model_combo)

        # Language section
        lang_label = QLabel("LANGUAGE")
        lang_label.setObjectName("sectionLabel")
        layout.addWidget(lang_label)

        self.lang_combo = QComboBox()
        languages = [
            ("English", "en"),
            ("Auto Detect", "auto"),
            ("Hindi", "hi"),
            ("Spanish", "es"),
            ("French", "fr"),
            ("German", "de"),
            ("Japanese", "ja"),
        ]
        for name, code in languages:
            self.lang_combo.addItem(name, code)
        self.lang_combo.currentIndexChanged.connect(
            lambda idx: self.language_changed.emit(self.lang_combo.itemData(idx))
        )
        layout.addWidget(self.lang_combo)

        # Hint
        hint = QLabel("Click outside or settings icon to collapse")
        hint.setObjectName("hint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        # Set container to fill
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(container)

        self.adjustSize()

    def _populate_models(self):
        """Find available .bin model files."""
        self.model_combo.clear()
        if os.path.isdir(MODELS_DIR):
            for f in sorted(os.listdir(MODELS_DIR)):
                if f.endswith(".bin"):
                    self.model_combo.addItem(f)

        idx = self.model_combo.findText("ggml-base.bin")
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)

    def show_below(self, pill_widget: QWidget):
        """Position panel just below the pill (attached to it)."""
        pill_pos = pill_widget.pos()
        pill_w = pill_widget.width()
        panel_w = self.width()
        # Center horizontally under the pill
        x = pill_pos.x() + (pill_w - panel_w) // 2
        y = pill_pos.y() + pill_widget.height() + 4
        self.move(x, y)
        self.show()

    def mousePressEvent(self, event):
        self.closed.emit()
        self.hide()
