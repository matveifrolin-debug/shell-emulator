"""Команды работы с VFS: ls, cd, du, uniq."""

from errors import ShellError
from vfs import node_size, resolve_path

MAX_CD_ARGS = 1
UNIQUE_COUNT = 1
COUNT_WIDTH = 7
SIZE_WIDTH = 8
ROOT = "/"


def require_vfs(ctx, name):
    """Вернуть загруженную VFS или сообщить, что её нет."""
    if ctx is None or ctx.vfs is None:
        raise ShellError(f"{name}: VFS is not loaded")
    return ctx.vfs


def parse_options(name, args, allowed):
    """Разделить аргументы на набор однобуквенных опций и операнды."""
    options, operands = set(), []
    for arg in args:
        if arg.startswith("-") and arg != "-":
            for letter in arg[1:]:
                if letter not in allowed:
                    raise ShellError(f"{name}: invalid option -- '{letter}'")
                options.add(letter)
        else:
            operands.append(arg)
    return options, operands


def get_node(ctx, name, path):
    """Найти узел VFS по пути; вернуть (абсолютный путь, узел)."""
    full = resolve_path(ctx.cwd, path)
    node = ctx.vfs.find(full)
    if node is None:
        raise ShellError(f"{name}: {path}: No such file or directory")
    return full, node


def sorted_children(node):
    """Вернуть дочерние узлы каталога, отсортированные по имени."""
    return sorted(node.children.values(), key=lambda child: child.name)


def format_entry(node, long_format):
    """Сформировать строку ls для одного узла."""
    if not long_format:
        return node.name
    kind = "d" if node.is_dir else "-"
    return f"{kind} {node_size(node):>{SIZE_WIDTH}} {node.name}"


def list_target(ctx, path, long_format, show_header):
    """Сформировать вывод ls для одного операнда."""
    _, node = get_node(ctx, "ls", path)
    if not node.is_dir:
        return format_entry(node, long_format)
    lines = [format_entry(child, long_format)
             for child in sorted_children(node)]
    if show_header:
        lines.insert(0, f"{path}:")
    return "\n".join(lines)


def cmd_ls(args, ctx):
    """ls [-l] [путь...]: вывести содержимое каталогов VFS.

    -l - подробный формат: тип (d/-), размер в байтах, имя.
    """
    require_vfs(ctx, "ls")
    options, operands = parse_options("ls", args, "l")
    targets = operands or [ctx.cwd]
    show_header = bool(targets[1:])
    blocks = [list_target(ctx, path, "l" in options, show_header)
              for path in targets]
    return "\n\n".join(blocks) if show_header else blocks[0]


def cmd_cd(args, ctx):
    """cd [путь]: сменить текущий каталог VFS (без аргумента - /)."""
    if len(args) > MAX_CD_ARGS:
        raise ShellError("cd: too many arguments")
    require_vfs(ctx, "cd")
    target = args[0] if args else ROOT
    full, node = get_node(ctx, "cd", target)
    if not node.is_dir:
        raise ShellError(f"cd: {target}: Not a directory")
    ctx.cwd = full
    return ""


def join_display(path, name):
    """Склеить путь для вывода du."""
    return f"{path.rstrip('/')}/{name}"


def format_du(size, path):
    """Сформировать строку du: размер и путь."""
    return f"{size:<{SIZE_WIDTH}}{path}"


def du_lines(node, path, options):
    """Строки du для узла: сначала вложенные элементы, затем он сам."""
    if "s" in options or not node.is_dir:
        return [format_du(node_size(node), path)]
    lines = []
    for child in sorted_children(node):
        child_path = join_display(path, child.name)
        if child.is_dir:
            lines += du_lines(child, child_path, options)
        elif "a" in options:
            lines.append(format_du(len(child.data), child_path))
    lines.append(format_du(node_size(node), path))
    return lines


def cmd_du(args, ctx):
    """du [-a|-s] [путь...]: размер файлов и каталогов VFS в байтах.

    -a - выводить также файлы; -s - только итог для каждого операнда.
    """
    require_vfs(ctx, "du")
    options, operands = parse_options("du", args, "as")
    if {"a", "s"} <= options:
        raise ShellError("du: cannot both summarize and show all entries")
    lines = []
    for path in operands or ["."]:
        _, node = get_node(ctx, "du", path)
        lines += du_lines(node, path, options)
    return "\n".join(lines)


def read_text_lines(ctx, path):
    """Прочитать текстовый файл VFS и вернуть список строк."""
    _, node = get_node(ctx, "uniq", path)
    if node.is_dir:
        raise ShellError(f"uniq: {path}: Is a directory")
    try:
        return node.data.decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise ShellError(f"uniq: {path}: binary file") from error


def group_lines(lines):
    """Сгруппировать подряд идущие одинаковые строки: [строка, число]."""
    groups = []
    for line in lines:
        if groups and groups[-1][0] == line:
            groups[-1][1] += 1
        else:
            groups.append([line, 1])
    return groups


def keep_group(count, options):
    """Проверить, выводить ли группу с учётом опций -d и -u."""
    if "d" in options and count == UNIQUE_COUNT:
        return False
    if "u" in options and count > UNIQUE_COUNT:
        return False
    return True


def cmd_uniq(args, ctx):
    """uniq [-c] [-d] [-u] файл: убрать соседние повторяющиеся строки.

    -c - показать число повторов; -d - только повторяющиеся строки;
    -u - только неповторяющиеся строки.
    """
    require_vfs(ctx, "uniq")
    options, operands = parse_options("uniq", args, "cdu")
    if not operands:
        raise ShellError("uniq: missing file operand")
    if operands[1:]:
        raise ShellError(f"uniq: extra operand '{operands[1]}'")
    groups = group_lines(read_text_lines(ctx, operands[0]))
    lines = []
    for line, count in groups:
        if not keep_group(count, options):
            continue
        prefix = f"{count:>{COUNT_WIDTH}} " if "c" in options else ""
        lines.append(prefix + line)
    return "\n".join(lines)