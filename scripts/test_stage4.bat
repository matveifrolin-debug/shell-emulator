@echo off
rem Этап 4: ls, cd, du, uniq на VFS с 3+ уровнями
python "%~dp0..\src\main.py" --vfs "%~dp0..\vfs\deep.csv" --script "%~dp0start_stage4.txt"