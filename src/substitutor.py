from envscope import EnvScope

from enum import Enum


SPECIAL_CHARS: str = "'\"$ "


class SplitStatus(Enum):
    OK = 0
    IN_QUOTES = 1
    IN_DOUBLE_QUOTES = 2


def is_space(ch) -> bool:
    return ch == " "


def replace_by_scope(raw_cmd: str, envs: EnvScope) -> str:
    """Replace all $ by values from EnvScope"""
    new_str: str = ""
    status: SplitStatus = SplitStatus.OK

    reading_name: bool = False
    cur_read_name: str = ""

    for ch in raw_cmd:
        if ch in SPECIAL_CHARS:
            if reading_name:
                reading_name = False
                new_str += envs.get(cur_read_name)
                cur_read_name = ""

        if is_space(ch):
            new_str += ch
        elif ch == '"':
            if status == SplitStatus.OK:
                status = SplitStatus.IN_DOUBLE_QUOTES
            elif status == SplitStatus.IN_DOUBLE_QUOTES:
                status = SplitStatus.OK
            new_str += ch
        elif ch == "'":
            if status == SplitStatus.OK:
                status = SplitStatus.IN_QUOTES
            elif status == SplitStatus.IN_QUOTES:
                status = SplitStatus.OK
            new_str += ch
        elif ch == "$":
            if status == SplitStatus.IN_QUOTES:
                new_str += ch
            else:
                reading_name = True
        else:
            if reading_name:
                cur_read_name += ch
            else:
                new_str += ch

    if reading_name:
        reading_name = False
        new_str += envs.get(cur_read_name)

    return new_str


def split_into_arguments(raw_cmd: str, envs: EnvScope) -> list[str]:
    """Parse command into list of arguments"""
    s = replace_by_scope(raw_cmd, envs)

    cur_str: str = ""
    args: list[str] = []
    status: SplitStatus = SplitStatus.OK

    for ch in s:
        if is_space(ch):
            if status == SplitStatus.OK:
                if len(cur_str) > 0:
                    args.append(cur_str)
                    cur_str = ""
            else:
                cur_str += ch
        elif ch == '"':
            if status == SplitStatus.OK:
                status = SplitStatus.IN_DOUBLE_QUOTES
            elif status == SplitStatus.IN_DOUBLE_QUOTES:
                status = SplitStatus.OK
            else:
                cur_str += ch
        elif ch == "'":
            if status == SplitStatus.OK:
                status = SplitStatus.IN_QUOTES
            elif status == SplitStatus.IN_QUOTES:
                status = SplitStatus.OK
            else:
                cur_str += ch
        else:
            cur_str += ch

    if status != SplitStatus.OK:
        raise EOFError("Quotes not closed")

    if len(cur_str) > 0:
        args.append(cur_str)

    return args
