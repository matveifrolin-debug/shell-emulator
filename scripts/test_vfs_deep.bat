@echo off
rem VFS: не менее 3 уровней файлов и папок
python "%~dp0..\src\main.py" --vfs "%~dp0..\vfs\deep.csv" --script "%~dp0start_vfs.txt"