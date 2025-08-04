import argparse
import sys
from pathlib import Path
from telebot import TeleBot
from sympy import * # pylint: disable=wildcard-import, unused-wildcard-import

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.calculator import Calculator
from core.logger import make_logger
from core.session_storage import JSONStorage, StateManager

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
    def __init__(self, token, logger, conf_path=""):
        super().__init__(token)
        self.logger = logger
        self.calcs = dict()
        storage = JSONStorage(logger=self.logger, json_path=conf_path)
        self.state_manager = StateManager(storage=storage)
        self.logger.info("Tegram bot launched")

    def get_calc(self, chat_id, restart=False):
        """ Gets calulator for the chat
        Creates new calculator if it does not exist
        """
        if restart and chat_id in self.calcs:
            self.calcs.pop(chat_id)

        if chat_id not in self.calcs:
            self.calcs[chat_id] = BCalculator(logger=self.logger) # separate calculator for each chat with initial expr='0'
            self.state_manager.load_state(calc=self.calcs[chat_id], session_id=chat_id)
            self.logger.info("Bot added some chat")
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
        /save — сохранить состояние и опции
        /crear — полная отчистка
        """
        self.send_message(chat_id, text)

    def cancel(self, message):
        text = 'Отмена\n'
        self.send_message(message.chat.id, text)
        message.text = '/status'
        action(message)

    def save(self, chat_id):
        self.state_manager.save_state(self.calcs[chat_id], session_id=chat_id)
        self.logger.info("State of chat %s saved", chat_id)

    def save_all(self):
        for chat_id in self.calcs:
            self.save(chat_id)

    def load(self, chat_id):
        self.state_manager.load_state(self.calcs[chat_id], session_id=chat_id)
        self.logger.info("State loaded for chat %s", chat_id)


try:
    from telegram.mytoken import TOKEN
except ModuleNotFoundError:
    TOKEN = '' # enter the token of your bot here

if not TOKEN:
    TOKEN = input("Токен не найден. Введите токен своего телеграм-бота: ")

if not TOKEN:
    raise ValueError("Put your token to variable TOKEN in telegram/token.py")

parser = argparse.ArgumentParser(description=f'Символьный калькулятор: телеграм-бот', add_help=False)

parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='показать справку и выйти')
parser.add_argument('-l', action='store_true', help='логировать в консоль')
parser.add_argument('-f', action='store_true', help='логировать в файл')
parser.add_argument('--conf', type=str, default="", help='логировать в файл')

args = parser.parse_args()

logger = make_logger(name="telegram_bot", file=args.f, console=args.l)
bot = BotCalc(TOKEN, logger=logger, conf_path=args.conf)

@bot.message_handler(commands=['info', 'help', 'h'])
def info(message):
    chat_id = message.chat.id
    if chat_id not in bot.calcs:
        bot.get_calc(chat_id)
    s1 = message.text[1] # first symbol of the command
    if s1 == 'i':
        bot.info(chat_id)
    elif s1 == 'h':
        bot.send_message(chat_id, bot.calcs[chat_id].get_help_text())

@bot.message_handler(commands=['save'])
def save_state(message):
    chat_id = message.chat.id
    bot.get_calc(chat_id, restart=False)
    bot.save(chat_id)
    bot.send_message(chat_id, "State saved")

@bot.message_handler(commands=['clear'])
def clear(message):
    chat_id = message.chat.id
    calc = bot.get_calc(chat_id, restart=False)
    calc.clear_all()
    bot.send_message(chat_id, "State cleared")

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
    bot.logger.debug("text_handler: text = '%s'", message.text)
    chat_id = message.chat.id
    calc = bot.get_calc(chat_id)

    if calc.change_variable_mode:
        calc.change_variable_mode = False
        var =  message.text
        if not var or var[0] == '/':
            bot.cancel(message)
            return

        calc.input_variable = var
        text = f'Введите значение переменной {var}\n(для отмены введите "/"):'

    elif calc.delete_variable_mode:
        calc.delete_variable_mode = False
        var =  message.text
        if not var or var[0] == '/':
            bot.cancel(message)
            return

        if var not in calc.values:
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
        if not expr or expr[0] == '/':
            bot.cancel(message)
            return

        calc.set_value(var, expr)
        lines = [f'Новое значение {var} = {expr}\n']
        lines.extend(calc.status())
        text = '\n'.join(lines)

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
        if text == "":
            text = '\n'.join(calc.status()) 

    bot.logger.debug("Sending message: '%s'", text)
    bot.send_message(chat_id, text)

if __name__ == '__main__':
    try:
        bot.polling()
    except KeyboardInterrupt:
        bot.logger.info("Interrupted by Keyboard")
    # except Exception as exc:
        # bot.logger.error("Error: %s", exc)
    finally:
        bot.save_all()
