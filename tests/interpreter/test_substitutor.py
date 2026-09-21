from interpreter import split_into_arguments
from runtime import EnvScope

import pytest


@pytest.mark.parametrize(
    "cmd,scope,expected",
    [
        ("echo x", EnvScope(), ["echo", "x"]),
        ("cat file.txt", EnvScope(), ["cat", "file.txt"]),
        ("echo 'hello world'", EnvScope(), ["echo", "hello world"]),
        (" cat    file.txt  ", EnvScope(), ["cat", "file.txt"]),
        ("echo ' hello world '", EnvScope(), ["echo", " hello world "]),
        ("echo '$x$x$y'", EnvScope(), ["echo", "$x$x$y"]),
        ("echo $x$x$y", EnvScope(), ["echo"]),
        ('echo "$x$x$y"', EnvScope(), ["echo"]),
        ("echo \"''\"", EnvScope(), ["echo", "''"]),
        ("echo $x", EnvScope({"x": "30"}), ["echo", "30"]),
        ("$x$y", EnvScope({"x": "ec", "y": "ho hello"}), ["echo", "hello"]),
    ],
)
def test_split(cmd, scope, expected) -> None:
    assert split_into_arguments(cmd, scope) == expected
