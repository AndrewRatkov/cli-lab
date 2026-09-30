import re

_ASSIGN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", re.DOTALL)


def split_assignments(args: list[str]) -> tuple[list[tuple[str, str]], list[str]]:
    assigns: list[tuple[str, str]] = []
    i = 0
    while i < len(args):
        match = _ASSIGN.match(args[i])
        if not match:
            break
        assigns.append((match.group(1), match.group(2)))
        i += 1
    return assigns, args[i:]
