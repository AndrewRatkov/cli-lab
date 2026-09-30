import io
from pathlib import Path

import pytest

from commands import ShellExit
from main import run
from runtime import EnvScope, FdTriple


def make_fd() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO(), encoding="utf-8")


def test1() -> None:
    string: str = "echo hello"
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run(string, fds)
    res_fd.seek(0)
    assert res_fd.read() == "hello\n"


def test2(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("Hello, world!\n")

    string: str = "cat " + str(f)
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run(string, fds)
    res_fd.seek(0)
    assert res_fd.read() == "Hello, world!\n"


def test3() -> None:
    string: str = "echo hello | cat"
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run(string, fds)
    res_fd.seek(0)
    assert res_fd.read() == "hello\n"


def test4() -> None:
    string: str = "echo hello; echo world"
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run(string, fds)
    res_fd.seek(0)
    assert res_fd.read() == "hello\nworld\n"


def test5() -> None:
    string: str = "echo hello | cat | cat | cat"
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run(string, fds)
    res_fd.seek(0)
    assert res_fd.read() == "hello\n"


def test6() -> None:
    string: str = "echo hello | cat;"
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run(string, fds)
    res_fd.seek(0)
    assert res_fd.read() == "hello\n"


def test7() -> None:
    string: str = "echo hello | cat; echo world | cat"
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run(string, fds)
    res_fd.seek(0)
    assert res_fd.read() == "hello\nworld\n"


def test8() -> None:
    string: str = "{ echo hello; echo world } | cat"
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run(string, fds)
    res_fd.seek(0)
    assert res_fd.read() == "hello\nworld\n"


def test_assignment_then_substitution() -> None:
    envs = EnvScope()
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run("FILE=example.txt", fds, envs)
    run("echo $FILE", fds, envs)
    res_fd.seek(0)
    assert res_fd.read() == "example.txt\n"


def test_prefix_assignment_is_local() -> None:
    envs = EnvScope()
    fds = FdTriple()
    fds.set_out(make_fd())

    run("X=1 echo hi", fds, envs)
    assert envs.get("X") == ""


def test_run_returns_exit_code() -> None:
    fds = FdTriple()
    fds.set_out(make_fd())
    fds.set_err(make_fd())
    assert run("echo hi", fds) == 0
    assert run("cat no_such_file", fds) == 1


def test_empty_substitution_is_noop() -> None:
    fds = FdTriple()
    fds.set_out(make_fd())
    assert run("$EMPTY", fds, EnvScope()) == 0


def test_exit_raises() -> None:
    with pytest.raises(ShellExit):
        run("exit", FdTriple())
