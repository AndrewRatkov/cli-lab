import io
import sys


class fdTriple:
    """Triple of file descriptors: input, output and error streams."""

    def __init__(
        self,
        fd_in: io.TextIOWrapper | None = None,
        fd_out: io.TextIOWrapper | None = None,
        fd_err: io.TextIOWrapper | None = None,
    ) -> None:
        self._in: io.TextIOWrapper = fd_in if fd_in is not None else sys.stdin
        self._out: io.TextIOWrapper = fd_out if fd_out is not None else sys.stdout
        self._err: io.TextIOWrapper = fd_err if fd_err is not None else sys.stderr

    def SetIn(self, fd: io.TextIOWrapper) -> None:
        self._in = fd

    def GetIn(self) -> io.TextIOWrapper:
        return self._in

    def SetOut(self, fd: io.TextIOWrapper) -> None:
        self._out = fd

    def GetOut(self) -> io.TextIOWrapper:
        return self._out

    def SetErr(self, fd: io.TextIOWrapper) -> None:
        self._err = fd

    def GetErr(self) -> io.TextIOWrapper:
        return self._err
