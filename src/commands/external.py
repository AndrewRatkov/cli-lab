import io
import subprocess

from runtime import EnvScope, FdTriple


def _has_fileno(stream) -> bool:
    try:
        stream.fileno()
        return True
    except (OSError, AttributeError, io.UnsupportedOperation):
        return False


def external(fds: FdTriple, env: EnvScope, args: list[str]) -> int:
    in_fd = fds.get_in()
    out_fd = fds.get_out()
    err_fd = fds.get_err()

    out_fd.flush()
    err_fd.flush()

    out_real = _has_fileno(out_fd)
    err_real = _has_fileno(err_fd)

    stdin = None
    input_data = None
    if _has_fileno(in_fd):
        stdin = in_fd
    else:
        input_data = in_fd.read().encode("utf-8")

    stdout = subprocess.PIPE
    if out_real:
        stdout = out_fd

    stderr = subprocess.PIPE
    if err_real:
        stderr = err_fd

    try:
        proc = subprocess.run(
            args,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            input=input_data,
            env=env.as_dict(),
        )
    except FileNotFoundError:
        err_fd.write(f"{args[0]}: command not found\n")
        return 127
    except PermissionError:
        err_fd.write(f"{args[0]}: permission denied\n")
        return 126

    if not out_real:
        out_fd.write(proc.stdout.decode("utf-8", errors="replace"))
    if not err_real:
        err_fd.write(proc.stderr.decode("utf-8", errors="replace"))

    return proc.returncode
