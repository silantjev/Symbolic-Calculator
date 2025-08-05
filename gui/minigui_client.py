# Mini-GUI version: application for launch

import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication # pylint: disable=wildcard-import, unused-wildcard-import

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from web.calc_client import CalcClient
from core.logger import make_logger
from gui.minigui import MainWin


def main(log_file=True, log_console=True, url=None):
    app = QApplication(sys.argv)  # create application
    logger = make_logger(name="minigui_client", file=log_file, console=log_console)
    if url is None:
        calc = CalcClient(logger=logger)
    else:
        calc = CalcClient(base_url=url, logger=logger)
    win = MainWin(calc)
    win.show()
    sys.exit(app.exec_())  # execute the application


if __name__ == '__main__':
    main()
