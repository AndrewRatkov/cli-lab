import argparse
import io
import re
from collections.abc import Iterable

from runtime import EnvScope, FdTriple


class _UsageError(Exception):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise _UsageError(message)


def _make_parser() -> _Parser:
    parser = _Parser(
        prog="grep",
        usage="grep [-w] PATTERN [FILE...]",
        add_help=False,
    )
    parser.add_argument(
        "-w", "--word-regexp", action="store_true", help="match whole words only"
    )
    parser.add_argument("-h", "--help", action="store_true", help="print usage")
    parser.add_argument("pattern", nargs="?", metavar="PATTERN")
    parser.add_argument("files", nargs="*", metavar="FILE")
    return parser


_PARSER: _Parser = _make_parser()


def _search(
    lines: Iterable[str],
    regex: re.Pattern[str],
    prefix: str,
    out: io.TextIOWrapper,
) -> bool:
    found = False
    for line in lines:
        if regex.search(line.rstrip("\n")):
            found = True
            out.write(prefix + line if line.endswith("\n") else prefix + line + "\n")
    return found


def grep(fds: FdTriple, env: EnvScope, args: list[str]) -> int:
    out: io.TextIOWrapper = fds.get_out()
    err: io.TextIOWrapper = fds.get_err()

    try:
        opts = _PARSER.parse_args(args[1:])
        if opts.help:
            out.write(_PARSER.format_help())
            return 0
        if opts.pattern is None:
            raise _UsageError("the following arguments are required: PATTERN")
    except (_UsageError, argparse.ArgumentError) as e:
        err.write(_PARSER.format_usage())
        err.write(f"grep: {e}\n")
        return 2

    pattern: str = opts.pattern
    if opts.word_regexp:
        pattern = rf"\b(?:{pattern})\b"
    try:
        regex = re.compile(pattern)
    except re.error as e:
        err.write(f"grep: invalid pattern: {e}\n")
        return 2

    names: list[str] = opts.files
    with_names = len(names) > 1
    found = False
    error = False

    if len(names) == 0:
        found = _search(fds.get_in(), regex, "", out)

    for name in names:
        prefix = f"{name}:" if with_names else ""
        try:
            if name == "-":
                found |= _search(fds.get_in(), regex, prefix, out)
                continue
            with open(name, "r", encoding="utf-8") as f:
                found |= _search(f, regex, prefix, out)
        except OSError as e:
            err.write(f"grep: {name}: {e.strerror}\n")
            error = True
        except UnicodeDecodeError:
            err.write(f"grep: {name}: binary file or unsupported encoding\n")
            error = True

    out.flush()
    if error:
        return 2
    return 0 if found else 1
