import io
import os
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


def run_cd(fds: FdTriple, env: EnvScope, *args: str) -> int:
    return commands.lookup("cd")(fds, env, ["cd", *args])


@pytest.fixture
def tree(tmp_path: Path, monkeypatch) -> Path:
    (tmp_path / "a" / "b" / "c").mkdir(parents=True)
    (tmp_path / "file.txt").write_text("text\n")
    # cd changes the working directory of the whole process, monkeypatch
    # returns it back after the test
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_cd_relative_dir(tree: Path) -> None:
    env = EnvScope()
    fds = default_fd_triple()
    assert run_cd(fds, env, "a") == 0
    assert os.getcwd() == str(tree / "a")
    assert env.get("PWD") == str(tree / "a")
    assert env.get("OLDPWD") == str(tree)
    assert read_out(fds) == ""
    assert read_err(fds) == ""


def test_cd_parent_dirs(tree: Path) -> None:
    env = EnvScope()
    assert run_cd(default_fd_triple(), env, "a/b/c") == 0
    assert run_cd(default_fd_triple(), env, "../../..") == 0
    assert os.getcwd() == str(tree)


def test_cd_absolute_path(tree: Path) -> None:
    assert run_cd(default_fd_triple(), EnvScope(), str(tree / "a" / "b")) == 0
    assert os.getcwd() == str(tree / "a" / "b")


def test_cd_without_args_goes_home(tree: Path) -> None:
    env = EnvScope({"HOME": str(tree / "a")})
    assert run_cd(default_fd_triple(), env) == 0
    assert os.getcwd() == str(tree / "a")


def test_cd_dash_goes_back(tree: Path) -> None:
    env = EnvScope()
    run_cd(default_fd_triple(), env, "a")
    fds = default_fd_triple()
    assert run_cd(fds, env, "-") == 0
    assert os.getcwd() == str(tree)
    assert read_out(fds) == str(tree) + "\n"


def test_cd_missing_dir_reports_error(tree: Path) -> None:
    fds = default_fd_triple()
    assert run_cd(fds, EnvScope(), "missing") == 1
    assert read_err(fds).startswith("cd: missing: ")
    assert os.getcwd() == str(tree)


def test_cd_file_reports_error(tree: Path) -> None:
    fds = default_fd_triple()
    assert run_cd(fds, EnvScope(), "file.txt") == 1
    assert read_err(fds).startswith("cd: file.txt: ")
    assert os.getcwd() == str(tree)


def test_cd_too_many_arguments(tree: Path) -> None:
    fds = default_fd_triple()
    assert run_cd(fds, EnvScope(), "a", "a/b") == 1
    assert read_err(fds) == "cd: too many arguments\n"
    assert os.getcwd() == str(tree)


def test_cd_is_registered() -> None:
    assert commands.lookup("cd").name == "cd"
