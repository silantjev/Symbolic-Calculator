# Symbolic calculator 2.0
# Console version

import sys
from pathlib import Path
from simple_term_menu import TerminalMenu
from sympy import * # pylint: disable=wildcard-import, unused-wildcard-import

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.calculator import Calculator
from core.logger import make_logger


class CCalculator(Calculator):
    """ Console version of calculator.
    The inherited method 'symbolic_expr' is used.
    """

    # Attributes:

    # se: current expression as a SymPy object

    # values: is a dict of their values {'x': value}, where value is a number
    # (if a variable 'x' does not have a value, then we output it as an abstract variable)

    # options: values of options

    # explanations: description of options (a constant)

    # Options:
    # digits: means the number of digits, which are shown by evaluation

    def __init__(self, expr='0', logger=None):
        """ expr: SymPy expression of the string type """
        super().__init__(expr, logger=logger)

    def main_menu(self, expr=None):
        if expr is not None:
            expr = str(expr)
            self.se = parse_expr(expr)

        while True:
            print('\nТекущее выражение:', self.get_nice())
            subs_string = self.current_values()
            if subs_string:
                print('Значения переменных: ' + subs_string)
            print()

            menu = [
                'Выйти',
                'Ввести новое выражение',
                'Вычислить текущее выражение',
                'Задать значение переменной',
                'Удалить значение переменной',
                'Удалить значение всех переменных',
                'Показать справку',
                'Изменить опции',
            ]
            terminal_menu = TerminalMenu(menu, clear_menu_on_exit=True)
            ch = terminal_menu.show()
            print()

            if ch == 0 or ch is None:
                break
            
            if ch == 1:
                self.new_expr()

            if ch == 2:
                self.evaluate()

            if ch == 3:
                c = True
                while c:
                    c = self.change_values()

            if ch == 4:
                c = True
                while c:
                    c = self.delete_values()
            
            if ch == 5:
                self.delete_values(delete_all=True)

            if ch == 6:
                self.show_help()

            if ch == 7:
                self.change_options()


    def change_options(self):
        print('Опции:')
        for k, v in self.options.items():
            print(f'\t{self.explanations[k]}: {k} = {v}')
            val = input('Введите новое значение опции\n(для отмены нажмите Enter): ')
            if val:
                try:
                    val = int(val)
                    if val > 1:
                        self.options[k] = val
                except TypeError:
                    pass

    def show_help(self):
        print(self.get_help_text())
        input('Нажмите Enter')


    def change_values(self):
        """ Reruns True if it should be called once more """
        current, lines = self.get_variables()
        text = '\n'.join(lines)
        print(text)
        while True:
            choice = input('Введите имя переменной \n(чтобы вернуться в меню нажмите Enter): ')
            choice = choice.strip()
            if choice == '':
                return False
            if choice not in current:
                print('Предупреждение: переменной нет в текущем выражении')
                if choice not in self.values.keys():
                    print(f'Предупреждение: переменной {choice} нет и среди заданных переменных')
                    expr =  input(f'Введите значение новой переменной {choice}\n(для отмены нажмите Enter): ')
                else:
                    expr =  input(f'Введите значение переменной {choice}\n(для отмены нажмите Enter): ')
                if expr == '':
                    continue
            else:
                expr =  input('Введите значение переменной\n(для отмены нажмите Enter): ')
            try:
                value = self.symbolic_expr(expr)
                if value == 'Error':
                    raise TypeError('Неизвестна ошибка')
                self.values[choice] = value
                return True
            except (AssertionError, ValueError, TypeError, KeyError) as exc:
                print(f'Ошибка: {exc}')
                return True


    def delete_values(self, delete_all=False):
        """ Reruns True if it should be called once more """
        if not self.values:
            print('Ни одна переменная не задана')
            input('Нажмите Enter')
            return False
        
        _, lines = self.get_variables(include_unset=False)
        print('\n'.join(lines))

        if delete_all:
            while True:
                choice = input('Удалить значения всех переменных (y/n — да/нет): ')
                if choice == '':
                    continue
                else:
                    ch = choice[0]
                if ch in 'yд':
                    self.values = {}
                    return False
                elif ch in 'nн':
                    return False
        else:
            while True:
                choice = input('Введите имя переменной для удаления\n(для отмены нажмите Enter): ')
                choice = choice.strip()
                if choice == '':
                    return False
                if choice in self.values.keys():
                    self.values.pop(choice)
                    return True
                else:
                    print(f'Переменная {choice} отсутствует')

    def evaluate(self):
        sec = super().evaluate()
        subs_string = self.current_values()
        if subs_string:
            subs_string = ', где ' + subs_string
        print(f'{self.se} = {sec}' + subs_string)
        if str(sec).find('zoo') != -1 or str(sec).find('nan') != -1:
            print('Деление на 0')
            input('Нажмите Enter')
            return

        while True:
            choice = input('Сохранить как текущее (y/n — да/нет): ')
            if choice == '':
                break
            else:
                ch = choice[0]

            if ch in 'yд':
                self.se = parse_expr(str(sec))
                break
            elif ch in 'nнq':
                break

    def new_expr(self):
        while True:
            expr = input('Введите выражение\n(для отмены нажмите Enter): ')
            if expr == '':
                break

            text = self.set_new_expr(expr)

            if text == None:
                break

            print(text)

def main(log_file=True, log_console=True):
    logger = make_logger(name="console", file=log_file, console=log_console)
    ccalcul = CCalculator(logger=logger)
    expr = '0'
    ccalcul.main_menu(expr)


if __name__ == '__main__':
    main()


