import io
from pathlib import Path

import pytest
import sys

from commands import ShellExit
from main import run
from runtime import EnvScope, FdTriple
from interpreter import MasterClass, Parser, NodeType


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


def test9() -> None:
    envs = EnvScope()
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run('a="ec"; b="ho hello"', fds, envs)
    run("$a$b", fds, envs)
    res_fd.seek(0)
    assert res_fd.read() == "hello\n"


def test10() -> None:
    envs = EnvScope()
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run('a="ec"; b="ho hello > res.txt"', fds, envs)
    run("$a$b", fds, envs)
    res_fd.seek(0)
    assert res_fd.read() == "hello > res.txt\n"


def test11() -> None:
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run("echo hello | wc", fds)
    res_fd.seek(0)
    assert res_fd.read() == "1 1 6\n"


def test12() -> None:
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run('echo " hello " | wc', fds)
    res_fd.seek(0)
    assert res_fd.read() == "1 1 8\n"


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

    string: str = "X=1 echo hi"

    parser: Parser = Parser(string)
    masterclass_root: MasterClass = parser.parse()
    assert masterclass_root.get_node_type() == NodeType.LEAF

    fds.replace_nones(sys.stdin, sys.stdout, sys.stderr)
    masterclass_root.set_fd_triple(fds)
    masterclass_root.set_env_scope(envs)

    assert masterclass_root.is_valid()
    assert masterclass_root.get_raw_cmd() == string
    masterclass_root.preprocess()
    masterclass_root.process()
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
