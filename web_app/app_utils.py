import re
import os
import sys
from pathlib import Path

FILEDIR = Path(__file__).resolve().parent
ROOT = FILEDIR.parent
sys.path.insert(0, str(ROOT))

from core.calculator import Calculator
from core.logger import make_logger
from core.session_storage import JSONStorage, StateManager


class Sessions:
    UUID_THRESHOLD = 1_000_000
    def __init__(self):
        console_logging = os.environ.get("CONSOLE_LOGGING", "yes")
        file_logging = os.environ.get("FILE_LOGGING", "yes")
        log_console = (console_logging != "no")
        log_file = (file_logging != "no")
        self.logger = make_logger(name="web", console=log_console, file=log_file)

        conf_path = os.environ.get("CONF_PATH", "")
        storage = JSONStorage(logger=self.logger, json_path=conf_path)
        self.state_manager = StateManager(storage)
        self.calcs = {} # dict[int, Calculator]

    def get_calc(self, uu_id: int):
        if uu_id not in self.calcs:
            calc = Calculator(logger=self.logger)
            if uu_id <= self.UUID_THRESHOLD:
                self.state_manager.load_state(calc, uu_id)
            self.calcs[uu_id] = calc

        return self.calcs[uu_id]

    def save(self):
        for uu_id, calc in self.calcs.items():
            if (uu_id <= self.UUID_THRESHOLD):
                self.state_manager.save_state(calc, uu_id)

class HtmlGenetator:
    def __init__(self, template_path, error_template_path, info_template_path):
        assert template_path.is_file(), f'File {template_path} not found'
        assert error_template_path.is_file(), f'File {error_template_path} not found'
        assert info_template_path.is_file(), f'File {error_template_path} not found'
        with open(template_path, 'r', encoding='utf8') as f:
            self.template = f.read()
        with open(error_template_path, 'r', encoding='utf8') as f:
            self.error_template = f.read()
        with open(info_template_path, 'r', encoding='utf8') as f:
            self.info_template = f.read()
        self.url_reg_expr = re.compile(r'(https?://[\w\-./]+)')

    def get_html(self, calc):
        return self.template.format(
                expr=calc.expr,
                se=calc.get_nice(),
                sec=str(calc.sec),
            )

    def show_error(self, expr, error):
        return self.error_template.format(
                expr=expr,
                error=error,
            )

    def show_info(self, calc):
        html_text = self.info_template.format(text=calc.get_help_text())
        return re.sub(self.url_reg_expr, r'<a href="\1">\1</a>', html_text)


