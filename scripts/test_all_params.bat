@echo off
rem Оба параметра, скрипт с ошибочными строками
python "%~dp0..\src\main.py" --vfs "%~dp0..\vfs\minimal.csv" --script "%~dp0start_errors.txt"