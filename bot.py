from gen_calc import Calculator

import os
from telebot import TeleBot
from sympy import *

class BCalculator(Calculator):
    """ bot-calculator """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_variable_mode = False
        self.input_variable = None
        self.delete_variable_mode = False

    def status(self):
        lines = [f'Текущее выражение: {self.get_nice()}']
        sec = self.evaluate()
        subs_string = self.current_values()
        if subs_string:
            subs_string = ', где ' + subs_string
        lines.append(f'Вычисление: {self.se} = {sec}' + subs_string)
        if str(sec).find('zoo') != -1 or str(sec).find('nan') != -1:
            lines.append('\t\t\tДеление на 0\n')
        lines.append('Введите команду или новое выражение:')
        return lines



class BotCalc(TeleBot):
    def __init__(self, token):
        super().__init__(token)
        self.calcs = dict()

    def get_calc(self, chat_id, restart=False):
        """ Gets calulator for the chat
        Creates new calculator if it does not exist
        """
        if restart and chat_id in self.calcs:
            self.calcs.pop(chat_id)

        if chat_id not in self.calcs:
            self.calcs[chat_id] = BCalculator() # separate calculator for each chat with initial expr='0'
        return self.calcs[chat_id]

    def info(self, chat_id):
        text = """ 
        «Символьный Калькулятор» — это приложение, предназначеное для численных и символьных вычислений.
        Написано на Python 3.10. Основано на модуле SymPy.
        https://github.com/silantjev/Symbolic-Calculator
        Чат поддерживает следующие комманды:
        Для задания нового выражения введите текст (см. /help).
        /start — начать
        /status, /s — посмотреть текущее состояние
        /eval, /e — вычислить текущее выражение
        /var, /v — посмотреть переменные
        /change, /c — добавить/изменить значения переменных
        /del, /d — удалить значение переменной
        /all — удалить все переменные
        /restart — перезапустить
        /info, /i — данная справка
        /help, /h — справка о формате вводимых выражений
        """
        bot.send_message(chat_id, text)

    def cancel(self, message):
        text = 'Отмена\n'
        self.send_message(message.chat.id, text)
        message.text = '/status'
        action(message)

try:
    from mytoken import token
except ModuleNotFoundError:
    token = '' # enter the token of your bot here

bot = BotCalc(token)

@bot.message_handler(commands=['info', 'help', 'h'])
def info(message):
    chat_id = message.chat.id
    s1 = message.text[1] # first symbol of the command
    if s1 == 'i':
        bot.info(chat_id)
    elif s1 == 'h':
        bot.send_message(chat_id, Calculator.get_help_text())

@bot.message_handler(commands=['restart'])
def restart(message):
    chat_id = message.chat.id
    calc = bot.get_calc(chat_id, restart=True)
    message.text = '/start'
    action(message, calc)

#@bot.message_handler(commands=['start',
    # 'status', 'stat', 'eval', 'evaluation',
    # 'variables', 'delete', 'all'])
def action(message, calc=None):
    chat_id = message.chat.id
    if calc is None:
        calc = bot.get_calc(chat_id)

    lines = [0] # marks the index of the first needed line in the result of calc.status() in the end of this function

    s1 = message.text[1] # first symbol of the command
    if message.text == '/start':
        lines = [f'Привет, {message.chat.first_name}!',
                'Я — символьный калькулятор.',
                'Для инструкции использования наберите /info\n'
                ] + lines
    elif s1 == 'e':
        lines = [1]
    elif s1 in 'vc': # /(change_)var(iables)
        _, lines_v = calc.get_variables()
        if s1 == 'c':
            lines = lines_v + ['Введите имя переменной', '(для отмены введите "/"):']
            calc.change_variable_mode = True
        else:
            if lines_v == []:
                lines_v = ['Сейчас нет никаких переменных.\n']
            lines = lines_v + lines

        
    elif s1 == 'd': # /del(ete_variables)
        if not calc.values:
            lines.insert(0, 'Ни одна переменная не задана\n')
        else:
            _, lines_v = calc.get_variables(include_unset=False)
            lines = lines_v + ['Введите имя переменной', '(для отмены введите "/"):']
            calc.delete_variable_mode = True

    elif message.text == '/all': # (delete all variables)
        calc.values = {}
        lines.insert(0, 'Значения всех переменных удалены.\n')
 
    status_lines = calc.status()
    lines = ['\n'.join(status_lines[line:]) if isinstance(line, int) else line for line in lines]
    bot.send_message(chat_id, '\n'.join(lines))

@bot.message_handler(content_types=['text'])
def text_handler(message):
    chat_id = message.chat.id
    calc = bot.get_calc(chat_id)

    if calc.change_variable_mode:
        calc.change_variable_mode = False
        var =  message.text
        if var == '/':
            bot.cancel(message)
            return
        else:
            calc.input_variable = var
            text = f'Введите значение переменной {var}\n(для отмены введите "/"):'

    elif calc.delete_variable_mode:
        calc.delete_variable_mode = False
        var =  message.text
        if var == '/':
            bot.cancel(message)
            return
        elif var not in calc.values:
            lines = [f'Переменная {var} отсутствует\n']
        else:
            calc.values.pop(var)
            lines = [f'Переменная {var} удалена\n']
        lines.extend(calc.status())
        text = '\n'.join(lines)

    elif calc.input_variable is not None:
        var = calc.input_variable
        calc.input_variable = None
        expr = message.text
        if expr == '/':
            bot.cancel(message)
            return
        else:
            value = calc.symbolic_expr(expr)
            calc.values[var] = value
            lines = [f'Новое значение {var} = {value}\n']
            lines.extend(calc.status())
            text = '\n'.join(lines)

    elif calc.delete_variable_mode:
        calc.delete_variable_mode = False
        return

    elif message.text == '/':
        message.text = '/status'
        action(message, calc)
        return

    elif message.text[0] == '/':
        if message.text[1] in 'ih':
            info(message)
        else:
            action(message, calc)
        return

    else:
        text = calc.set_new_expr(message.text) # None or text of an Error
        if text is None:
            text = '\n'.join(calc.status()) 

    bot.send_message(chat_id, text)

if __name__ == '__main__':
    bot.polling()
