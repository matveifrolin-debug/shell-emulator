@echo off
rem Ошибка: стартовый скрипт не существует
python "%~dp0..\src\main.py" --script "%~dp0no_such_file.txt"