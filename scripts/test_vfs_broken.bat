@echo off
rem Ошибка: неверный формат VFS
python "%~dp0..\src\main.py" --vfs "%~dp0..\vfs\broken.csv" --script "%~dp0start_vfs.txt"