# Console version for application or client

import sys
from pathlib import Path
from simple_term_menu import TerminalMenu
# from sympy import * # pylint: disable=wildcard-import, unused-wildcard-import

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.session_storage import JSONStorage, StateManager, ClientStateManager
from core.calculator import Calculator
from web.calc_client import CalcClient


class CCalculator:
    """ Console version of calculator.
    """

    # Attributes:

    # calc: Union[Calculator, CalcClient]

    def __init__(self, calc, conf_path=""):
        """ expr: SymPy expression of the string type """
        self.calc = calc
        if isinstance(calc, Calculator):
            storage = JSONStorage(json_path=conf_path)
            self.state_manager = StateManager(storage=storage, logger=self.calc.logger)
        elif isinstance(calc, CalcClient):
            self.state_manager = ClientStateManager()
        else:
            raise TypeError(f"Acceptable types of calc are Calculator and CalcClient, not {type(calc)}")

    def main_menu(self, expr=None):
        """ Запуск приложения """
        self.state_manager.load_state(self.calc)
        if expr is not None:
            self.calc.set_se(expr)

        while True:
            print('\nТекущее выражение:', self.calc.get_nice())
            subs_string = self.calc.current_values()
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
                'Сохранить состояние',
                'Полная отчистка'
            ]
            terminal_menu = TerminalMenu(menu, clear_menu_on_exit=True)
            ch = terminal_menu.show()
            print()

            if ch == 0 or ch is None:
                self.state_manager.save_state(self.calc)
                break
            
            if ch == 1:
                self.new_expr()

            elif ch == 2:
                self.evaluate()

            elif ch == 3:
                c = True
                while c:
                    c = self.change_values()

            elif ch == 4:
                c = True
                while c:
                    c = self.delete_values()
            
            elif ch == 5:
                self.delete_values(delete_all=True)

            elif ch == 6:
                self.show_help()

            elif ch == 7:
                self.change_options()

            elif ch == 8:
                self.state_manager.save_state(self.calc)

            elif ch == 9:
                self.calc.clear_all()


    def change_options(self):
        print('Опции:')
        for k, v in self.calc.get_options().items():
            print(f'\t{self.calc.get_explanations()[k]}: {k} = {v}')
            val = input('Введите новое значение опции\n(для отмены нажмите Enter): ')
            if val:
                ok = self.calc.set_option(k, val)
                if not ok:
                    print(f"Ошибка присвоения {k} = {v}")

    def show_help(self):
        print(self.calc.get_help_text())
        input('Нажмите Enter')


    def change_values(self):
        """ Reruns True if it should be called once more """
        current, lines = self.calc.get_variables()
        text = '\n'.join(lines)
        print(text)
        while True:
            choice = input('Введите имя переменной \n(чтобы вернуться в меню нажмите Enter): ')
            choice = choice.strip()
            if choice == '':
                return False
            if choice not in current:
                print('Предупреждение: переменной нет в текущем выражении')
                if choice not in self.calc.get_var_names():
                    print(f'Предупреждение: переменной {choice} нет и среди заданных переменных')
                    expr =  input(f'Введите значение новой переменной {choice}\n(для отмены нажмите Enter): ')
                else:
                    expr =  input(f'Введите значение переменной {choice}\n(для отмены нажмите Enter): ')
                if expr == '':
                    continue
            else:
                expr =  input('Введите значение переменной\n(для отмены нажмите Enter): ')
            try:
                self.calc.set_value(choice, expr)
            except (AssertionError, ValueError, TypeError, KeyError) as exc:
                print(f'Ошибка: {exc}')
            return True

    def delete_values(self, delete_all=False):
        """ Returns True if it should be called once more """
        if not self.calc.get_var_names():
            print('Ни одна переменная не задана')
            input('Нажмите Enter')
            return False
        
        _, lines = self.calc.get_variables(include_unset=False)
        print('\n'.join(lines))

        if delete_all:
            while True:
                choice = input('Удалить значения всех переменных (y/n — да/нет): ')
                if choice == '':
                    continue
                ch = choice[0]
                if ch in 'yд':
                    self.calc.delete_all_values()
                    return False
                if ch in 'nн':
                    return False
        else:
            while True:
                choice = input('Введите имя переменной для удаления\n(для отмены нажмите Enter): ')
                choice = choice.strip()
                if choice == '':
                    return False
                if choice in self.calc.get_var_names():
                    self.calc.delete_value(choice)
                    return True
                print(f'Переменная {choice} отсутствует')

    def evaluate(self):
        sec = self.calc.evaluate()
        subs_string = self.calc.current_values()
        if subs_string:
            subs_string = ', где ' + subs_string
        print(f'{self.calc.get_se()} = {sec}' + subs_string)
        if str(sec).find('zoo') != -1 or str(sec).find('nan') != -1:
            print('Деление на 0')
            input('Нажмите Enter')
            return

        while True:
            choice = input('Сохранить как текущее (y/n — да/нет): ')
            if choice == "":
                break
            ch = choice[0]

            if ch in 'yд':
                self.calc.set_se(sec)
                break
            if ch in 'nнq':
                break

    def new_expr(self):
        while True:
            expr = input('Введите выражение\n(для отмены нажмите Enter): ')
            if expr == '':
                break

            text = self.calc.set_new_expr(expr)

            if text == "":
                break

            print(text)  # Error — let's repeat


