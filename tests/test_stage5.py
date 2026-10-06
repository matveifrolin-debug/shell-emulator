"""Тесты этапа 5: команда cp."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from commands import ShellContext, execute  # noqa: E402
from errors import ShellError  # noqa: E402
from vfs import load_vfs  # noqa: E402

DEEP = os.path.join(os.path.dirname(__file__), "..", "vfs", "deep.csv")


class CpTest(unittest.TestCase):
    """Проверки успешного копирования."""

    def setUp(self):
        """Подготовить контекст с VFS deep.csv."""
        self.ctx = ShellContext(vfs=load_vfs(DEEP))
        self.vfs = self.ctx.vfs

    def test_file_into_dir(self):
        """Файл копируется в каталог под своим именем."""
        execute("cp", ["/etc/hostname", "/tmp"], self.ctx)
        self.assertEqual(self.vfs.find("/tmp/hostname").data, b"emulator")

    def test_file_new_name(self):
        """Файл копируется под новым именем."""
        execute("cp", ["/etc/hostname", "/tmp/name.txt"], self.ctx)
        self.assertIsNotNone(self.vfs.find("/tmp/name.txt"))

    def test_overwrite(self):
        """Существующий файл перезаписывается."""
        execute("cp", ["/etc/hostname", "/home/user/notes.txt"], self.ctx)
        node = self.vfs.find("/home/user/notes.txt")
        self.assertEqual(node.data, b"emulator")

    def test_several_files(self):
        """Несколько файлов копируются в каталог."""
        execute("cp", ["/etc/hostname", "/bin/tool.bin", "/tmp"], self.ctx)
        self.assertEqual(execute("ls", ["/tmp"], self.ctx),
                         "hostname\ntool.bin")

    def test_recursive(self):
        """Каталог копируется рекурсивно с -r."""
        execute("cp", ["-r", "/home/user/projects", "/tmp"], self.ctx)
        node = self.vfs.find("/tmp/projects/shell/main.py")
        self.assertEqual(node.data, b"print('hi')")

    def test_copy_is_independent(self):
        """Изменение копии не затрагивает оригинал."""
        execute("cp", ["-r", "/home/user/projects", "/tmp"], self.ctx)
        execute("cp", ["/etc/hostname", "/tmp/projects/shell/main.py"],
                self.ctx)
        original = self.vfs.find("/home/user/projects/shell/main.py")
        self.assertEqual(original.data, b"print('hi')")

    def test_relative(self):
        """Относительные пути считаются от текущего каталога."""
        execute("cd", ["/home/user"], self.ctx)
        execute("cp", ["notes.txt", "copy.txt"], self.ctx)
        self.assertIsNotNone(self.vfs.find("/home/user/copy.txt"))

    def test_csv_unchanged(self):
        """CSV-файл не меняется: повторная загрузка даёт исходную VFS."""
        execute("cp", ["-r", "/home", "/tmp"], self.ctx)
        self.assertEqual(load_vfs(DEEP).stats(), (7, 5))


class CpErrorTest(unittest.TestCase):
    """Проверки ошибок cp."""

    def setUp(self):
        """Подготовить контекст с VFS deep.csv."""
        self.ctx = ShellContext(vfs=load_vfs(DEEP))

    def assert_error(self, args):
        """Убедиться, что cp с аргументами args завершается ошибкой."""
        with self.assertRaises(ShellError):
            execute("cp", args, self.ctx)

    def test_operands(self):
        """Нет операндов или нет назначения."""
        self.assert_error([])
        self.assert_error(["/etc/hostname"])

    def test_not_found(self):
        """Источник не найден, каталог назначения не существует."""
        self.assert_error(["/nope", "/tmp"])
        self.assert_error(["/etc/hostname", "/nope/x"])

    def test_dir_without_r(self):
        """Каталог без -r не копируется."""
        self.assert_error(["/home", "/tmp"])

    def test_into_itself(self):
        """Каталог нельзя скопировать в самого себя."""
        self.assert_error(["-r", "/home", "/home/user"])

    def test_same_file(self):
        """Файл нельзя скопировать в самого себя."""
        self.assert_error(["/etc/hostname", "/etc"])

    def test_several_to_file(self):
        """Несколько источников требуют каталог назначения."""
        self.assert_error(["/etc/hostname", "/bin/tool.bin",
                           "/etc/hostname"])

    def test_dir_over_file(self):
        """Каталог нельзя записать поверх файла."""
        self.assert_error(["-r", "/bin", "/etc/hostname"])

    def test_bad_option(self):
        """Неизвестная опция."""
        self.assert_error(["-x", "/etc/hostname", "/tmp"])

    def test_no_vfs(self):
        """Без VFS - ошибка."""
        with self.assertRaises(ShellError):
            execute("cp", ["/a", "/b"], ShellContext())


if __name__ == "__main__":
    unittest.main()