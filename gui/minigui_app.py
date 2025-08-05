# Mini-GUI version: application for launch

import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication # pylint: disable=wildcard-import, unused-wildcard-import

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.calculator import Calculator
from core.logger import make_logger
from gui.minigui import MainWin


def main(log_console=True, log_file=True):
    app = QApplication(sys.argv)  # create application
    logger = make_logger(name="minigui", file=log_file, console=log_console)
    calc = Calculator(logger=logger)
    win = MainWin(calc)
    win.show()
    sys.exit(app.exec_())  # execute the application


if __name__ == '__main__':
    main()
