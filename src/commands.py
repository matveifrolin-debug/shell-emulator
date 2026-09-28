"""Команды эмулятора. На этапе 1 ls и cd являются заглушками."""

from errors import ExitRequested, ShellError

MAX_CD_ARGS = 1


def format_stub(name, args):
    """Сформировать вывод заглушки: имя команды и её аргументы."""
    return f"{name}: args={args}"


def cmd_ls(args):
    """Заглушка ls: печатает своё имя и аргументы."""
    return format_stub("ls", args)


def cmd_cd(args):
    """Заглушка cd: печатает своё имя и аргументы."""
    if len(args) > MAX_CD_ARGS:
        raise ShellError("cd: too many arguments")
    return format_stub("cd", args)


def cmd_exit(args):
    """Завершить работу эмулятора."""
    if args:
        raise ShellError("exit: too many arguments")
    raise ExitRequested()


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}


def execute(name, args):
    """Выполнить команду name с аргументами args и вернуть вывод."""
    handler = COMMANDS.get(name)
    if handler is None:
        raise ShellError(f"{name}: command not found")
    return handler(args)