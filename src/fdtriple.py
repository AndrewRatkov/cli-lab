import io
import sys


class FdTriple:
    """Triple of file descriptors: input, output and error streams."""

    def __init__(
        self,
        fd_in: io.TextIOWrapper | None = None,
        fd_out: io.TextIOWrapper | None = None,
        fd_err: io.TextIOWrapper | None = None,
    ) -> None:
        self._in: io.TextIOWrapper | None = fd_in
        self._out: io.TextIOWrapper | None = fd_out
        self._err: io.TextIOWrapper | None = fd_err

    def set_in(self, fd: io.TextIOWrapper) -> None:
        self._in = fd

    def get_in(self) -> io.TextIOWrapper:
        return self._in

    def set_out(self, fd: io.TextIOWrapper) -> None:
        self._out = fd

    def get_out(self) -> io.TextIOWrapper:
        return self._out

    def set_err(self, fd: io.TextIOWrapper) -> None:
        self._err = fd

    def get_err(self) -> io.TextIOWrapper:
        return self._err

    def replace_nones(
        self,
        fd_in: io.TextIOWrapper = sys.stdin,
        fd_out: io.TextIOWrapper = sys.stdout,
        fd_err: io.TextIOWrapper = sys.stderr,
    ) -> None:
        if not self._in:
            self._in = fd_in
        if not self._out:
            self._out = fd_out
        if not self._err:
            self._err = fd_err

    def all_fds_are_set(self) -> bool:
        if self._in is None:
            return False
        if self._out is None:
            return False
        if self._err is None:
            return False
        return True
