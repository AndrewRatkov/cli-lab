import io
from pathlib import Path

import commands
from envscope import envScope
from fdtriple import fdTriple


def _text_fd(content: str = "") -> io.TextIOWrapper:
    fd = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    fd.write(content)
    fd.seek(0)
    return fd


def defaultFdTriple(in_str: str = "") -> fdTriple:
    return fdTriple(_text_fd(in_str), _text_fd(), _text_fd())


def readOut(fds: fdTriple) -> str:
    out = fds.GetOut()
    out.seek(0)
    return out.read()


def readErr(fds: fdTriple) -> str:
    err = fds.GetErr()
    err.seek(0)
    return err.read()


def run_cat(fds: fdTriple, *args: str) -> int:
    return commands.lookup("cat")(fds, envScope(), ["cat", *args])


def test_cat_single_file(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("Hello, world!\n")
    fds = defaultFdTriple()
    assert run_cat(fds, str(f)) == 0
    assert readOut(fds) == "Hello, world!\n"
    assert readErr(fds) == ""


def test_cat_concatenates_files_in_order(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("first")
    b.write_text("second")
    fds = defaultFdTriple()
    assert run_cat(fds, str(a), str(b)) == 0
    assert readOut(fds) == "firstsecond"


def test_cat_without_args_reads_stdin() -> None:
    fds = defaultFdTriple("from stdin\n")
    assert run_cat(fds) == 0
    assert readOut(fds) == "from stdin\n"


def test_cat_dash_means_stdin(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("file\n")
    fds = defaultFdTriple("stdin\n")
    assert run_cat(fds, str(f), "-") == 0
    assert readOut(fds) == "file\nstdin\n"


def test_cat_empty_file(tmp_path: Path) -> None:
    f = tmp_path / "empty.txt"
    f.write_text("")
    fds = defaultFdTriple()
    assert run_cat(fds, str(f)) == 0
    assert readOut(fds) == ""


def test_cat_missing_file_reports_error(tmp_path: Path) -> None:
    fd_missing = tmp_path / "nope.txt"
    fds = defaultFdTriple()
    assert run_cat(fds, str(fd_missing)) == 1
    assert readOut(fds) == ""
    assert readErr(fds) == f"cat: {fd_missing}: No such file or directory\n"


def test_cat_directory_reports_error(tmp_path: Path) -> None:
    fds = defaultFdTriple()
    assert run_cat(fds, str(tmp_path)) == 1
    assert readErr(fds) == f"cat: {tmp_path}: Is a directory\n"


def test_cat_continues_after_error(tmp_path: Path) -> None:
    fd0 = tmp_path / "a.txt"
    fd1 = tmp_path / "b.txt"
    fd0.write_text("a\n")
    fd1.write_text("b\n")
    fd_missing = tmp_path / "missing.txt"
    fds = defaultFdTriple()
    assert run_cat(fds, str(fd0), str(fd_missing), str(fd1)) == 1
    assert readOut(fds) == "a\nb\n"
    assert readErr(fds) == f"cat: {fd_missing}: No such file or directory\n"


def test_cat_is_registered() -> None:
    assert commands.lookup("cat") is not None
    assert commands.lookup("cat").name == "cat"
