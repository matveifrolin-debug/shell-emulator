"""Чтение стартового скрипта эмулятора."""

from errors import ShellError


def read_script(path):
    """Прочитать стартовый скрипт и вернуть список его строк.

    Бросает ShellError, если файл не найден или не читается.
    """
    try:
        with open(path, encoding="utf-8") as file:
            return file.read().splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise ShellError(f"cannot read script: {error}") from error