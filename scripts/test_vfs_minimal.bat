@echo off
rem VFS: минимальная (только корень)
python "%~dp0..\src\main.py" --vfs "%~dp0..\vfs\minimal.csv" --script "%~dp0start_vfs.txt"