import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PySide6.QtWidgets import QApplication
from aied.gui.main_window import MainWindow
from aied.gui.styles import APP_STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AI Engineering Designer")
    app.setStyleSheet(APP_STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
