@echo off
rem Ошибка: неизвестный параметр командной строки
python "%~dp0..\src\main.py" --unknown value
echo Exit code: %errorlevel%