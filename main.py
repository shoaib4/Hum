import sys
import logging
from PySide6.QtWidgets import QApplication

from app.application import Voice2TextApp

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)


def main():
    qt_app = QApplication(sys.argv)
    qt_app.setQuitOnLastWindowClosed(False)

    app = Voice2TextApp(qt_app)
    sys.exit(app.run())


if __name__ == "__main__":
    main()
