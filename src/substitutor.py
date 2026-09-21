from envscope import envScope

from enum import Enum


SPECIAL_CHARS: str = "'\"$ "


class splitStatus(Enum):
    OK = 0
    IN_QUOTES = 1
    IN_DOUBLE_QUOTES = 2


def isSpace(ch) -> bool:
    return ch == " "


def replaceByScope(rawCmd: str, envs: envScope) -> str:
    """Replace all $ by values from envScope"""
    new_str: str = ""
    status: splitStatus = splitStatus.OK

    reading_name: bool = False
    cur_read_name: str = ""

    for ch in rawCmd:
        if ch in SPECIAL_CHARS:
            if reading_name:
                reading_name = False
                new_str += envs.Get(cur_read_name)
                cur_read_name = ""

        if isSpace(ch):
            new_str += ch
        elif ch == '"':
            if status == splitStatus.OK:
                status = splitStatus.IN_DOUBLE_QUOTES
            elif status == splitStatus.IN_DOUBLE_QUOTES:
                status = splitStatus.OK
            new_str += ch
        elif ch == "'":
            if status == splitStatus.OK:
                status = splitStatus.IN_QUOTES
            elif status == splitStatus.IN_QUOTES:
                status = splitStatus.OK
            new_str += ch
        elif ch == "$":
            if status == splitStatus.IN_QUOTES:
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
        new_str += envs.Get(cur_read_name)

    return new_str


def splitIntoArguments(rawCmd: str, envs: envScope) -> list[str]:
    """Parse command into list of arguments"""
    s = replaceByScope(rawCmd, envs)

    cur_str: str = ""
    args: list[str] = []
    status: splitStatus = splitStatus.OK

    for ch in s:
        if isSpace(ch):
            if status == splitStatus.OK:
                if len(cur_str) > 0:
                    args.append(cur_str)
                    cur_str = ""
            else:
                cur_str += ch
        elif ch == '"':
            if status == splitStatus.OK:
                status = splitStatus.IN_DOUBLE_QUOTES
            elif status == splitStatus.IN_DOUBLE_QUOTES:
                status = splitStatus.OK
            else:
                cur_str += ch
        elif ch == "'":
            if status == splitStatus.OK:
                status = splitStatus.IN_QUOTES
            elif status == splitStatus.IN_QUOTES:
                status = splitStatus.OK
            else:
                cur_str += ch
        else:
            cur_str += ch

    if status != splitStatus.OK:
        raise EOFError("Quotes not closed")

    if len(cur_str) > 0:
        args.append(cur_str)

    return args
