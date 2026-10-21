import io
from pathlib import Path

import pytest

import commands
from runtime import EnvScope, FdTriple

NOTES = "Минимальный синтаксис grep\nчасть II\nстрока после II\nx\ny\nII again\nz\n"


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


def run_grep(fds: FdTriple, *args: str) -> int:
    return commands.lookup("grep")(fds, EnvScope(), ["grep", *args])


@pytest.fixture
def notes(tmp_path: Path) -> str:
    f = tmp_path / "notes.md"
    f.write_text(NOTES, encoding="utf-8", newline="")
    return str(f)


def test_grep_is_registered() -> None:
    assert commands.lookup("grep").name == "grep"


def test_grep_simple_match(notes: str) -> None:
    fds = default_fd_triple()
    assert run_grep(fds, "Минимальный", notes) == 0
    assert read_out(fds) == "Минимальный синтаксис grep\n"


def test_grep_no_match(notes: str) -> None:
    fds = default_fd_triple()
    assert run_grep(fds, "Минимальный$", notes) == 1
    assert read_out(fds) == ""
    assert read_err(fds) == ""


def test_grep_line_start_anchor(notes: str) -> None:
    fds = default_fd_triple()
    assert run_grep(fds, "^II", notes) == 0
    assert read_out(fds) == "II again\n"


def test_grep_ignore_case(notes: str) -> None:
    fds = default_fd_triple()
    assert run_grep(fds, "-i", "минимальный", notes) == 0
    assert read_out(fds) == "Минимальный синтаксис grep\n"


def test_grep_ignore_case_long_option(notes: str) -> None:
    fds = default_fd_triple()
    assert run_grep(fds, "--ignore-case", "GREP", notes) == 0
    assert read_out(fds) == "Минимальный синтаксис grep\n"


def test_grep_word_regexp_rejects_part_of_word(notes: str) -> None:
    fds = default_fd_triple()
    assert run_grep(fds, "-w", "Минимал", notes) == 1
    assert read_out(fds) == ""


def test_grep_word_regexp_with_alternation() -> None:
    fds = default_fd_triple("foobar\nfoo baz\nqux\n")
    assert run_grep(fds, "-w", "foo|qux") == 0
    assert read_out(fds) == "foo baz\nqux\n"


def test_grep_clustered_keys(notes: str) -> None:
    fds = default_fd_triple()
    assert run_grep(fds, "-iw", "GREP", notes) == 0
    assert read_out(fds) == "Минимальный синтаксис grep\n"


def test_grep_after_context(notes: str) -> None:
    fds = default_fd_triple()
    assert run_grep(fds, "-A", "1", "часть", notes) == 0
    assert read_out(fds) == "часть II\nстрока после II\n"


def test_grep_after_context_separates_groups(notes: str) -> None:
    fds = default_fd_triple()
    assert run_grep(fds, "-A", "1", "II", notes) == 0
    assert read_out(fds) == "часть II\nстрока после II\nx\n--\nII again\nz\n"


def test_grep_after_context_merges_overlapping_windows(notes: str) -> None:
    fds = default_fd_triple()
    assert run_grep(fds, "--after-context", "3", "II", notes) == 0
    assert read_out(fds) == "часть II\nстрока после II\nx\ny\nII again\nz\n"


def test_grep_after_context_at_end_of_input() -> None:
    fds = default_fd_triple("a\nb\n")
    assert run_grep(fds, "-A", "5", "b") == 0
    assert read_out(fds) == "b\n"


def test_grep_stdin() -> None:
    fds = default_fd_triple("abc\nxyz\nbar")
    assert run_grep(fds, "a") == 0
    assert read_out(fds) == "abc\nbar\n"


def test_grep_dash_reads_stdin() -> None:
    fds = default_fd_triple("one\ntwo\n")
    assert run_grep(fds, "two", "-") == 0
    assert read_out(fds) == "two\n"


def test_grep_several_files_prefixes_names(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("x\n", newline="")
    b.write_text("y\nx\n", newline="")
    fds = default_fd_triple()
    assert run_grep(fds, "x", str(a), str(b)) == 0
    assert read_out(fds) == f"{a}:x\n{b}:x\n"


def test_grep_pattern_after_double_dash() -> None:
    fds = default_fd_triple("a-x\nb\n")
    assert run_grep(fds, "--", "-x") == 0
    assert read_out(fds) == "a-x\n"


def test_grep_missing_file() -> None:
    fds = default_fd_triple()
    assert run_grep(fds, "x", "no_such_file") == 2
    assert read_err(fds) == "grep: no_such_file: No such file or directory\n"


def test_grep_missing_file_does_not_stop_others(notes: str) -> None:
    fds = default_fd_triple()
    assert run_grep(fds, "^x$", "no_such_file", notes) == 2
    assert read_out(fds) == f"{notes}:x\n"
    assert "no_such_file" in read_err(fds)


def test_grep_invalid_pattern() -> None:
    fds = default_fd_triple("abc\n")
    assert run_grep(fds, "(") == 2
    assert read_out(fds) == ""
    assert read_err(fds).startswith("grep: invalid pattern: ")


@pytest.mark.parametrize(
    "args, message",
    [
        ((), "the following arguments are required: PATTERN"),
        (("--bad", "x"), "unrecognized arguments: --bad"),
        (("-A", "x", "y"), "invalid int value: 'x'"),
        (("-A", "-1", "y"), "-1: invalid context length"),
    ],
)
def test_grep_usage_errors(args: tuple[str, ...], message: str) -> None:
    fds = default_fd_triple()
    assert run_grep(fds, *args) == 2
    assert read_out(fds) == ""
    err = read_err(fds)
    assert err.startswith("usage: grep [-i] [-w] [-A NUM] PATTERN [FILE...]\n")
    assert message in err


def test_grep_help() -> None:
    fds = default_fd_triple()
    assert run_grep(fds, "-h") == 0
    out = read_out(fds)
    assert out.startswith("usage: grep")
    assert "--after-context" in out
    assert read_err(fds) == ""
