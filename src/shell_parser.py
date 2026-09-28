"""Разбор строки ввода: разбиение на слова и раскрытие переменных."""

import os
import re
import shlex

from errors import ShellError

# ${VAR} или $VAR, где VAR состоит из букв, цифр и подчёркиваний.
VAR_PATTERN = re.compile(r"\$\{(\w+)\}|\$(\w+)")


def get_environment():
    """Вернуть переменные окружения реальной ОС.

    В Windows нет переменной HOME, поэтому она добавляется
    из домашнего каталога пользователя (USERPROFILE).
    """
    env = dict(os.environ)
    env.setdefault("HOME", os.path.expanduser("~"))
    return env


def expand_variables(word, env):
    """Заменить в слове $VAR и ${VAR} на значения из env.

    Неизвестная переменная заменяется пустой строкой, как в bash.
    """
    def replace(match):
        name = match.group(1) or match.group(2)
        return env.get(name, "")

    return VAR_PATTERN.sub(replace, word)


def parse_line(line, env=None):
    """Разобрать строку на имя команды и список аргументов.

    Возвращает кортеж (команда, аргументы) или None для пустой строки.
    Бросает ShellError, если кавычки не закрыты.
    """
    if env is None:
        env = get_environment()
    try:
        words = shlex.split(line)
    except ValueError as error:
        raise ShellError(f"parse error: {error}") from error
    words = [expand_variables(word, env) for word in words]
    if not words:
        return None
    return words[0], words[1:]