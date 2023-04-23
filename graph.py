# This module contains functions that clean the input expression
# parse it and to make the calculation graph.


# The two main functions:


def cleaning(expr):
    """ Checks and clean the expression 'expr' """
    assert is_balanced(expr), "Скобки не сбалансированы"
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



# The others functions are auxiliary:


def is_balanced(expr):
    """ Checks the correctness of the bracket positions.
    Checks also modulus symbols '|'.
    """
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
    """ Replaces '|some_expression|' in the string 'expr' by 'abs(some_expression)'.
    The expression 'expr' is supposed to be checked by the function 'is_balanced'.
    The expression 'expr' is supposed to be cleaned from spaces etc.
    Realised by loop instead of recursion.
    """
    
    unacceptable = '+-/*^%' # symbols that can not be in the end of argument of modulus

    while True:
        i = expr.find('|') # index of the first '|'
        if i == -1: # if not found
            break

        j = i + 1 +expr[i+1:].find('|') # index of the next '|'

        while True:
            if j == -1:
                raise AssertionError('The modulus symbols "|" are not in balance')
            if expr[j-1] not in unacceptable:
                expr = expr[:i] + 'abs(' + expr[i+1:j] + ')' + expr[j+1:]
                break

            # if the symbol before the considered '|' is unacceptable,
            # then it should be nested modulus, so we check the next one:

            j = j + 1 + expr[j+1:].find('|') # index of the next '|'

    return expr


def insert(graph: dict, expr: str):
    """ Add the parsed expression 'expr' to the dictionary 'graph'.
    Finally, recurrently does the same for all arguments.
    """
    expr0 = expr
    while True:
        if is_unnecessary(expr):
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
    
    # assert expr != ''
    if expr == '':
        expr = '0'
    p = parse(expr) # p = ([arg_1,..., arg_n], n-ary operation)
    graph[expr0] = p
    for arg in p[0]:
        insert(graph, arg)

def parse(expr: str) -> tuple:
    """ Parses the expression 'expr'
    Returns ([arg_1,..., arg_n], n-ary operation)
    """
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
        assert expr.endswith(')'), 'Лишние символы после закрывающей скобки'
        fun = expr[:i] # name of a function
        args = splitting_comma(expr[i+1:-1]) # arguments of the function
        return args, fun
    
    return [], expr


def splitting2(expr, operations):
    """ Searches first operation from 'operations'
    in the top level parts of the expression 'expr'
    ("level" means the depth of the nested parentheses),
    returns index and operation to split the expression into 2 parts.

    Note that the operations are searched in the order of 'operations',
    not by their positions in the expression;
    this gives a little different graph,
    but it does not affect the final result.
    """

    level = 0 # top level
    # The variable 'end' means the index of the previous ')'
    end = -1 # The value -1 means that there was not ')' before
    for i, s in enumerate(expr):
        if s == '(':
            if level == 0:
                # Check the expression before all '(' (if end=-1) and between ')', '(':
                expr_to_check = expr[end+1:i]
                for oper in operations:
                    j = expr_to_check.find(oper)
                    if j != -1:
                        return end+1+j, oper
            level += 1
        elif s == ')':
            end = i
            level -= 1
    # Finally, check the expression after all ')':
    for oper in operations:
        expr_to_check = expr[end+1:]
        j = expr_to_check.find(oper)
        if j != -1:
            return end+1+j, oper


def splitting_comma(expr):
    """ Splits the expression 'expr' by commas on the top level parts """
    args =[]
    sp = splitting2(expr, ',')

    while sp:
        i, oper = sp
        arg = expr[:i]
        args.append(arg)
        expr = expr[i+1:]
        sp = splitting2(expr, ',')

    # If 'sp' becomes None, then there is no more comma,
    # so the rest 'expr' is the last argument (if it is not empty):
    if expr.strip() != '':
        args.append(expr)
    return args


def is_unnecessary(expr):
    """ Check if there are unnecessary parentheses at the bounds
    expr: string expression, which supposed to be balanced
    """

    if expr.startswith('(') and expr.endswith(')'):
        pass
    else:
        return False

    level = 0
    for s in expr[:-1]:
        if s == '(':
            level += 1
        elif s == ')':
            level -= 1
        if level == 0:
            return False

    # If we came here, then the first '(' is still unclosed

    return True


if __name__ == '__main__':
    # Examples:
    expr = '|x+|z|-y|'
    expr = '|x+z|+|y|'
    expr = '(x)/(x)'
    expr = cleaning(expr)
    print('Expression:', expr)
    print('Calculation graph:')
    graph = make_graph(expr)
    for k, v in graph.items():
        print(f' \'{k}\': {v}')


