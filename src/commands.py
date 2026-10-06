"""Реестр команд эмулятора и общие команды (exit, vfs-info)."""

from dataclasses import dataclass

from errors import ExitRequested, ShellError
from fs_commands import cmd_cd, cmd_du, cmd_ls, cmd_uniq

INDENT = "  "


@dataclass
class ShellContext:
    """Состояние эмулятора, доступное командам."""

    vfs: object = None
    cwd: str = "/"


def cmd_exit(args, _ctx):
    """Завершить работу эмулятора."""
    if args:
        raise ShellError("exit: too many arguments")
    raise ExitRequested()


def format_node(vfs, depth, node):
    """Сформировать строку дерева VFS для одного узла."""
    indent = INDENT * depth
    if node is vfs.root:
        return "/"
    if node.is_dir:
        return f"{indent}{node.name}/"
    return f"{indent}{node.name} ({len(node.data)} bytes)"


def cmd_vfs_info(args, ctx):
    """Служебная команда: сведения о загруженной VFS и её дерево."""
    if args:
        raise ShellError("vfs-info: too many arguments")
    if ctx is None or ctx.vfs is None:
        raise ShellError("vfs-info: VFS is not loaded")
    vfs = ctx.vfs
    dirs, files = vfs.stats()
    lines = [f"VFS '{vfs.name}': {dirs} dirs, {files} files"]
    lines += [format_node(vfs, depth, node) for depth, node in vfs.walk()]
    return "\n".join(lines)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "du": cmd_du,
    "uniq": cmd_uniq,
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
}


def execute(name, args, ctx=None):
    """Выполнить команду name с аргументами args и вернуть вывод."""
    handler = COMMANDS.get(name)
    if handler is None:
        raise ShellError(f"{name}: command not found")
    return handler(args, ctx)