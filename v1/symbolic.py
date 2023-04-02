# This module contains functions to transform the input string to the sympy expression

from graph import make_graph
from graph import cleaning
from sympy import *

# Global variables:
# 'variables' is a dict of variables {'x': sympy.Symbol('x'), ...},
# 'graph' is the calculation graph made by make_graph

abs = globals()['Abs']
min = globals()['Min']
max = globals()['Max']

def sumprod(args, sign):
    """ Auxiliary function to transform 'sum' and 'prod' """
    s = ''
    if args:
        s = args[0]
        for arg in args[1:]:
            s += sign + arg
    return s

def bottom(oper, variables):
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
        if oper not in variables.keys():
            variables[oper] = Symbol(oper)
        return variables[oper]

def symbolic_expr(expr: str):
    """ Builds the sympy expression by the string 'expr' """
    def calc_sym(expr):
        """ Calculates the symbolic expression by the graph with the root 'expr' """
        global variables
        global graph
        args, oper =  graph[expr]
        if args == []:
            return bottom(oper, variables)
        if oper == '+':
            return calc_sym(args[0]) + calc_sym(args[1])
        if oper == '-':
            return calc_sym(args[0]) - calc_sym(args[1])
        if oper == '*':
            return calc_sym(args[0]) * calc_sym(args[1])
        if oper == '/':
            return calc_sym(args[0]) / calc_sym(args[1])
        if oper == '//':
            return calc_sym(args[0]) // calc_sym(args[1])
        if oper == '%':
            return calc_sym(args[0]) % calc_sym(args[1])
        if oper == '^':
            return calc_sym(args[0]) ** calc_sym(args[1])
        if oper == '!!':
            return factorial2(calc_sym(args[0]))
        if oper == '!':
            return factorial(calc_sym(args[0]))
        if oper == 'round':
            return floor(args[0] + '- 0.5')
        opers = {'sum': '+', 'prod': '-'}
        if oper in opers.keys():
            return sumprod(args, opers[oper])
        # https://docs.sympy.org/latest/modules/functions/index.html
        fun = globals()[oper]
        return fun(*args)
    
    global variables
    global graph
    variables = {}
    expr = cleaning(expr)
    graph = make_graph(expr)
    se = calc_sym(expr)
    try:
        se = calc_sym(expr)
        # Without any variable the expression 'se' is still a string,
        # we need to transform it to a sympy expression:
        if isinstance(se, str):
            se = parse_expr(se)

    except: # for incorrect expressions
        se = 'Error'

    return se


if __name__ == '__main__':
    #expr = 'round(x+4.1) + y!'
    expr = 'diff(x^7,x)'
    #print(locals()['diff'])
    print(expr)
    se = symbolic_expr(expr)
    print(se)
    if se != 'Error':
        print(se.subs([('x', 5), ('y', 3)]).evalf(10))
        #x = variables['x']
        #y = variables['y']
        #print(se.subs([(x, 5), (y, 3)]))


