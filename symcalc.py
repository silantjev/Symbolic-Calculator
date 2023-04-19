#!/bin/python3
import sys

args = sys.argv[1:]
command = sys.argv[0]

def first_char(s: str):
    s = s.lower()
    for ch in s:
        if ch != '-':
            return ch
    return ''

args = list(map(first_char, args))

def get_help():
    print(
        """
Символьный калькулятор.

Использование: {} [опции]

Доступные опции:
-m, -g \t мини-графическая версия (по умолчанию)
-c     \t консольная версия
-h     \t справка
""".format(command)
    )

if 'h' in args:
    get_help()
    quit()
elif 'm' in args or 'g' in args: 
    from minigui import main
elif 'c' in args:
    from ccalc import main 
else:
    from minigui import main

main()

