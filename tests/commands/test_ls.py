import io
from pathlib import Path

import pytest

import commands
from runtime import EnvScope, FdTriple


def _text_fd() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO(), encoding="utf-8")


def default_fd_triple() -> FdTriple:
    return FdTriple(_text_fd(), _text_fd(), _text_fd())


def read_out(fds: FdTriple) -> str:
    out = fds.get_out()
    out.seek(0)
    return out.read()


def read_err(fds: FdTriple) -> str:
    err = fds.get_err()
    err.seek(0)
    return err.read()


def run_ls(fds: FdTriple, *args: str) -> int:
    return commands.lookup("ls")(fds, EnvScope(), ["ls", *args])


@pytest.fixture
def tree(tmp_path: Path, monkeypatch) -> Path:
    (tmp_path / "b.txt").write_text("b\n")
    (tmp_path / "a.txt").write_text("a\n")
    (tmp_path / ".hidden").write_text("h\n")
    (tmp_path / "dir").mkdir()
    (tmp_path / "dir" / "x.txt").write_text("x\n")
    (tmp_path / "empty").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_ls_current_dir(tree: Path) -> None:
    fds = default_fd_triple()
    assert run_ls(fds) == 0
    assert read_out(fds) == "a.txt\nb.txt\ndir\nempty\n"
    assert read_err(fds) == ""


def test_ls_dir(tree: Path) -> None:
    fds = default_fd_triple()
    assert run_ls(fds, "dir") == 0
    assert read_out(fds) == "x.txt\n"


def test_ls_empty_dir(tree: Path) -> None:
    fds = default_fd_triple()
    assert run_ls(fds, "empty") == 0
    assert read_out(fds) == ""


def test_ls_file(tree: Path) -> None:
    fds = default_fd_triple()
    assert run_ls(fds, "a.txt") == 0
    assert read_out(fds) == "a.txt\n"


def test_ls_missing_reports_error(tree: Path) -> None:
    fds = default_fd_triple()
    assert run_ls(fds, "missing") == 2
    assert read_out(fds) == ""
    assert read_err(fds).startswith("ls: cannot access 'missing': ")


def test_ls_too_many_arguments(tree: Path) -> None:
    fds = default_fd_triple()
    assert run_ls(fds, "a.txt", "dir") == 2
    assert read_err(fds) == "ls: too many arguments\n"


def test_ls_is_registered() -> None:
    assert commands.lookup("ls").name == "ls"
