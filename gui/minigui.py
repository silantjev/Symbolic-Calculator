# Mini-GUI version
# Under development...

import sys
from pathlib import Path
from PyQt5.QtWidgets import * # pylint: disable=wildcard-import, unused-wildcard-import

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.session_storage import JSONStorage, StateManager, ClientStateManager
from core.calculator import Calculator
from web.calc_client import CalcClient
from gui.qt_classes import QLE


class MainWin(QDialog):
    """ Realises gui interface """
    def __init__(self, calc, conf_path=""):
        self.calc = calc
        if isinstance(self.calc, Calculator):
            storage = JSONStorage(logger=self.calc.logger, json_path=conf_path)
            self.state_manager = StateManager(storage=storage)
            self.state_manager.load_state(self.calc)
        elif isinstance(self.calc, CalcClient):
            self.state_manager = ClientStateManager()
        else:
            raise TypeError(f"Acceptable types of calc are Calculator and CalcClient, not {type(calc)}")

        super().__init__()

        self.setWindowTitle('Symbolic Calculator')
        self.resize(450, 300)

        self.input_text = QLE(calc.get_expr(), self)
        self.input_text.move(50, 20)
        self.input_text.resize(350, 25)
        self.input_text.returnPressed.connect(self.parse_down)
        self.input_text.selectAll()

        self.btn_parse = QPushButton('↓ преобразовать', self)
        self.btn_parse.move(70, 50)
        self.btn_parse.clicked.connect(self.parse_down)

        self.btn_up = QPushButton('↑ перебросить', self)
        self.btn_up.move(250, 50)
        self.btn_up.clicked.connect(self.se_up)

        self.se_text = QLE(str(calc.get_se()), self)
        self.se_text.move(50, 80)
        self.se_text.resize(350, 25)
        self.se_text.editingFinished.connect(self.eval_down)

        self.btn_eval = QPushButton('↓ вычислить', self)
        self.btn_eval.move(70, 110)
        self.btn_eval.clicked.connect(self.eval_down)

        self.btn_up = QPushButton('↑ перебросить', self)
        self.btn_up.move(250, 110)
        self.btn_up.clicked.connect(self.sec_up)

        self.sec_text = QLE(calc.get_sec(), self)
        self.sec_text.move(50, 140)
        self.sec_text.resize(350, 25)

        # self.btn_var = QPushButton('Переменные', self)
        # self.btn_var.move(70, 170)
        # self.btn_var.clicked.connect(self.vars)

    def closeEvent(self, event):
        """ Called when the window are closing """
        self.state_manager.save_state(self.calc)
        super().closeEvent(event)

    def reject(self):
        self.state_manager.save_state(self.calc)
        super().reject()

    def parse_down(self):
        """ parse the input expression to 'se' and evaluate it to 'sec' """
        expr = self.input_text.text()
        if self.calc.get_expr() == expr:
            return
        self.calc.set_expr(expr)

        error = self.calc.set_new_expr(expr)
        if error:
            QMessageBox.warning(self, 'Warning', error)
            return
        # try:
            # se_new = self.calc.symbolic_expr(expr)
        # except (AssertionError, KeyError, TypeError) as exc:
            # QMessageBox.warning(self, 'Warning', f'Не корректное выражение!\n{exc}')
            # return
        # if se_new == 'Error':
            # QMessageBox.warning(self, 'Warning', 'Не корректное выражение!')
            # return
        # self.calc.se = se_new
        # try:
            # se_new = float(se_new)
        # except TypeError:
            # pass
        self.se_text.setText(str(self.calc.get_nice()))
        self.eval_down()

    def se_up(self):
        """ put 'se' to the top line (input) """
        expr = str(self.calc.get_se())
        self.calc.set_expr(expr)
        self.input_text.setText(expr)

    def sec_up(self):
        """ put 'sec' to 'se' """
        sec_text = str(self.calc.get_sec())
        error = self.calc.set_se(sec_text)
        if error:
            QMessageBox.warning(self, 'Warning', error)
            return
        self.se_text.setText(sec_text)

    def eval_down(self):
        """ Evaluates 'se' to 'sec' """
        se_new_text = self.se_text.text()
        if se_new_text != str(self.calc.get_se()):
            error = self.calc.set_se(se_new_text)
            if error:
                QMessageBox.warning(self, 'Warning', error)
                return

        sec = self.calc.evaluate()
        if str(sec).find('zoo') != -1 or str(sec).find('nan') != -1:
            QMessageBox.warning(self, 'Warning', 'Деление на 0')
        else:
            self.calc.set_sec(sec)
            self.sec_text.setText(str(sec))

    # def vars(self):
        # var_dialog = Vars(parent=self, calc=self.calc)
        # var_dialog.setWindowTitle('Variables')
        # var_dialog.show()
