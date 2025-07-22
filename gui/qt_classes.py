from PyQt5.QtWidgets import * # pylint: disable=wildcard-import, unused-wildcard-import
from PyQt5.QtCore import Qt
# from sympy import *

class QLE(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, e):
        k = e.key()

        if QApplication.keyboardModifiers() == Qt.AltModifier:
            if k == Qt.Key_A:
                self.home(False)
            
            if k == Qt.Key_E:
                self.end(False)

            return

        super().keyPressEvent(e)



class Vars(QDialog):

    def __init__(self, parent, calc):
        self.calc = calc
        super().__init__(parent=parent)
        self.setWindowTitle('Variables')
        current = calc.get_current_variables()
        current = list(current)
        current.sort()
        other = calc.get_other_variables()
        other = list(other)
        other.sort()
        
        self.resize(450, 300)

        label_current = QLabel(self)
        label_current.setText(f'Переменные текущего выражения: {current}')
        x = 10
        y = 10
        label_current.move(x, y)
        step = 30
        labels = {}
        self.inputs = inputs = {}

        for v in current:
            y += step
            labels[v] = QLabel(self)
            labels[v].setText(str(v) + ' : ')
            labels[v].move(x, y)

            value = calc.values.get(v, '')
            inputs[v] = QLE(value, self)
            inputs[v].move(x + 30, y)
            inputs[v].resize(350, 25)
            inputs[v].returnPressed.connect(self.change_value(v))

    def change_value(self, v):
        def func():
            expr = self.inputs[v].text()
            if expr.strip == '':
                return
            try:
                value = self.calc.symbolic_expr(expr)
            except AssertionError:
                QMessageBox.warning(self, 'Warning', 'Не корректное выражение!')
                return
            if value == 'Error':
                QMessageBox.warning(self, 'Warning', 'Не корректное выражение!')
                return

            self.calc.values[v] = value

        return func

