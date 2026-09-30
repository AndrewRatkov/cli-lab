import os
from runtime import EnvScope, FdTriple


def pwd(fds: FdTriple, env: EnvScope, args: list[str]) -> int:
    fds.get_out().write(os.getcwd() + "\n")
    return 0
