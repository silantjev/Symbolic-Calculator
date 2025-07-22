# This module contains functions (realised as methods)
# that transform the input string to SymPy expression

from sympy import * # pylint: disable=wildcard-import, unused-wildcard-import

try:
    from .graph import make_graph, cleaning, splitting_comma
except ImportError:
    from graph import make_graph, cleaning, splitting_comma

# abs = globals()['Abs']
# min = globals()['Min']
# max = globals()['Max']

# The functions 'abs', 'min', 'max' are not in globals()
# Substitute them to their SymPy analogues:
abs = Abs
min = Min
max = Max

class Symbolic:

# Attributes
# variables: dict of variables {'x': sympy.Symbol('x'), ...},
# graph: calculation graph made by the function 'make_graph'


    def sumprod(self, args, sign):
        """ Auxiliary method to transform 'sum' and 'prod' """
        s = ''
        if args:
            s = args[0]
            for arg in args[1:]:
                s += sign + arg
        return s

    def bottom(self, oper):
        """ Transforms expression 'oper' (operator without arguments)
        to a SymPy object.
        Creates SymPy Symbols if needed
        """
        if oper == 'pi':
            return pi
        if oper == 'E':
            return E
        if oper == 'I':
            return I
        try:
            complex(oper)
        except ValueError:
            if oper not in self.variables.keys():
                self.variables[oper] = Symbol(oper)
            return self.variables[oper]

        # If ValueError has not occurred, then 'oper' is an integer, float or complex type number,
        # so we transform it to a SymPy class object by the SymPy function 'parse_expr'
        return parse_expr(oper)

    def calc_sym(self, expr):
        """ Calculates the symbolic expression by the tree 'graph' with the root 'expr' """
        args, oper =  self.graph[expr]
        if args == []:
            return self.bottom(oper)
        if oper == '+':
            return self.calc_sym(args[0]) + self.calc_sym(args[1])
        if oper == '-':
            return self.calc_sym(args[0]) - self.calc_sym(args[1])
        if oper == '*':
            return self.calc_sym(args[0]) * self.calc_sym(args[1])
        if oper == '/':
            return self.calc_sym(args[0]) / self.calc_sym(args[1])
        if oper == '//':
            return self.calc_sym(args[0]) // self.calc_sym(args[1])
        if oper == '%':
            return self.calc_sym(args[0]) % self.calc_sym(args[1])
        if oper == '^':
            return self.calc_sym(args[0]) ** self.calc_sym(args[1])
        if oper == '!!':
            return factorial2(self.calc_sym(args[0]))
        if oper == '!':
            return factorial(self.calc_sym(args[0]))
        if oper == 'round':
            if len(args) == 1:
                return floor(args[0] + '+ 0.5')
            if len(args) == 2:
                try: 
                    d = int(args[1])
                except ValueError:
                    raise AssertionError('Второй аргумент функции "round" должен быть целым числом')
                return 10**(-d) * floor(f'10**{d} * ({args[0]}) + 0.5')
            assert len(args) != 0, 'Функция "round" требует аргумента'
            # Остался случай len(args) > 2
            raise AssertionError('Функция "round" не допускает более двух аргументов')

        opers = {'sum': '+', 'prod': '-'}
        if oper in opers.keys():
            return self.sumprod(args, opers[oper])
        if oper == 'integrate':
            assert len(args) > 1, 'оператор "integrate" требует больше аргументов'
            integrand = args.pop(0)
            limits = []
            for arg in args:
                if arg.startswith('('):
                    assert arg.endswith(')'), 'Лишние символы после скобки'
                    subargs = splitting_comma(arg[1:-1]) # list [x] or [x, a, b]
                    if subargs[-1].strip() == '':
                        subargs.pop()
                else:
                    subargs = [arg]
                limits.append(tuple(subargs))
            return integrate(integrand, *limits)

        # https://docs.sympy.org/latest/modules/functions/index.html
        fun = globals()[oper]
        return fun(*args)
        
    def symbolic_expr(self, expr: str):
        """ Builds the sympy expression by the string 'expr' """
        self.variables = {}
        expr = cleaning(expr)
        self.graph = make_graph(expr)
        # se = self.calc_sym(expr) # for debugging
        try:
            se = self.calc_sym(expr)
            # Without any variable the expression 'se' is still a string,
            # we need to transform it to a sympy expression:
            if isinstance(se, str):
                se = parse_expr(se)

        except AssertionError as exc:
            raise
        except KeyError as exc:
            raise KeyError(f'Функция {str(exc)} не найдена')
        except: # for incorrect expressions
            se = 'Error'

        return se


if __name__ == '__main__':
    # expr = 'diff(x^7,x)'
    # print(locals()['diff'])
    expr = 'abs(x-y)'
    expr = 'integrate(x^2 + x + 1, (x,), y,)'
    expr = 'round(x+11115.2222, -3) + y'
    print('expr = ', expr)
    symb = Symbolic()
    se = symb.symbolic_expr(expr)
    print('se = ', se)
    if se != 'Error':
        print(se.subs([('x', 5), ('y', 0)]).evalf(10))
        # x = variables['x']
        # y = variables['y']
        # print(se.subs([(x, 5), (y, 3)]))


