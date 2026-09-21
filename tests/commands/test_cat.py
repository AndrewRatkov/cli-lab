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


def run_cat(fds: FdTriple, *args: str) -> int:
    return commands.lookup("cat")(fds, EnvScope(), ["cat", *args])


def test_cat_single_file(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("Hello, world!\n")
    fds = default_fd_triple()
    assert run_cat(fds, str(f)) == 0
    assert read_out(fds) == "Hello, world!\n"
    assert read_err(fds) == ""


def test_cat_concatenates_files_in_order(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("first")
    b.write_text("second")
    fds = default_fd_triple()
    assert run_cat(fds, str(a), str(b)) == 0
    assert read_out(fds) == "firstsecond"


def test_cat_without_args_reads_stdin() -> None:
    fds = default_fd_triple("from stdin\n")
    assert run_cat(fds) == 0
    assert read_out(fds) == "from stdin\n"


def test_cat_dash_means_stdin(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("file\n")
    fds = default_fd_triple("stdin\n")
    assert run_cat(fds, str(f), "-") == 0
    assert read_out(fds) == "file\nstdin\n"


def test_cat_empty_file(tmp_path: Path) -> None:
    f = tmp_path / "empty.txt"
    f.write_text("")
    fds = default_fd_triple()
    assert run_cat(fds, str(f)) == 0
    assert read_out(fds) == ""


def test_cat_missing_file_reports_error(tmp_path: Path) -> None:
    fd_missing = tmp_path / "nope.txt"
    fds = default_fd_triple()
    assert run_cat(fds, str(fd_missing)) == 1
    assert read_out(fds) == ""
    assert read_err(fds) == f"cat: {fd_missing}: No such file or directory\n"


def test_cat_directory_reports_error(tmp_path: Path) -> None:
    fds = default_fd_triple()
    assert run_cat(fds, str(tmp_path)) == 1
    assert read_err(fds) == f"cat: {tmp_path}: Is a directory\n"


def test_cat_continues_after_error(tmp_path: Path) -> None:
    fd0 = tmp_path / "a.txt"
    fd1 = tmp_path / "b.txt"
    fd0.write_text("a\n")
    fd1.write_text("b\n")
    fd_missing = tmp_path / "missing.txt"
    fds = default_fd_triple()
    assert run_cat(fds, str(fd0), str(fd_missing), str(fd1)) == 1
    assert read_out(fds) == "a\nb\n"
    assert read_err(fds) == f"cat: {fd_missing}: No such file or directory\n"


def test_cat_is_registered() -> None:
    assert commands.lookup("cat") is not None
    assert commands.lookup("cat").name == "cat"
