# Symbolic Calculator
Проект «Символьный Калькулятор» — это десктопное приложение (в консольной и графической версии), написанное на языке Python.
Его предназначение — численные и символьные вычисления.
Приложение фактически устроенное как оболочка для модуля SymPy (модуль Python для оперирования с математическими абстракциями и выполнения как символьных так и численных вычислений).
Цель написания приложения состоит в создании простого калькулятора, который имеет клавиатурный ввод (плюс вставка из буфера обмена «копи-паст») и за одно работает с символьными переменными.
Для описания использования, см. файл help_rus.txt

Автор: А. В. Силантьев

Файлы:
ccalc.py — консольная версия калькулятора
graph.py — вспомогательный модуль
symbolic.py — вспомогательный модуль
requirements.txt — файл с необходимыми библиотеками
Dockerfile используется для создания образа приложения ccalc

Графическая версия находится в разработке

Используемые библиотеки:
os, sympy=1.11.1

Файлы с расширением py следует запускать программой-интерпретатором:
python3 ccalc.py
или
python ccalc.py

Для установки Python см. https://www.python.org/downloads/
На ubuntu:
sudo apt-get install python3

Также необходимо установить модуль SymPy:
pip install sympy
или
pip install -r requirements.txt

Команды для docker.

-Создание образа:
docker build -t ccalc_image .

-Запуск:
docker run -i --rm --name ccalc ccalc_image

-Остановка:
docker stop ccalc
