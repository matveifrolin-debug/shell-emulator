"""Параметры командной строки эмулятора."""

import argparse


def parse_args(argv=None):
    """Разобрать параметры командной строки.

    --vfs     путь к физическому расположению VFS;
    --script  путь к стартовому скрипту.
    """
    parser = argparse.ArgumentParser(
        description="Эмулятор командной строки UNIX с GUI",
    )
    parser.add_argument("--vfs", help="путь к физическому расположению VFS")
    parser.add_argument("--script", help="путь к стартовому скрипту")
    return parser.parse_args(argv)