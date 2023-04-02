# This module contains functions (realised as methods)
# that transform the input string to SymPy expression

from graph import make_graph
from graph import cleaning
from sympy import *

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
        if oper == 'pi':
            return pi
        if oper == 'E':
            return E
        if oper == 'I':
            return I
        try:
            complex(oper)
            # If ValueError has not occurred, then it is a real or imaginary compoex number and we transform it to a sympy class object
            return parse_expr(oper)
        except:
            if oper not in self.variables.keys():
                self.variables[oper] = Symbol(oper)
            return self.variables[oper]

    def calc_sym(self, expr):
        """ Calculates the symbolic expression by the graph with the root 'expr' """
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
            return floor(args[0] + '- 0.5')
        opers = {'sum': '+', 'prod': '-'}
        if oper in opers.keys():
            return self.sumprod(args, opers[oper])
        # https://docs.sympy.org/latest/modules/functions/index.html
        fun = globals()[oper]
        return fun(*args)
        
    def symbolic_expr(self, expr: str):
        """ Builds the sympy expression by the string 'expr' """
        self.variables = {}
        expr = cleaning(expr)
        self.graph = make_graph(expr)
        se = self.calc_sym(expr)
        try:
            se = self.calc_sym(expr)
            # Without any variable the expression 'se' is still a string,
            # we need to transform it to a sympy expression:
            if isinstance(se, str):
                se = parse_expr(se)

        except: # for incorrect expressions
            se = 'Error'

        return se


if __name__ == '__main__':
    #expr = 'round(x+4.1) + y!'
    # expr = 'diff(x^7,x)'
    #print(locals()['diff'])
    expr = 'abs(x-y)'
    print(expr)
    symb = Symbolic()
    se = symb.symbolic_expr(expr)
    print(se)
    if se != 'Error':
        print(se.subs([('x', 5), ('y', 3)]).evalf(10))
        #x = variables['x']
        #y = variables['y']
        #print(se.subs([(x, 5), (y, 3)]))


