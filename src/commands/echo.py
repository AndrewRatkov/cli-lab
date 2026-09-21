from envscope import EnvScope
from fdtriple import FdTriple


def echo(fds: FdTriple, env: EnvScope, args: list[str]) -> int:
    fds.get_out().write(" ".join(args[1:]) + "\n")
    return 0
