import io
from pathlib import Path

import commands
from runtime import EnvScope, FdTriple


def _text_fd(content: str = "") -> io.TextIOWrapper:
    fd = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    fd.write(content)
    fd.seek(0)
    return fd


def default_fd_triple(in_str: str = "") -> FdTriple:
    return FdTriple(_text_fd(in_str), _text_fd(), _text_fd())


def read_out(fds: FdTriple) -> str:
    out = fds.get_out()
    out.seek(0)
    return out.read()


def read_err(fds: FdTriple) -> str:
    err = fds.get_err()
    err.seek(0)
    return err.read()


def run_wc(fds: FdTriple, *args: str) -> int:
    return commands.lookup("wc")(fds, EnvScope(), ["wc", *args])


def test_wc_file(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("Some example text\n")
    fds = default_fd_triple()
    assert run_wc(fds, str(f)) == 0
    assert read_out(fds) == f"1 3 18 {f}\n"


def test_wc_stdin() -> None:
    fds = default_fd_triple("123\n")
    assert run_wc(fds) == 0
    assert read_out(fds) == "1 1 4\n"


def test_wc_several_files_prints_total(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("one\n")
    b.write_text("two three\n")
    fds = default_fd_triple()
    assert run_wc(fds, str(a), str(b)) == 0
    assert read_out(fds).splitlines()[-1] == "2 3 14 total"


def test_wc_missing_file() -> None:
    fds = default_fd_triple()
    assert run_wc(fds, "no_such_file") == 1
    assert "no_such_file" in read_err(fds)
