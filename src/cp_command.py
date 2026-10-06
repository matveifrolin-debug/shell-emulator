"""Команда cp: копирование файлов и каталогов VFS только в памяти."""

from errors import ShellError
from fs_commands import get_node, parse_options, require_vfs
from vfs import Node, resolve_path

MIN_OPERANDS = 2
ROOT = "/"


def split_parent(full):
    """Разделить абсолютный путь на путь родительского каталога и имя."""
    parent, _, name = full.rpartition("/")
    return parent or ROOT, name


def join_path(parent, name):
    """Склеить путь каталога и имя."""
    return f"{parent.rstrip('/')}/{name}"


def copy_node(src, dst_parent, name):
    """Рекурсивно скопировать узел src в каталог dst_parent как name."""
    existing = dst_parent.children.get(name)
    if not src.is_dir:
        if existing is not None and existing.is_dir:
            raise ShellError(
                f"cp: cannot overwrite directory '{name}' with non-directory")
        dst_parent.children[name] = Node(name, False, src.data)
        return
    if existing is None:
        existing = Node(name, True)
        dst_parent.children[name] = existing
    elif not existing.is_dir:
        raise ShellError(
            f"cp: cannot overwrite non-directory '{name}' with directory")
    for child in list(src.children.values()):
        copy_node(child, existing, child.name)


def resolve_target(ctx, dest, src_name):
    """Найти каталог назначения и имя копии.

    Если dest - существующий каталог, копия кладётся в него под именем
    источника; иначе dest - путь новой копии в существующем каталоге.
    Возвращает (путь каталога, каталог, имя копии).
    """
    full = resolve_path(ctx.cwd, dest)
    node = ctx.vfs.find(full)
    if node is not None and node.is_dir:
        return full, node, src_name
    parent_path, name = split_parent(full)
    parent = ctx.vfs.find(parent_path)
    if parent is None or not parent.is_dir:
        raise ShellError(
            f"cp: cannot create '{dest}': No such file or directory")
    return parent_path, parent, name


def check_copy(src_full, src, target_full):
    """Запретить копирование каталога в себя и файла в самого себя."""
    if src.is_dir:
        prefix = src_full.rstrip("/") + "/"
        if target_full == src_full or target_full.startswith(prefix):
            raise ShellError(
                f"cp: cannot copy a directory, '{src_full}', into itself")
    elif target_full == src_full:
        raise ShellError(f"cp: '{src_full}' and '{target_full}' "
                         "are the same file")


def copy_one(ctx, source, dest, recursive):
    """Скопировать один источник в место назначения."""
    src_full, src = get_node(ctx, "cp", source)
    if src.is_dir and not recursive:
        raise ShellError(
            f"cp: -r not specified; omitting directory '{source}'")
    _, src_name = split_parent(src_full)
    parent_path, parent, name = resolve_target(ctx, dest, src_name)
    check_copy(src_full, src, join_path(parent_path, name))
    copy_node(src, parent, name)


def cmd_cp(args, ctx):
    """cp [-r] источник... назначение: копировать файлы и каталоги VFS.

    -r (-R) - копировать каталоги рекурсивно. При нескольких
    источниках назначение должно быть существующим каталогом.
    Изменения выполняются только в памяти, CSV-файл не меняется.
    """
    require_vfs(ctx, "cp")
    options, operands = parse_options("cp", args, "rR")
    if not operands:
        raise ShellError("cp: missing file operand")
    if len(operands) < MIN_OPERANDS:
        raise ShellError(
            f"cp: missing destination file operand after '{operands[0]}'")
    *sources, dest = operands
    if sources[1:]:
        node = ctx.vfs.find(resolve_path(ctx.cwd, dest))
        if node is None or not node.is_dir:
            raise ShellError(f"cp: target '{dest}' is not a directory")
    recursive = bool(options & {"r", "R"})
    for source in sources:
        copy_one(ctx, source, dest, recursive)
    return ""