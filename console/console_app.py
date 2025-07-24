# Symbolic calculator 3.0
# Console version

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.calculator import Calculator
from core.logger import make_logger
from console.console_calc import CCalculator


def main(log_console=False, log_file=True):
    logger = make_logger(name="console", file=log_file, console=log_console)
    calc = Calculator(logger=logger)
    ccalc = CCalculator(calc=calc)
    expr = '0'
    ccalc.main_menu(expr)


if __name__ == '__main__':
    main()


