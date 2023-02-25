from symbolic import symbolic_expr

import os
from sympy import *

# Global variables:

variables = {}
values = {}
options = {'digits': 8}
explanations = {'digits': 'Точность вычисления в количестве цифр'}

# 'variables' is a dict of variables {'x': sympy.Symbol('x'), ...},
# 'values' is a dict of their values {'x': value}, where value is a number.
# If a variable 'x' does not has a value, then we output it as an abstract variable.

# Options:
# 'digits' means the number of digits, which are shown by evaluation

def current_values(se):
    current = {var.name for var in se.free_symbols}
    subs_strings= [f'{k} = {v}' for k, v in values.items() if k in current]
    subs_string = ', '.join(subs_strings)
    return subs_string

def main_menu(expr = '0'):
    se = parse_expr(expr)
    while True:
        print('\nТекущее выражение:', se)
        subs_string = current_values(se)
        if subs_string:
            print('Значения переменных: ' + subs_string)
        print()
        print('Меню:\n')
        print('q \u2014 Выйти')
        print('n \u2014 Ввести новое выражение')
        print('v \u2014 Задать значение переменной')
        print('d \u2014 Удалить значение переменной')
        print('a \u2014 Удалить значение всех переменных')
        print('e \u2014 Вычислить текущее выражение')
        print('h \u2014 Показать справку')
        print('o \u2014 Изменить опции')

        choice = input('Ваш выбор: ')
        print()
        if choice == '':
            continue
        else:
            ch = choice[0]
        
        if ch == 'q':
            break
        
        if ch == 'n':
            se = new_expr(se)

        if ch == 'e':
            se = evaluate(se)

        if ch == 'v':
            c = change_values(se)
            while c:
                c = change_values(se)

        if ch == 'd':
            c = delete_values(se)
            while c:
                c = delete_values(se)
        
        if ch == 'a':
            delete_values(se, delete_all=True)

        if ch == 'h':
            show_help()

        if ch == 'o':
            change_options()


def change_options():
    global options
    print('Опции:')
    for k, v in options.items():
        print(f'\t{explanations[k]}: {k} = {v}')
        val = input('Введите новое значение опции (пустая строка \u2014 пропустить): ')
        if val:
            try:
                val = int(val)
                if val > 1:
                    options[k] = val
            except:
                pass

def show_help():
    dir_path = os.path.dirname(__file__)
    path = os.path.join(dir_path, 'help_rus.txt')
    with open(path, 'r', encoding='utf-8') as file:
        print(file.read())
    input('Нажмите "ввод"')


def change_values(se):
    global values
    current = {var.name for var in se.free_symbols}
    current_set = current & set(values.keys())
    current_unset = current - set(values.keys())
    other_set = set(values.keys()) - current
    if current:
        print('Переменные в текущем выражении:')
    if current_set:
        print('\tзаданные:')
    for var in current_set:
        print(f'\t\t{var} = {values[var]}')
    if current_unset:
        print('\tсвободные:')
    for var in current_unset:
        print(f'\t\t{var}')
    if other_set:
        print('Другие переменные:')
    for var in other_set:
        print(f'\t\t{var} = {values[var]}')
    while True:
        choice = input('Введите имя переменной (пустая строка \u2014 вернуться в меню): ')
        choice = choice.strip()
        if choice == '':
            return False
        if choice not in current:
            print('Предупреждение: переменной нет в текущем выражении')
            if choice not in values.keys():
                print('Предупреждение: переменной нет и среди заданных переменных')
                expr =  input('Введите значение новой переменной (пустая строка \u2014 отмена): ')
            else:
                expr =  input('Введите значение переменной (пустая строка \u2014 отмена): ')
            if expr == '':
                continue
        else:
            expr =  input('Введите значение переменной (пустая строка \u2014 оставить свободной): ')
        try:
            value = symbolic_expr(expr)
            values[choice] = value
            return True
        except:
            print('Error')
            return True


def delete_values(se, delete_all=False):
    global values
    if not values:
        print('Ни одна переменная не задана')
        input('Нажмите "ввод"')
        return False
    current = {var.name for var in se.free_symbols}
    current_set = current & set(values.keys())
    other_set = set(values.keys()) - current
    print('Заданные переменные:')
    if current_set:
        print('\tПеременные в текущем выражении:')
    for var in current_set:
        print(f'\t\t{var} = {values[var]}')
    if other_set:
        print('\tДругие переменные:')
    for var in other_set:
        print(f'\t\t{var} = {values[var]}')
    if delete_all:
        while True:
            choice = input('Удалить значения всех переменных (y/n \u2014 да/нет): ')
            if choice == '':
                continue
            else:
                ch = choice[0]
            if ch in 'yд':
                values = {}
                return False
            elif ch in 'nн':
                return False
    else:
        while True:
            choice = input('Введите имя переменной для удаления (пустая строка \u2014 отмена): ')
            choice = choice.strip()
            if choice == '':
                return False
            if choice in values.keys():
                values.pop(choice)
                return True
            else:
                print(f'Переменная {choice} отсутствует')



def evaluate(se):
    subs_list = [(k,v) for k, v in values.items()]
    subs_string = current_values(se)
    if subs_string:
        subs_string = ', где ' + subs_string
    sec = se.subs(subs_list)
    digits = options['digits']
    sec = sec.evalf(digits)
    print(f'{se} = {sec}' + subs_string)
    if str(sec).find('zoo') != -1 or str(sec).find('nan') != -1:
        print('Деление на 0')
        input('Нажмите "ввод"')
        return se
    while True:
        choice = input('Сохранить как текущее (y/n \u2014 да/нет): ')
        if choice == '':
            continue
        else:
            ch = choice[0]
        if ch in 'yд':
            return sec
        elif ch in 'nн':
            return se


def new_expr(se):
    global variables
    se_new = 'Error'
    while se_new == 'Error':
        expr = input('Введите выражение (пустая строка \u2014 отмена): ')
        if expr:
            se_new = symbolic_expr(expr)
        else:
            return se
    return se_new

if __name__ == '__main__':
    expr = '0'
    main_menu(expr)


