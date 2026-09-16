from envscope import envScope
from fdtriple import fdTriple


def echo(fds: fdTriple, env: envScope, args: list[str]) -> int:
    fds.GetOut().write(" ".join(args[1:]) + "\n")
    return 0
