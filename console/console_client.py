import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from console.console_calc import CCalculator
from core.logger import make_logger
from web.calc_client import CalcClient

def main(log_file=True, log_console=False, url=None):
    logger = make_logger(name="console_client", file=log_file, console=log_console)
    if url is None:
        calc = CalcClient(logger=logger)
    else:
        calc = CalcClient(base_url=url, logger=logger)
    ccalc = CCalculator(calc=calc)
    ccalc.main_menu()


if __name__ == '__main__':
    main()

