"""Тесты этапа 1: парсер и команды-заглушки."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from commands import execute  # noqa: E402
from errors import ExitRequested, ShellError  # noqa: E402
from shell_parser import parse_line  # noqa: E402

ENV = {"HOME": "/home/user", "USER": "user"}


class ParserTest(unittest.TestCase):
    """Проверки разбора строки и раскрытия переменных."""

    def test_split(self):
        """Строка делится на команду и аргументы."""
        self.assertEqual(parse_line("ls -l /tmp", ENV),
                         ("ls", ["-l", "/tmp"]))

    def test_empty_line(self):
        """Пустая строка не является командой."""
        self.assertIsNone(parse_line("   ", ENV))

    def test_expand_home(self):
        """$HOME и ${USER} раскрываются."""
        self.assertEqual(parse_line("cd $HOME/${USER}", ENV),
                         ("cd", ["/home/user/user"]))

    def test_unknown_variable(self):
        """Неизвестная переменная заменяется пустой строкой."""
        self.assertEqual(parse_line("ls $NOPE", ENV), ("ls", [""]))

    def test_quotes(self):
        """Аргумент в кавычках с пробелом остаётся одним словом."""
        self.assertEqual(parse_line('ls "my dir"', ENV),
                         ("ls", ["my dir"]))

    def test_unclosed_quote(self):
        """Незакрытая кавычка приводит к ошибке."""
        with self.assertRaises(ShellError):
            parse_line('ls "abc', ENV)


class CommandsTest(unittest.TestCase):
    """Проверки команд-заглушек."""

    def test_ls_without_vfs(self):
        """ls без загруженной VFS - ошибка."""
        with self.assertRaises(ShellError):
            execute("ls", [])

    def test_cd_too_many(self):
        """cd с двумя аргументами - ошибка."""
        with self.assertRaises(ShellError):
            execute("cd", ["a", "b"])

    def test_unknown_command(self):
        """Неизвестная команда - ошибка."""
        with self.assertRaises(ShellError):
            execute("foo", [])

    def test_exit(self):
        """exit сигнализирует о завершении."""
        with self.assertRaises(ExitRequested):
            execute("exit", [])


if __name__ == "__main__":
    unittest.main()