@echo off
rem Этап 5: cp на VFS с 3+ уровнями (изменения только в памяти)
python "%~dp0..\src\main.py" --vfs "%~dp0..\vfs\deep.csv" --script "%~dp0start_stage5.txt"