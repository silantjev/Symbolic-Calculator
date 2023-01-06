# This module contains functions to parse the input expression and make the calculation graph.

def is_balanced(expr):
    """ Checks the correctness of the bracket positions """
    stack = []
    brackets = {'(': ')', '[': ']', '{': '}'}
    for symbol in expr:
        if symbol in brackets.keys():
            stack.append(symbol)

        elif symbol == '|':
            if stack == []:
                stack = ['|']
            elif stack[-1] != '|':
                stack.append('|')
            else:
                stack.pop()

        elif symbol in brackets.values():
            if stack == []:
                return False
            else:
                poped = stack.pop()
                if poped == '|':
                    return False
                elif symbol != brackets[poped]:
                    return False
    return stack == []


def replace_all(expr, replace_dict):
    for k, v in replace_dict.items():
        expr = expr.replace(k, v)
    return expr


def delete_all(expr, del_list):
    for s in del_list:
        expr = expr.replace(s, '')
    return expr


def insert_abs(expr):
    stack = []
    while True:
        i = expr.find('|')
        if i == -1:
            break
        else:
            j = -1-expr[::-1].find('|') # index of the last '|'
            if j == -1:
                after = ''
            else:
                after = expr[j+1:]
            expr = expr[:i] + 'abs(' + expr[i+1:j] + ')' + after

    return expr


def cleaning(expr):
    """ Checks and cleans the expression """
    assert is_balanced(expr)
    expr = expr.strip()
    replace_dict = {
        '[': '(', '{': '(', ']': ')', '}': ')',
        ' mod': '%',
        '\\mod': '%',
        #',': '.',
        '**': '^'
        }
    expr = replace_all(expr, replace_dict)
    expr = insert_abs(expr)
    return delete_all(expr, '$\\ \t\n')

def make_graph(expr: str) -> dict:
    """ Creates new calculation graph for the expression 'expr' """
    graph = {}
    insert(graph, expr)
    return graph


def insert(graph: dict, expr: str):
    """ Inserts the expression 'expr' to the graph 'graph' """
    expr0 = expr
    while True:
        if expr.startswith('(') and expr.endswith(')'):
            expr = expr[1:-1]
        elif expr.startswith('+'):
            expr = expr[1:]
        elif expr.startswith('-'):
            expr = '0' + expr
        elif expr.startswith(('*', '/', '//', '%')):
            expr = '1' + expr
        elif expr.endswith('%'):
            expr = expr[:-1] + '/100'
        else:
            break
    
    assert expr != ''
    p = parse(expr) # p = ([arg_1,..., arg_n], n-ary operation)
    graph[expr0] = p
    for arg in p[0]:
        insert(graph, arg)


def parse(expr: str) -> tuple:
    """ Parses the expression 'expr' in the form ([arg_1,..., arg_n], n-ary operation) """
    sp = splitting2(expr, ['+', '-'])
    if sp == None:
        sp =  splitting2(expr, ['*', '/', '//', '%'])
    if sp == None:
        sp =  splitting2(expr, ['^'])
    if sp != None:
        i, oper = sp
        arg1 = expr[:i]
        arg2 = expr[i+len(oper):]
        return [arg1, arg2], oper
    postoperations = ['!!', '!']
    for oper in postoperations:
        if expr.endswith(oper):
            arg = expr[:-len(oper)]
            return [arg], oper

    i = expr.find('(')
    if i != -1:
        assert expr.endswith(')')
        fun = expr[:i] # name of a function
        args = splitting_comma(expr[i+1:-1]) # arguments of the function
        return args, fun
    
    return [], expr


def splitting2(expr, operations):
    """ Searches first 'operation' in the top level parts of the expression 'expr' """
    """ Returns index and operation to split the expression it into 2 parts """
    stack = 0
    end = -1
    for i, s in enumerate(expr):
        if s == '(':
            if stack == 0:
                # check the expression before all '(' (if end=-1) and between ')', '(':
                expr_to_check = expr[end+1:i]
                for oper in operations:
                    j = expr_to_check.find(oper)
                    if j != -1:
                        return end+1+j, oper
            stack += 1
        elif s == ')':
            end = i
            stack -= 1
    # finally check the expression after all ')':
    for oper in operations:
        expr_to_check = expr[end+1:]
        j = expr_to_check.find(oper)
        if j != -1:
            return end+1+j, oper


def splitting_comma(expr):
    """ Splits the expression 'expr' by commas on the top level parts"""
    args =[]
    sp = splitting2(expr, ',')
    i = -1 # needed for the case sp == None
    while sp:
        i, oper = sp
        arg = expr[:i]
        args.append(arg)
        expr = expr[i+1:]
        sp = splitting2(expr, ',')

    args.append(expr)
    return args


if __name__ == '__main__':
    expr = 'abs(x+4) + y!'
    expr = cleaning(expr)
    print(expr)
    graph = make_graph(expr)
    for k, v in graph.items():
        print(f'\'{k}\': {v}')


