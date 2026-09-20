from src.substitutor import splitIntoArguments
from src.envscope import envScope

import pytest


@pytest.mark.parametrize(
    "cmd,scope,expected",
    [
        ("echo x", envScope(), ["echo", "x"]),
        ("cat file.txt", envScope(), ["cat", "file.txt"]),
        ("echo 'hello world'", envScope(), ["echo", "hello world"]),
        (" cat    file.txt  ", envScope(), ["cat", "file.txt"]),
        ("echo ' hello world '", envScope(), ["echo", " hello world "]),
        ("echo '$x$x$y'", envScope(), ["echo", "$x$x$y"]),
        ("echo $x$x$y", envScope(), ["echo"]),
        ('echo "$x$x$y"', envScope(), ["echo"]),
        ("echo \"''\"", envScope(), ["echo", "''"]),
        ("echo $x", envScope({"x": "30"}), ["echo", "30"]),
        ("$x$y", envScope({"x": "ec", "y": "ho hello"}), ["echo", "hello"]),
    ],
)
def test_split(cmd, scope, expected) -> None:
    assert splitIntoArguments(cmd, scope) == expected
