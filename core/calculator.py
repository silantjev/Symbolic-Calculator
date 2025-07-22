# General calculator: module for ccalc, bot and minigui 

import logging
from pathlib import Path
from sympy import * # pylint: disable=wildcard-import, unused-wildcard-import

try:
    from .logger import make_logger
    from .symbolic import Symbolic
except ImportError:
    from logger import make_logger
    from symbolic import Symbolic


class Calculator(Symbolic):
    """ Mini GUI version of calculator.
    The inherited method 'symbolic_expr' is used.
    """

    # Attributes:

    # expr: input expression

    # se: current expression as a SymPy object (Sympy Expression)

    # sec: evaluated 'se' (Sympy Expression Calculated)

    # values: is a dict of their values {'x': value}, where value is a number
    # (if a variable 'x' does not have a value, then we output it as an abstract variable)

    # options: values of options

    # explanations: description of options (a constant)

    # Options:
    # digits: means the number of digits, which are shown by evaluation

    def __init__(self, expr='0', logger=None):
        """ expr: SymPy expression of the string type """

        if logger is None:
            logger_name = logging.self.__class__.__name__
            self.logger = make_logger(name=logger_name, file=False, console=False, level=logging.WARNING)
        else:
            self.logger = logger
        level_str = logging.getLevelName(self.logger.level)
        self.logger.debug("Logger '%s' created with level %s", self.logger.name, level_str)

        expr = str(expr)  # For the case if 'expr' is a SymPy object 
        self.expr = expr
        self.se = parse_expr(expr) # SymPy parser 'parse_expr' is used
        self.sec = self.se # SymPy Expression Calculated
        self.variables = {}
        self.values = {}
        self.options = {'digits': 8}
        self.explanations = {'digits': 'Точность вычисления в количестве цифр'}
        self.help_text = ""
        self.load_help_text()

    def set_new_expr(self, expr):
        expr = expr.replace('_', '(' + str(self.se) + ')')
        try:
            se_new = self.symbolic_expr(expr)
            if se_new == 'Error':
                raise AssertionError('Неизвестная ошибка')
            if str(se_new).find('zoo') != -1 or str(se_new).find('nan') != -1:
                raise ZeroDivisionError('Деление на 0')
            self.se =  se_new
            return
        except (AssertionError, ValueError, TypeError, KeyError, ZeroDivisionError) as exc:
            return f'Ошибка: {exc}\nПопытайтесь ещё раз.\n'

    def get_current_variables(self):
        current = {var.name for var in self.se.free_symbols}
        return current

    # def get_other_variables(self):
        # other = set(self.variables.keys()) - self.get_current_variables()
        # return other

    def get_values(self, variable_set=None):
        """ Get text with values of required variables """
        if variable_set is None:
            variable_set = self.variables.keys()
        subs_strings= [f'{k} = {self.get_nice(v)}' for k, v in self.values.items() if k in variable_set]
        subs_string = ', '.join(subs_strings)
        return subs_string

    def current_values(self):
        current = self.get_current_variables()
        return self.get_values(current)

    def dec_round(self, x):
        """ Round a float-like number.
        Number of non-zero digits is taken from the attribute 'options'
        """
        try:
            x = float(x)
        except TypeError:
            return x
        if x == 0.0:
            return 0.0
        exponent = int(log(abs(x),10)) + (abs(x) >= 1)
        mantissa = x * 10**(-exponent)
        digits = self.options['digits']
        # For correct rounding we use function 'int'
        # (function 'round' works not always correctly):
        mantissa = 10**(-digits) * int(10**digits * mantissa + 0.5)
        # We use round to delete an incorrent tail:
        return round(mantissa * 10**exponent, digits)

    def get_value(self, var):
        """ Get value of a variable """
        value = self.values.get(var)
        return self.get_nice(value)

    def get_nice(self, se=None):
        if se == None:
            se = self.se

        if isinstance(se, Float):
            return self.dec_round(se)

        return se

    def evaluate(self):
        """ Evaluates 'se' """
        subs_list = [(k,v) for k, v in self.values.items()]
        # subs_string = self.current_values()
        # if subs_string:
            # subs_string = ', где ' + subs_string
        sec = self.se.subs(subs_list)
        digits = self.options['digits']
        sec = sec.evalf(digits)
        sec = self.dec_round(sec)
        return sec

    def get_variables(self, include_unset=True):
        current = self.get_current_variables()
        set_variables = set(self.values.keys())
        current_set = current & set_variables
        current_unset = current - set_variables 
        other_set = set_variables - current
        lines = []
        if current:
            lines.append('Переменные в текущем выражении:')
        if current_set and include_unset:
            lines.append('\tзаданные:')
        for var in current_set:
            lines.append(f'\t\t{var} = {self.get_value(var)}')
        if current_unset and include_unset:
            lines.append('\tсвободные:')
            for var in current_unset:
                lines.append(f'\t\t{var}')
        if other_set:
            lines.append('Переменные, отсутствующие в текущем выражении:')
        for var in other_set:
            lines.append(f'\t\t{var} = {self.get_value(var)}')

        return current, lines #'\n'.join(lines)

    def get_help_text(self):
        return self.help_text

    def load_help_text(self):
        CORE_DIR = Path(__file__).resolve().parent
        path = CORE_DIR / 'help_rus.txt'
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    self.help_text = file.read()
            except IOError as e:
                self.logger.warning("Не удалось открыть файл '%s'", path)
                print("Не удалось открыть файл '%s'" % path)
        else:
            print("Не удалось найти файл '%s'" % path)

        if self.help_text == "":
            self.help_text = "Справка не загрузилась"
                




