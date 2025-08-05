# General calculator: module for ccalc, bot and minigui 

import sys
import logging
from pathlib import Path
from sympy import * # pylint: disable=wildcard-import, unused-wildcard-import

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.logger import make_logger
from core.symbolic import Symbolic


class Calculator(Symbolic):

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

    DEFAULT_OPTIONS =  {'digits': 8}
    def __init__(self, expr='0', logger=None):
        """ expr: SymPy expression of the string type """
        super().__init__()

        if logger is None:
            logger_name = self.__class__.__name__
            self.logger = make_logger(name=logger_name, file=False, console=False, level=logging.WARNING)
        else:
            self.logger = logger
        level_str = logging.getLevelName(self.logger.level)
        self.logger.debug("Logger '%s' created with level %s", self.logger.name, level_str)

        expr = str(expr)  # For the case if 'expr' is a SymPy object 
        self.expr = expr
        self.se = parse_expr(expr) # SymPy parser 'parse_expr' is used
        self.sec = self.se # SymPy Expression Calculated
        self.values = {}
        self.options = self.DEFAULT_OPTIONS
        self.explanations = {'digits': 'Точность вычисления в количестве цифр'}
        self.help_text = ""
        self._load_help_text()

    def _load_help_text(self):
        core_dir = Path(__file__).resolve().parent
        path = core_dir / 'help_rus.txt'
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    self.help_text = file.read()
            except IOError as e:
                self.logger.warning("Failed to open file '%s'. Error: %s", path, e)
                print("Не удалось открыть файл '%s'" % path)
        else:
            self.logger.warning("File %s not found", path)

        if self.help_text == "":
            self.help_text = "Справка не загрузилась"

    def symbolic_expr(self, expr):
        se_new = super().symbolic_expr(expr)
        if se_new == 'Error':
            self.logger.error('Unknown Error')
            raise AssertionError('Неизвестная ошибка')
        return se_new

    def set_new_expr(self, expr):
        expr = expr.replace('_', '(' + str(self.se) + ')')
        try:
            se_new = self.symbolic_expr(expr)
            # if se_new == 'Error':
                # raise AssertionError('Неизвестная ошибка')
            if str(se_new).find('zoo') != -1 or str(se_new).find('nan') != -1:
                self.logger.error('Zero Devision Error')
                raise ZeroDivisionError('Деление на 0')
            self.se = se_new
            self.logger.info("New sympy-expression: se = %s", se_new)
            return ""
        except (AssertionError, ValueError, TypeError, KeyError, ZeroDivisionError) as exc:
            self.logger.error("Error while setting new expression: %s", exc)
            return f'Ошибка: {exc}\nПопытайтесь ещё раз.\n'

    def get_current_variables(self) -> set[str]:
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

    def current_values(self) -> str:
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

    def get_nice(self, se=None) -> str:
        if se is None:
            se = self.se

        if isinstance(se, Float):
            return str(self.dec_round(se))

        return str(se)

    def evaluate(self):
        """ Evaluates 'se' """
        subs_list = list(self.values.items())
        # subs_string = self.current_values()
        # if subs_string:
            # subs_string = ', где ' + subs_string
        sec = self.se.subs(subs_list)
        digits = self.options['digits']
        sec = sec.evalf(digits)
        sec = self.dec_round(sec)
        self.logger.info("Sympy-expression (se = %s) evaluated and ronded to %d digits: sec = %s", self.se, digits, sec)
        return sec

    def get_variables(self, include_unset=True) -> tuple[set[str], list[str]]:
        """
        Возвращает:
          - current : Set[str]
          - lines : List[str]
        """
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

    def set_option(self, k, val) -> bool:
        try:
            val = int(val)
            if val == self.options[k]:
                self.logger.debug("Trying to set the same value %d to option %s", val, k)
                return True
            if val > 1:
                self.options[k] = val
                self.logger.debug("Option %s set to value %d", k, val)
                return True
            self.logger.warning("Wrong value of %s. The value should be positive but %d is given", k, val)
        except TypeError:
            self.logger.warning("Wrong type of the value of %s. The type is %s, but int is needed", k, type(val))
        except KeyError:
            self.logger.warning("Key Error: probably wrong option '%s'", k)

        return False


    """ API for interfaces
        Using it instead of direct acces to attributes allow to change class Calculator by a web-client
    """

    def set_se(self, expr):
        expr = str(expr)
        self.se = parse_expr(expr)
        self.logger.info("Sympy-expression: se = %s", self.se)

    def set_expr(self, expr):
        self.expr = expr
        self.logger.info("New expression set: expr = %s", expr)

    def set_sec(self, sec):
        self.sec = sec
        self.logger.info("Field 'sec' set: sec = %s", sec)

    def set_value(self, var, expr):
        value = self.symbolic_expr(expr)
        self.values[var] = value
        self.logger.info("Value of %s set to %s", var, value)

    def delete_all_values(self):
        self.values = {}
        self.logger.info("Values of all variables deleted")

    def delete_value(self, var):
        self.values.pop(var)
        self.logger.info("Values of variable %s deleted", var)

    def get_value(self, var: str) -> str:
        """ Get value of a variable """
        value = self.values.get(var)
        return self.get_nice(value)

    def get_expr(self):
        return self.expr

    def get_sec(self):
        return str(self.sec)

    def get_se(self):
        return self.se

    def get_var_names(self):
        return self.values.keys()

    def get_options(self) -> dict[str, int]:
        return self.options

    def get_explanations(self) -> dict[str, str]:
        return self.explanations

    def get_help_text(self) -> str:
        return self.help_text

    def get_session(self):
        session_data = {}
        session_data['expr'] = str(self.expr)
        session_data['se'] = str(self.se)
        session_data['sec'] = str(self.sec)
        session_data['options'] = self.options
        session_data['values'] = self.values
        return session_data
    
    def load_state(self, data):
        self.set_expr(data['expr'])
        self.set_se(data['se'])
        self.set_sec(data['sec'])
        self.options = data['options']
        for var, value in data.get('values', {}).items():
            self.set_value(var, value)

    def clear_all(self):
        data = {'expr': '0', 'se': '0', 'sec': '0', 'options': self.DEFAULT_OPTIONS}
        self.load_state(data)
