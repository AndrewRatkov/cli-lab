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
        self._in: io.TextIOWrapper | None = fd_in
        self._out: io.TextIOWrapper | None = fd_out
        self._err: io.TextIOWrapper | None = fd_err

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

    def replaceNones(
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

    def allFdsAreSet(self) -> bool:
        if self._in is None:
            return False
        if self._out is None:
            return False
        if self._err is None:
            return False
        return True
