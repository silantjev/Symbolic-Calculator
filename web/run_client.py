import sys
import argparse
import ipaddress
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

VERSION = '3.0'

def check_host(host):
    try:
        ipaddress.ip_address(host)
    except ValueError:
        raise ValueError(f"Wrong host syntax: {host}")

def check_port(port):
    try:
        port = int(port)
    except ValueError:
        raise ValueError(f"Wrong port: {port}. It should be integer value in [1, 65535]")
    if port < 1:
        raise ValueError(f"Minimal port is 1")
    if port > 65535:
        raise ValueError(f"Maximal port is 65535")


def make_url(host, port):
    try:
        check_host(host)
        check_port(port)
        url=f"http://{host}:{port}"
        requests.get(
                f"{url}/calc/get_state",
                params={"full": False},
                timeout=5,
            )
        return url
    except requests.exceptions.ConnectionError as exc:
        print(f"Connection to '{url}' failed: {exc}")
        print(f"Run service:\n./run_web_service.sh --host {host} --port {port}")
    except ValueError as exc:
        print(f"Error: {exc}")
    sys.exit(1)

parser = argparse.ArgumentParser(description=f'Символьный калькулятор (клиетнт): версия {VERSION}', add_help=False)

parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='показать справку и выйти')
parser.add_argument('-m', action='store_true', help='мини-графическая версия (по умолчанию)')
parser.add_argument('-c', action='store_true', help='консольная версия')
parser.add_argument('-l', action='store_true', help='логировать в консоль')
parser.add_argument('-f', action='store_true', help='логировать в файл')
parser.add_argument('--host', type=str, default='127.0.0.1', help='host')
parser.add_argument('--port', type=str, default='8000', help='port')

args = parser.parse_args()

if args.m:
    from gui.minigui_client import main
# elif args.g: # Полная графическая версия находится в разработке
elif args.c:
    from console.console_client import main 
else:
    from gui.minigui_client import main

url = make_url(args.host, args.port)

main(log_console=args.l, log_file=args.f, url=url)

