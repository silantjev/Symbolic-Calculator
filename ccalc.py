# Symbolic calculator 2.0
# Console version

from symbolic import Symbolic

import os
from sympy import *


class CCalculator(Symbolic):
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

    def __init__(self, expr='0'):
        """ expr: SymPy expression of the string type """

        expr = str(expr)  # For the case if 'expr' is a SymPy object 
        self.se = parse_expr(expr)  # SymPy parser
        self.variables = {}
        self.values = {}
        self.options = {'digits': 8}
        self.explanations = {'digits': 'Точность вычисления в количестве цифр'}

    def current_values(self):
        current = {var.name for var in self.se.free_symbols}
        subs_strings= [f'{k} = {v}' for k, v in self.values.items() if k in current]
        subs_string = ', '.join(subs_strings)
        return subs_string

    def main_menu(self, expr=None):
        if expr is not None:
            expr = str(expr)
            self.se = parse_expr(expr)

        while True:
            print('\nТекущее выражение:', self.se)
            subs_string = self.current_values()
            if subs_string:
                print('Значения переменных: ' + subs_string)
            print()
            print('Меню:\n')
            print('q — Выйти')
            print('n — Ввести новое выражение')
            print('v — Задать значение переменной')
            print('d — Удалить значение переменной')
            print('a — Удалить значение всех переменных')
            print('e — Вычислить текущее выражение')
            print('h — Показать справку')
            print('o — Изменить опции')

            choice = input('Ваш выбор: ')
            print()
            if choice == '':
                continue
            else:
                ch = choice[0]
            
            if ch == 'q':
                break
            
            if ch == 'n':
                self.new_expr()

            if ch == 'e':
                self.evaluate()

            if ch == 'v':
                c = self.change_values()
                while c:
                    c = self.change_values()

            if ch == 'd':
                c = self.delete_values()
                while c:
                    c = self.delete_values()
            
            if ch == 'a':
                self.delete_values(delete_all=True)

            if ch == 'h':
                self.show_help()

            if ch == 'o':
                self.change_options()


    def change_options(self):
        print('Опции:')
        for k, v in self.options.items():
            print(f'\t{self.explanations[k]}: {k} = {v}')
            val = input('Введите новое значение опции (пустая строка — пропустить): ')
            if val:
                try:
                    val = int(val)
                    if val > 1:
                        self.options[k] = val
                except:
                    pass

    def show_help(self):
        dir_path = os.path.dirname(__file__)
        path = os.path.join(dir_path, 'help_rus.txt')
        with open(path, 'r', encoding='utf-8') as file:
            print(file.read())
        input('Нажмите "ввод"')


    def change_values(self):
        current = {var.name for var in self.se.free_symbols}
        current_set = current & set(self.values.keys())
        current_unset = current - set(self.values.keys())
        other_set = set(self.values.keys()) - current
        if current:
            print('Переменные в текущем выражении:')
        if current_set:
            print('\tзаданные:')
        for var in current_set:
            print(f'\t\t{var} = {self.values[var]}')
        if current_unset:
            print('\tсвободные:')
        for var in current_unset:
            print(f'\t\t{var}')
        if other_set:
            print('Другие переменные:')
        for var in other_set:
            print(f'\t\t{var} = {self.values[var]}')
        while True:
            choice = input('Введите имя переменной (пустая строка — вернуться в меню): ')
            choice = choice.strip()
            if choice == '':
                return False
            if choice not in current:
                print('Предупреждение: переменной нет в текущем выражении')
                if choice not in self.values.keys():
                    print('Предупреждение: переменной нет и среди заданных переменных')
                    expr =  input('Введите значение новой переменной (пустая строка — отмена): ')
                else:
                    expr =  input('Введите значение переменной (пустая строка — отмена): ')
                if expr == '':
                    continue
            else:
                expr =  input('Введите значение переменной (пустая строка — оставить свободной): ')
            try:
                value = self.symbolic_expr(expr)
                self.values[choice] = value
                return True
            except:
                print('Error')
                return True


    def delete_values(self, delete_all=False):
        if not self.values:
            print('Ни одна переменная не задана')
            input('Нажмите "ввод"')
            return False
        current = {var.name for var in self.se.free_symbols}
        current_set = current & set(self.values.keys())
        other_set = set(self.values.keys()) - current
        print('Заданные переменные:')
        if current_set:
            print('\tПеременные в текущем выражении:')
        for var in current_set:
            print(f'\t\t{var} = {self.values[var]}')
        if other_set:
            print('\tДругие переменные:')
        for var in other_set:
            print(f'\t\t{var} = {self.values[var]}')
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
                choice = input('Введите имя переменной для удаления (пустая строка — отмена): ')
                choice = choice.strip()
                if choice == '':
                    return False
                if choice in self.values.keys():
                    self.values.pop(choice)
                    return True
                else:
                    print(f'Переменная {choice} отсутствует')



    def evaluate(self):
        subs_list = [(k,v) for k, v in self.values.items()]
        subs_string = self.current_values()
        if subs_string:
            subs_string = ', где ' + subs_string
        sec = self.se.subs(subs_list)
        digits = self.options['digits']
        sec = sec.evalf(digits)
        print(f'{self.se} = {sec}' + subs_string)
        if str(sec).find('zoo') != -1 or str(sec).find('nan') != -1:
            print('Деление на 0')
            input('Нажмите "ввод"')
            return

        while True:
            choice = input('Сохранить как текущее (y/n — да/нет): ')
            if choice == '':
                continue
            else:
                ch = choice[0]

            if ch in 'yд':
                self.se = sec
                break
            elif ch in 'nн':
                break


    def new_expr(self):
        se_new = 'Error'
        while se_new == 'Error':
            expr = input('Введите выражение (пустая строка — отмена): ')
            expr = expr.replace('_', '(' + str(self.se) + ')')
            # print('Новое выражение:', expr)
            if expr:
                se_new = self.symbolic_expr(expr)
            else:
                return

        self.se =  se_new

if __name__ == '__main__':
    expr = '0'
    ccalcul = CCalculator()
    ccalcul.main_menu(expr)


