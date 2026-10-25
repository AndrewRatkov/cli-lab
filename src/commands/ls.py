import io
import os

from runtime import EnvScope, FdTriple


def ls(fds: FdTriple, env: EnvScope, args: list[str]) -> int:
    out: io.TextIOWrapper = fds.get_out()
    err: io.TextIOWrapper = fds.get_err()

    if len(args) > 2:
        err.write("ls: too many arguments\n")
        return 2

    path: str = args[1] if len(args) > 1 else "."
    names: list[str] = [path]
    try:
        if os.path.isdir(path):
            names = [name for name in os.listdir(path) if not name.startswith(".")]
        else:
            os.stat(path)  # raises an error if there is no such file
    except OSError as e:
        err.write(f"ls: cannot access '{path}': {e.strerror}\n")
        return 2

    for name in sorted(names):
        out.write(name + "\n")

    out.flush()
    return 0
