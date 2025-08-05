from pathlib import Path
import logging

ROOT = Path(__file__).resolve().parents[1]
LOGDIR = ROOT / 'logs'

def make_logger(name, file=True, console=True, level=logging.INFO, log_dir=LOGDIR):
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(level)
    if file:
        log_dir = Path(log_dir)
        if not log_dir.is_dir():
            log_dir.mkdir()
        log_dir.mkdir(exist_ok=True)
        fh = logging.FileHandler(log_dir/ f'{name}.log', 'a')
        datefmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt=datefmt)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    if console:
        sh = logging.StreamHandler() # console handler
        datefmt = '%H:%M:%S'
        formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt=datefmt)
        sh.setFormatter(formatter)
        logger.addHandler(sh)
    return logger

