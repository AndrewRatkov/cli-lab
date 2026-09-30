import io
import sys

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


def run_python(fds: FdTriple, env: EnvScope, code: str) -> int:
    return commands.EXTERNAL(fds, env, [sys.executable, "-c", code])


def test_external_stdout() -> None:
    fds = default_fd_triple()
    assert run_python(fds, EnvScope.from_os_environ(), "print('hi')") == 0
    assert read_out(fds).strip() == "hi"


def test_external_stdin() -> None:
    fds = default_fd_triple("from stdin")
    code = "import sys; print(sys.stdin.read().upper())"
    assert run_python(fds, EnvScope.from_os_environ(), code) == 0
    assert read_out(fds).strip() == "FROM STDIN"


def test_external_gets_env() -> None:
    env = EnvScope.from_os_environ()
    env.set("MY_VAR", "42")
    fds = default_fd_triple()
    assert run_python(fds, env, "import os; print(os.environ['MY_VAR'])") == 0
    assert read_out(fds).strip() == "42"


def test_external_exit_code_and_stderr() -> None:
    fds = default_fd_triple()
    code = "import sys; sys.stderr.write('boom'); sys.exit(5)"
    assert run_python(fds, EnvScope.from_os_environ(), code) == 5
    assert read_err(fds) == "boom"


def test_unknown_command() -> None:
    fds = default_fd_triple()
    name = "definitely_no_such_cmd"
    assert commands.lookup(name)(fds, EnvScope(), [name]) == 127
    assert "command not found" in read_err(fds)
