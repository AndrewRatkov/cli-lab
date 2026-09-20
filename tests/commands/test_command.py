import io
import commands
from src.command import Command
from src.envscope import envScope
from src.fdtriple import fdTriple


def _text_fd() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO(), encoding="utf-8")


def defaultFdTriple() -> fdTriple:
    return fdTriple(_text_fd(), _text_fd(), _text_fd())


def readOut(fds: fdTriple) -> str:
    out = fds.GetOut()
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
    fds = defaultFdTriple()
    seen_args: list[list[str]] = []

    def fake(fds: fdTriple, env: envScope, args: list[str]) -> int:
        seen_args.append(args)
        return 42

    cmd = Command("fake", fake)
    assert cmd(fds, envScope(), ["fake", "a", "b"]) == 42
    assert seen_args == [["fake", "a", "b"]]
