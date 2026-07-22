import os
import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from app.application import Voice2TextApp

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

# assets/ is bundled inside the exe (PyInstaller --add-data) and extracted
# to sys._MEIPASS at runtime; __file__ resolves correctly there too.
_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def main():
    qt_app = QApplication(sys.argv)
    qt_app.setQuitOnLastWindowClosed(False)

    icon_path = os.path.join(_ASSETS_DIR, "icons", "hum.ico")
    qt_app.setWindowIcon(QIcon(icon_path))

    app = Voice2TextApp(qt_app)
    sys.exit(app.run())


if __name__ == "__main__":
    main()
