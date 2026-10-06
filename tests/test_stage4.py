"""Тесты этапа 4: команды ls, cd, du, uniq."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from commands import ShellContext, execute  # noqa: E402
from errors import ShellError  # noqa: E402
from vfs import load_vfs, resolve_path  # noqa: E402

DEEP = os.path.join(os.path.dirname(__file__), "..", "vfs", "deep.csv")


def make_context():
    """Создать контекст с загруженной VFS deep.csv."""
    return ShellContext(vfs=load_vfs(DEEP))


class ResolvePathTest(unittest.TestCase):
    """Проверки преобразования путей."""

    def test_relative(self):
        """Относительный путь считается от текущего каталога."""
        self.assertEqual(resolve_path("/home", "user"), "/home/user")

    def test_parent(self):
        """.. поднимается на уровень выше, но не выше корня."""
        self.assertEqual(resolve_path("/home/user", ".."), "/home")
        self.assertEqual(resolve_path("/", "../.."), "/")

    def test_absolute(self):
        """Абсолютный путь не зависит от текущего каталога."""
        self.assertEqual(resolve_path("/home", "/etc/./x"), "/etc/x")


class LsTest(unittest.TestCase):
    """Проверки команды ls."""

    def setUp(self):
        """Подготовить контекст."""
        self.ctx = make_context()

    def test_root(self):
        """ls без аргументов выводит текущий каталог."""
        self.assertEqual(execute("ls", [], self.ctx),
                         "bin\netc\nhome\ntmp")

    def test_path(self):
        """ls с путём к каталогу."""
        output = execute("ls", ["/home/user"], self.ctx)
        self.assertEqual(output, "empty.txt\nnotes.txt\nprojects")

    def test_long(self):
        """ls -l выводит тип и размер."""
        output = execute("ls", ["-l", "/etc"], self.ctx)
        self.assertEqual(output, "-        8 hostname")

    def test_file(self):
        """ls для файла выводит его имя."""
        self.assertEqual(execute("ls", ["/etc/hostname"], self.ctx),
                         "hostname")

    def test_several(self):
        """Несколько каталогов выводятся с заголовками."""
        output = execute("ls", ["/etc", "/tmp"], self.ctx)
        self.assertEqual(output, "/etc:\nhostname\n\n/tmp:")

    def test_not_found(self):
        """Несуществующий путь - ошибка."""
        with self.assertRaises(ShellError):
            execute("ls", ["/nope"], self.ctx)

    def test_bad_option(self):
        """Неизвестная опция - ошибка."""
        with self.assertRaises(ShellError):
            execute("ls", ["-x"], self.ctx)


class CdTest(unittest.TestCase):
    """Проверки команды cd."""

    def setUp(self):
        """Подготовить контекст."""
        self.ctx = make_context()

    def test_absolute_and_relative(self):
        """cd по абсолютному и относительному пути."""
        execute("cd", ["/home"], self.ctx)
        execute("cd", ["user/projects"], self.ctx)
        self.assertEqual(self.ctx.cwd, "/home/user/projects")

    def test_parent_and_root(self):
        """cd .. и cd без аргументов."""
        execute("cd", ["/home/user"], self.ctx)
        execute("cd", [".."], self.ctx)
        self.assertEqual(self.ctx.cwd, "/home")
        execute("cd", [], self.ctx)
        self.assertEqual(self.ctx.cwd, "/")

    def test_errors(self):
        """cd в файл, несуществующий путь и лишние аргументы."""
        for args in (["/etc/hostname"], ["/nope"], ["a", "b"]):
            with self.assertRaises(ShellError):
                execute("cd", args, self.ctx)
        self.assertEqual(self.ctx.cwd, "/")


class DuTest(unittest.TestCase):
    """Проверки команды du."""

    def setUp(self):
        """Подготовить контекст."""
        self.ctx = make_context()

    def test_summary(self):
        """du -s выводит только итог."""
        self.assertEqual(execute("du", ["-s", "/home"], self.ctx),
                         "42      /home")

    def test_recursive(self):
        """du выводит вложенные каталоги и итог."""
        lines = execute("du", ["/home/user"], self.ctx).splitlines()
        self.assertEqual(lines[-1], "42      /home/user")
        self.assertIn("11      /home/user/projects/shell", lines)

    def test_all(self):
        """du -a выводит и файлы."""
        output = execute("du", ["-a", "/etc"], self.ctx)
        self.assertEqual(output, "8       /etc/hostname\n8       /etc")

    def test_conflict(self):
        """-a и -s вместе - ошибка."""
        with self.assertRaises(ShellError):
            execute("du", ["-as"], self.ctx)


class UniqTest(unittest.TestCase):
    """Проверки команды uniq."""

    def setUp(self):
        """Подготовить контекст."""
        self.ctx = make_context()
        self.path = "/home/user/notes.txt"

    def test_plain(self):
        """Соседние повторы удаляются."""
        self.assertEqual(execute("uniq", [self.path], self.ctx),
                         "apple\nbanana\napple")

    def test_count(self):
        """-c выводит число повторов."""
        output = execute("uniq", ["-c", self.path], self.ctx)
        self.assertEqual(output.split(), ["2", "apple", "2", "banana",
                                          "1", "apple"])

    def test_duplicated_and_unique(self):
        """-d и -u."""
        self.assertEqual(execute("uniq", ["-d", self.path], self.ctx),
                         "apple\nbanana")
        self.assertEqual(execute("uniq", ["-u", self.path], self.ctx),
                         "apple")

    def test_errors(self):
        """Нет файла, каталог, двоичный файл, лишний операнд."""
        for args in ([], ["/home"], ["/bin/tool.bin"],
                     [self.path, "x"], ["/nope"]):
            with self.assertRaises(ShellError):
                execute("uniq", args, self.ctx)


if __name__ == "__main__":
    unittest.main()