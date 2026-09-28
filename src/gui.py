"""Графический интерфейс эмулятора на tkinter."""

import getpass
import socket
import tkinter as tk
from tkinter import scrolledtext

from commands import execute
from errors import ExitRequested, ShellError
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

    def on_enter(self, _event):
        """Обработать Enter: выполнить каждую введённую строку."""
        text = self.entry.get()
        self.entry.delete(0, tk.END)
        for line in text.splitlines() or [""]:
            self.write(self.prompt + line)
            if not self.run_line(line):
                break

    def run_line(self, line):
        """Разобрать и выполнить строку, вывести результат или ошибку.

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
            self.write(f"Ошибка: {error}")
            return True
        if result:
            self.write(result)
        return True