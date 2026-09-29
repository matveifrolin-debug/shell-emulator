"""Тесты этапа 2: параметры командной строки и стартовый скрипт."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import parse_args  # noqa: E402
from errors import ShellError  # noqa: E402
from script import read_script  # noqa: E402
from shell_parser import parse_line  # noqa: E402


class ConfigTest(unittest.TestCase):
    """Проверки разбора параметров командной строки."""

    def test_no_params(self):
        """Без параметров оба значения равны None."""
        config = parse_args([])
        self.assertIsNone(config.vfs)
        self.assertIsNone(config.script)

    def test_all_params(self):
        """Оба параметра считываются."""
        config = parse_args(["--vfs", "a.csv", "--script", "s.txt"])
        self.assertEqual(config.vfs, "a.csv")
        self.assertEqual(config.script, "s.txt")

    def test_unknown_param(self):
        """Неизвестный параметр приводит к завершению с ошибкой."""
        with self.assertRaises(SystemExit):
            parse_args(["--foo"])


class ScriptTest(unittest.TestCase):
    """Проверки чтения стартового скрипта."""

    def test_read_lines(self):
        """Скрипт читается построчно."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "start.txt")
            with open(path, "w", encoding="utf-8") as file:
                file.write("ls\ncd /\n")
            self.assertEqual(read_script(path), ["ls", "cd /"])

    def test_missing_script(self):
        """Отсутствующий скрипт - ошибка."""
        with self.assertRaises(ShellError):
            read_script("no_such_script.txt")

    def test_comment_line(self):
        """Строка-комментарий не является командой."""
        self.assertIsNone(parse_line("# comment", {}))

    def test_trailing_comment(self):
        """Комментарий в конце строки отбрасывается."""
        self.assertEqual(parse_line("ls -a  # list", {}), ("ls", ["-a"]))


if __name__ == "__main__":
    unittest.main()