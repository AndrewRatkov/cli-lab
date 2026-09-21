import io
import shutil

from envscope import EnvScope
from fdtriple import FdTriple


def cat(fds: FdTriple, env: EnvScope, args: list[str]) -> int:
    out: io.TextIOWrapper = fds.get_out()
    err: io.TextIOWrapper = fds.get_err()
    names: list[str] = args[1:] or ["-"]
    status: int = 0

    for name in names:
        if name == "-":
            shutil.copyfileobj(fds.get_in(), out)
            continue
        try:
            with open(name, "r") as f:
                shutil.copyfileobj(f, out)
        except OSError as e:
            err.write(f"cat: {name}: {e.strerror}\n")
            status = 1

    out.flush()
    return status
