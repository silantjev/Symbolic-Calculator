# Symbolic Calculator
Проект «Символьный Калькулятор» — это десктопное приложение (в консольной и графической версии), написанное на языке Python.
Его предназначение — численные и символьные вычисления.
Приложение фактически устроенное как оболочка для модуля SymPy (модуль Python для оперирования с математическими абстракциями и выполнения как символьных так и численных вычислений).
Цель написания приложения состоит в создании простого калькулятора, который имеет клавиатурный ввод (плюс вставка из буфера обмена «копи-паст») и заодно работает с символьными переменными.
Для описания использования, см. файл help_rus.txt

Автор: А. В. Силантьев

Версия: 3.0

Файлы:
```plaintext
.
├── core
│   ├── graph.py            — функции для первичного парсинга строки в вычислительный граф
│   ├── symbolic.py         — класс для перевода в sympy-выражения
│   ├── calculator.py       — класс-калькулятор
│   ├── logger.py           — логирование
│   └── help_rus.txt        — текст с инструкцией использования
├── console
│   └── console_calc.py     — консольная версия
├── gui
│   ├── minigui.py          — мини-графическая версия калькулятора
│   ├── qt_classes.py       — вспомогательный модуль для графической версии
├── telegram
│   ├── bot.py              — сервис для телеграм-бота (требуется токен)
│   └── mytoken.py          — здесь секретный токен: TOKEN = ...
├── Dockerfile              (используется для создания образа консольной версии)
├── LICENSE
├── README.md
├── README_RUS.md
├── requirements.txt
├── requirements_console_calc.txt
└── symcalc.py              — скрипт для запуска
```

Полная графическая версия находится в разработке

Мой телеграм бот: https://t.me/SymbolicCalculator_bot

Используемые библиотеки:
sympy==1.11.1, PyQt5==5.15.7, simple_term_menu==1.6.1, pyTelegramBotAPI==4.12.0

Файлы с расширением py следует запускать программой-интерпретатором:
python3 ccalc.py
или
python ccalc.py

Для установки Python см. https://www.python.org/downloads/
На ubuntu:
sudo apt-get install python3

Также необходимо установить модули:
pip install sympy PyQt5 simple_term_menu
или
pip install -r requirements.txt

Команды для docker.

-Создание образа:
docker build -t ccalc_image .

-Запуск:
docker run -it --rm --name ccalc ccalc_image

-Остановка:
docker stop ccalc

7 directories, 28 files
