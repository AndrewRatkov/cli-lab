import io
import commands
from commands.command import Command
from runtime import EnvScope, FdTriple


def _text_fd() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO(), encoding="utf-8")


def default_fd_triple() -> FdTriple:
    return FdTriple(_text_fd(), _text_fd(), _text_fd())


def read_out(fds: FdTriple) -> str:
    out = fds.get_out()
    out.seek(0)
    return out.read()


def test_lookup_finds_registered_command() -> None:
    cmd = commands.lookup("echo")
    assert isinstance(cmd, Command)
    assert cmd.name == "echo"


def test_lookup_unknown_returns_none() -> None:
    assert commands.lookup("no-such-command") is None


def test_registry_names_are_unique() -> None:
    names = [cmd.name for cmd in commands.COMMANDS]
    assert len(names) == len(set(names))


def test_call_delegates_to_run() -> None:
    fds = default_fd_triple()
    seen_args: list[list[str]] = []

    def fake(fds: FdTriple, env: EnvScope, args: list[str]) -> int:
        seen_args.append(args)
        return 42

    cmd = Command("fake", fake)
    assert cmd(fds, EnvScope(), ["fake", "a", "b"]) == 42
    assert seen_args == [["fake", "a", "b"]]
