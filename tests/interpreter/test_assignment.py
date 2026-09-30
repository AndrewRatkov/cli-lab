from interpreter.assignment import split_assignments


def test_only_assignments() -> None:
    assert split_assignments(["x=1", "y=2"]) == ([("x", "1"), ("y", "2")], [])


def test_assignment_before_command() -> None:
    assert split_assignments(["x=1", "echo", "a"]) == ([("x", "1")], ["echo", "a"])


def test_no_assignments() -> None:
    assert split_assignments(["echo", "x=1"]) == ([], ["echo", "x=1"])


def test_empty_value() -> None:
    assert split_assignments(["x="]) == ([("x", "")], [])


def test_invalid_name_is_not_assignment() -> None:
    assert split_assignments(["1x=2"]) == ([], ["1x=2"])
