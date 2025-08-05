#!/bin/python3
import argparse

version = '3.0'

parser = argparse.ArgumentParser(description=f'Символьный калькулятор: версия {version}', add_help=False)

parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='показать справку и выйти')
parser.add_argument('-m', action='store_true', help='мини-графическая версия (по умолчанию)')
parser.add_argument('-c', action='store_true', help='консольная версия')
parser.add_argument('-l', action='store_true', help='логировать в консоль')
parser.add_argument('-f', action='store_true', help='логировать в файл')

args = parser.parse_args()

if args.m:
    from gui.minigui_app import main
# elif args.g: # Полная графическая версия находится в разработке
elif args.c:
    from console.console_app import main 
else:
    from gui.minigui_app import main

main(log_console=args.l, log_file=args.f)

