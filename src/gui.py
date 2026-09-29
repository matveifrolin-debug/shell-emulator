"""Графический интерфейс эмулятора на tkinter."""

import getpass
import socket
import tkinter as tk
from tkinter import scrolledtext

from commands import execute
from errors import ExitRequested, ShellError
from script import read_script
from shell_parser import parse_line

WINDOW_SIZE = "800x500"
FONT = ("Consolas", 11)
BG_COLOR = "black"
FG_COLOR = "white"


def get_user_host():
    """Вернуть строку user@host по данным реальной ОС."""
    return f"{getpass.getuser()}@{socket.gethostname()}"


class EmulatorApp:
    """Окно эмулятора: область вывода и строка ввода команд."""

    def __init__(self, root):
        """Создать виджеты окна и привязать обработчик Enter."""
        self.root = root
        self.prompt = f"{get_user_host()}$ "
        root.title(f"Эмулятор - [{get_user_host()}]")
        root.geometry(WINDOW_SIZE)
        self.output = scrolledtext.ScrolledText(
            root, state="disabled", font=FONT,
            bg=BG_COLOR, fg=FG_COLOR,
        )
        self.output.pack(fill="both", expand=True)
        self.entry = tk.Entry(
            root, font=FONT, bg=BG_COLOR, fg=FG_COLOR,
            insertbackground=FG_COLOR,
        )
        self.entry.pack(fill="x")
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus_set()

    def write(self, text):
        """Добавить строку текста в область вывода."""
        self.output.configure(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.configure(state="disabled")
        self.output.see(tk.END)

    def start(self, config):
        """Вывести параметры запуска и выполнить стартовый скрипт."""
        self.write("[debug] Параметры запуска:")
        self.write(f"[debug]   vfs    = {config.vfs}")
        self.write(f"[debug]   script = {config.script}")
        if config.script:
            self.run_script(config.script)

    def run_script(self, path):
        """Выполнить стартовый скрипт построчно.

        Строки с ошибками пропускаются, о каждой ошибке сообщается
        с указанием файла и номера строки.
        """
        try:
            lines = read_script(path)
        except ShellError as error:
            self.write(f"Ошибка: {error}")
            return
        self.write(f"[script] Выполнение {path}")
        for number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            self.write(self.prompt + line)
            if not self.run_line(line, f"{path}:{number}: "):
                return
        self.write("[script] Готово")

    def on_enter(self, _event):
        """Обработать Enter: выполнить каждую введённую строку."""
        text = self.entry.get()
        self.entry.delete(0, tk.END)
        for line in text.splitlines() or [""]:
            self.write(self.prompt + line)
            if not self.run_line(line):
                break

    def run_line(self, line, where=""):
        """Разобрать и выполнить строку, вывести результат или ошибку.

        where - префикс места ошибки (файл:строка) для скриптов.
        Возвращает False, если эмулятор нужно закрыть.
        """
        try:
            parsed = parse_line(line)
            if parsed is None:
                return True
            result = execute(*parsed)
        except ExitRequested:
            self.root.destroy()
            return False
        except ShellError as error:
            self.write(f"Ошибка: {where}{error}")
            return True
        if result:
            self.write(result)
        return True