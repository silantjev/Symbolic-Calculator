#!/bin/python3
import argparse

version = '2.3'

parser = argparse.ArgumentParser(description=f'Символьный калькулятор: версия {version}', add_help=False)

parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='показать справку и выйти')
parser.add_argument('-m', action='store_true', help='мини-графическая версия (по умолчанию)')
parser.add_argument('-c', action='store_true', help='консольная версия')

args = parser.parse_args()

if args.m:
    from gui.minigui import main
# elif args.g: # Полная графическая находится в разработке
elif args.c:
    from console.console_calc import main 
else:
    from gui.minigui import main

main()

