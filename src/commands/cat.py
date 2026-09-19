import io
import shutil

from src.envscope import envScope
from src.fdtriple import fdTriple


def cat(fds: fdTriple, env: envScope, args: list[str]) -> int:
    out: io.TextIOWrapper = fds.GetOut()
    err: io.TextIOWrapper = fds.GetErr()
    names: list[str] = args[1:] or ["-"]
    status: int = 0

    for name in names:
        if name == "-":
            shutil.copyfileobj(fds.GetIn(), out)
            continue
        try:
            with open(name, "r") as f:
                shutil.copyfileobj(f, out)
        except OSError as e:
            err.write(f"cat: {name}: {e.strerror}\n")
            status = 1

    out.flush()
    return status
