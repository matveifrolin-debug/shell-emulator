"""Точка входа эмулятора оболочки ОС."""

import tkinter as tk

from config import parse_args
from gui import EmulatorApp


def main():
    """Разобрать параметры, создать окно и запустить цикл событий."""
    config = parse_args()
    root = tk.Tk()
    app = EmulatorApp(root)
    root.after(0, app.start, config)
    root.mainloop()


if __name__ == "__main__":
    main()