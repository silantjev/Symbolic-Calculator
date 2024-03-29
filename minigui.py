# Symbolic calculator 2.0
# Mini-GUI version
# Under development...

# import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from sympy import * # ?

# from qt_classes import Vars
from qt_classes import QLE
from gen_calc import Calculator


class MainMenu(QDialog):
    """ Realises gui interface """
    def __init__(self, calc):
        self.calc = calc # an instance of the class Calculator
        super().__init__()
        self.setWindowTitle('Symbolic Calculator')
        self.resize(450, 300)

        self.input_text = QLE(calc.expr, self)
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

        self.se_text = QLE(str(calc.se), self)
        self.se_text.move(50, 80)
        self.se_text.resize(350, 25)
        self.se_text.editingFinished.connect(self.eval_down)

        self.btn_eval = QPushButton('↓ вычислить', self)
        self.btn_eval.move(70, 110)
        self.btn_eval.clicked.connect(self.eval_down)

        self.btn_up = QPushButton('↑ перебросить', self)
        self.btn_up.move(250, 110)
        self.btn_up.clicked.connect(self.sec_up)

        self.sec_text = QLE(str(calc.sec), self)
        self.sec_text.move(50, 140)
        self.sec_text.resize(350, 25)

        # self.btn_var = QPushButton('Переменные', self)
        # self.btn_var.move(70, 170)
        # self.btn_var.clicked.connect(self.vars)

    def parse_down(self):
        """ parse the input expression to 'se' and evaluate it to 'sec' """
        expr = self.input_text.text()
        if self.calc.expr == expr:
            return
        self.calc.expr = expr

        text = self.calc.set_new_expr(expr)
        if text is not None:
            QMessageBox.warning(self, 'Warning', text)
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
        expr = str(self.calc.se)
        self.calc.expr = expr
        self.input_text.setText(expr)

    def sec_up(self):
        """ put 'sec' to 'se' """
        sec_text = str(self.calc.sec)
        self.calc.se = parse_expr(sec_text)
        self.se_text.setText(sec_text)

    def eval_down(self):
        """ Evaluates 'se' to 'sec' """
        se_new_text = self.se_text.text()
        if se_new_text != str(self.calc.se):
            se_new = self.calc.symbolic_expr(se_new_text)
            self.calc.se = se_new

        sec = self.calc.evaluate()
        if str(sec).find('zoo') != -1 or str(sec).find('nan') != -1:
            QMessageBox.warning(self, 'Warning', 'Деление на 0')
        else:
            self.calc.sec = sec
            self.sec_text.setText(str(sec))

    # def vars(self):
        # var_dialog = Vars(parent=self, calc=self.calc)
        # var_dialog.setWindowTitle('Variables')
        # var_dialog.show()



def main():
    expr = '0'
    app = QApplication(sys.argv)  # create application
    calc = Calculator(expr)
    menu = MainMenu(calc)
    menu.show()
    sys.exit(app.exec_())  # execute the application


if __name__ == '__main__':
    main()
