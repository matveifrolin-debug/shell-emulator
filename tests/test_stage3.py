"""Тесты этапа 3: загрузка VFS из CSV и служебная команда vfs-info."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from commands import ShellContext, execute  # noqa: E402
from errors import ShellError  # noqa: E402
from vfs import VfsError, load_vfs  # noqa: E402

VFS_DIR = os.path.join(os.path.dirname(__file__), "..", "vfs")
HEADER = "path,type,content\n"


def load_text(text):
    """Записать text во временный CSV-файл и загрузить из него VFS."""
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "test.csv")
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
        return load_vfs(path)


class LoadTest(unittest.TestCase):
    """Проверки загрузки корректных VFS."""

    def test_minimal(self):
        """Минимальная VFS содержит только корень."""
        vfs = load_vfs(os.path.join(VFS_DIR, "minimal.csv"))
        self.assertEqual(vfs.stats(), (0, 0))

    def test_several(self):
        """VFS с несколькими файлами."""
        vfs = load_vfs(os.path.join(VFS_DIR, "several.csv"))
        self.assertEqual(vfs.stats(), (1, 3))
        self.assertEqual(vfs.find("/hello.txt").data, b"Hello, world!")

    def test_deep(self):
        """VFS с вложенностью не менее 3 уровней и двоичным файлом."""
        vfs = load_vfs(os.path.join(VFS_DIR, "deep.csv"))
        node = vfs.find("/home/user/projects/shell/main.py")
        self.assertIsNotNone(node)
        self.assertFalse(node.is_dir)
        binary = vfs.find("/bin/tool.bin").data
        self.assertTrue(binary.startswith(b"\x89PNG"))

    def test_parent_dirs_created(self):
        """Недостающие родительские каталоги создаются автоматически."""
        vfs = load_text(HEADER + "/a/b/c.txt,file,\n")
        self.assertTrue(vfs.find("/a/b").is_dir)

    def test_find_missing(self):
        """Несуществующий путь не найден."""
        vfs = load_text(HEADER)
        self.assertIsNone(vfs.find("/nope"))


class LoadErrorTest(unittest.TestCase):
    """Проверки ошибок загрузки VFS."""

    def assert_error(self, text):
        """Убедиться, что загрузка text приводит к VfsError."""
        with self.assertRaises(VfsError):
            load_text(text)

    def test_not_found(self):
        """Файл VFS не найден."""
        with self.assertRaises(VfsError):
            load_vfs("no_such_vfs.csv")

    def test_bad_header(self):
        """Неверный заголовок CSV."""
        self.assert_error("name,kind\n/a,dir\n")

    def test_empty_file(self):
        """Пустой файл без заголовка."""
        self.assert_error("")

    def test_unknown_type(self):
        """Неизвестный тип узла."""
        self.assert_error(HEADER + "/a,link,\n")

    def test_bad_base64(self):
        """Некорректное содержимое base64."""
        self.assert_error(HEADER + "/a.txt,file,@@@\n")

    def test_relative_path(self):
        """Путь должен быть абсолютным."""
        self.assert_error(HEADER + "a.txt,file,\n")

    def test_wrong_columns(self):
        """Неверное число столбцов."""
        self.assert_error(HEADER + "/a,dir\n")

    def test_file_as_dir(self):
        """Файл нельзя использовать как каталог."""
        self.assert_error(HEADER + "/a,file,\n/a/b,file,\n")

    def test_duplicate(self):
        """Повторяющийся путь."""
        self.assert_error(HEADER + "/a,file,\n/a,file,\n")

    def test_broken_example(self):
        """Пример vfs/broken.csv не загружается."""
        with self.assertRaises(VfsError):
            load_vfs(os.path.join(VFS_DIR, "broken.csv"))


class VfsInfoTest(unittest.TestCase):
    """Проверки служебной команды vfs-info."""

    def test_info(self):
        """vfs-info выводит статистику и дерево."""
        vfs = load_text(HEADER + "/d,dir,\n/d/f.txt,file,YWJj\n")
        output = execute("vfs-info", [], ShellContext(vfs=vfs))
        self.assertIn("1 dirs, 1 files", output)
        self.assertIn("    f.txt (3 bytes)", output)

    def test_not_loaded(self):
        """vfs-info без загруженной VFS - ошибка."""
        with self.assertRaises(ShellError):
            execute("vfs-info", [], ShellContext())


if __name__ == "__main__":
    unittest.main()