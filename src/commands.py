"""Команды эмулятора. ls и cd пока являются заглушками."""

from dataclasses import dataclass

from errors import ExitRequested, ShellError

MAX_CD_ARGS = 1
INDENT = "  "


@dataclass
class ShellContext:
    """Состояние эмулятора, доступное командам."""

    vfs: object = None
    cwd: str = "/"


def format_stub(name, args):
    """Сформировать вывод заглушки: имя команды и её аргументы."""
    return f"{name}: args={args}"


def cmd_ls(args, _ctx):
    """Заглушка ls: печатает своё имя и аргументы."""
    return format_stub("ls", args)


def cmd_cd(args, _ctx):
    """Заглушка cd: печатает своё имя и аргументы."""
    if len(args) > MAX_CD_ARGS:
        raise ShellError("cd: too many arguments")
    return format_stub("cd", args)


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
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
}


def execute(name, args, ctx=None):
    """Выполнить команду name с аргументами args и вернуть вывод."""
    handler = COMMANDS.get(name)
    if handler is None:
        raise ShellError(f"{name}: command not found")
    return handler(args, ctx)