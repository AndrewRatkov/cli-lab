import io
import os

from runtime import EnvScope, FdTriple


def cd(fds: FdTriple, env: EnvScope, args: list[str]) -> int:
    err: io.TextIOWrapper = fds.get_err()

    if len(args) > 2:
        err.write("cd: too many arguments\n")
        return 1

    if len(args) == 1:
        path: str = env.get("HOME") or os.path.expanduser("~")
    elif args[1] == "-":
        path = env.get("OLDPWD")
        if not path:
            err.write("cd: OLDPWD not set\n")
            return 1
    else:
        path = args[1]

    old_path: str = os.getcwd()
    try:
        os.chdir(path)
    except OSError as e:
        err.write(f"cd: {path}: {e.strerror}\n")
        return 1

    env.set("OLDPWD", old_path)
    env.set("PWD", os.getcwd())
    if args[1:] == ["-"]:
        fds.get_out().write(os.getcwd() + "\n")
    return 0
