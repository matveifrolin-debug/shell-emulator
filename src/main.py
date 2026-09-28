"""Точка входа эмулятора оболочки ОС."""

import tkinter as tk

from gui import EmulatorApp


def main():
    """Создать окно эмулятора и запустить цикл обработки событий."""
    root = tk.Tk()
    EmulatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()