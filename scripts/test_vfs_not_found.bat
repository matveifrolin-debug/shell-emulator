@echo off
rem Ошибка: файл VFS не найден
python "%~dp0..\src\main.py" --vfs "%~dp0..\vfs\no_such_vfs.csv" --script "%~dp0start_vfs.txt"