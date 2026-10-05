"""Виртуальная файловая система (VFS), загружаемая из CSV-файла.

Формат CSV: заголовок path,type,content и по строке на узел.
path    - абсолютный путь внутри VFS (вложенность задаётся путём);
type    - dir (каталог) или file (файл);
content - содержимое файла в base64 (для каталога пусто).
"""

import base64
import binascii
import csv
import os
from dataclasses import dataclass, field

from errors import ShellError

CSV_FIELDS = ["path", "type", "content"]
TYPE_DIR = "dir"
TYPE_FILE = "file"


class VfsError(ShellError):
    """Ошибка загрузки или обработки VFS."""


@dataclass
class Node:
    """Узел VFS: каталог или файл."""

    name: str
    is_dir: bool
    data: bytes = b""
    children: dict = field(default_factory=dict)


def split_path(path):
    """Разбить абсолютный путь VFS на список имён."""
    if not path.startswith("/"):
        raise VfsError(f"path must be absolute: '{path}'")
    parts = [part for part in path.split("/") if part]
    if any(part in (".", "..") for part in parts):
        raise VfsError(f"invalid path: '{path}'")
    return parts


class Vfs:
    """Дерево VFS, полностью хранящееся в памяти."""

    def __init__(self, name):
        """Создать пустую VFS с корневым каталогом."""
        self.name = name
        self.root = Node("/", True)

    def add(self, path, is_dir, data=b""):
        """Добавить узел, создав недостающие родительские каталоги."""
        parts = split_path(path)
        if not parts:
            raise VfsError("root '/' cannot be redefined")
        parent = self.root
        for part in parts[:-1]:
            parent = self._child_dir(parent, part, path)
        name = parts[-1]
        existing = parent.children.get(name)
        if existing is not None:
            if existing.is_dir and is_dir:
                return
            raise VfsError(f"duplicate path: '{path}'")
        parent.children[name] = Node(name, is_dir, data)

    @staticmethod
    def _child_dir(parent, name, path):
        """Вернуть подкаталог name, создав его при необходимости."""
        node = parent.children.get(name)
        if node is None:
            node = Node(name, True)
            parent.children[name] = node
        if not node.is_dir:
            raise VfsError(f"not a directory: '{name}' in '{path}'")
        return node

    def find(self, path):
        """Найти узел по абсолютному пути или вернуть None."""
        node = self.root
        for part in split_path(path):
            if not node.is_dir or part not in node.children:
                return None
            node = node.children[part]
        return node

    def walk(self):
        """Обойти дерево в глубину, возвращая пары (глубина, узел)."""
        stack = [(0, self.root)]
        while stack:
            depth, node = stack.pop()
            yield depth, node
            children = sorted(node.children.values(),
                              key=lambda child: child.name, reverse=True)
            stack.extend((depth + 1, child) for child in children)

    def stats(self):
        """Вернуть (число каталогов, число файлов) без учёта корня."""
        nodes = [node for _, node in self.walk() if node is not self.root]
        dirs = sum(1 for node in nodes if node.is_dir)
        return dirs, len(nodes) - dirs


def decode_content(content):
    """Декодировать содержимое файла из base64."""
    try:
        return base64.b64decode(content, validate=True)
    except binascii.Error as error:
        raise VfsError(f"invalid base64 content: {error}") from error


def add_row(vfs, row):
    """Добавить в VFS узел, описанный одной строкой CSV."""
    if len(row) != len(CSV_FIELDS):
        raise VfsError(
            f"expected {len(CSV_FIELDS)} columns, got {len(row)}")
    path, kind, content = row
    if kind == TYPE_DIR:
        if content:
            raise VfsError(f"directory cannot have content: '{path}'")
        vfs.add(path, True)
    elif kind == TYPE_FILE:
        vfs.add(path, False, decode_content(content))
    else:
        raise VfsError(f"unknown type '{kind}' (expected dir or file)")


def read_rows(path):
    """Прочитать строки CSV-файла VFS."""
    try:
        with open(path, encoding="utf-8-sig", newline="") as file:
            return list(csv.reader(file))
    except FileNotFoundError as error:
        raise VfsError(f"VFS file not found: '{path}'") from error
    except (OSError, UnicodeDecodeError, csv.Error) as error:
        raise VfsError(f"cannot read VFS '{path}': {error}") from error


def load_vfs(path):
    """Загрузить VFS из CSV-файла. Бросает VfsError при ошибке."""
    rows = read_rows(path)
    if not rows or rows[0] != CSV_FIELDS:
        header = ",".join(CSV_FIELDS)
        raise VfsError(f"{path}: invalid format, header must be: {header}")
    name = os.path.splitext(os.path.basename(path))[0]
    vfs = Vfs(name)
    for number, row in enumerate(rows[1:], start=2):
        if not row:
            continue
        try:
            add_row(vfs, row)
        except VfsError as error:
            raise VfsError(f"{path}:{number}: {error}") from error
    return vfs