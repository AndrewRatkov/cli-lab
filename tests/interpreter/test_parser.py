import pytest

from interpreter import NodeType, Parser, ParseError


def shape(node):
    """Leaf -> raw_cmd; inner node -> (separator, left, right)."""
    if node.get_node_type() == NodeType.LEAF:
        assert node.get_left_node() is None and node.get_right_node() is None
        return node.get_raw_cmd()
    assert node.get_node_type() == NodeType.INNER
    return (
        node.get_split_type().value,
        shape(node.get_left_node()),
        shape(node.get_right_node()),
    )


def parse(s):
    return shape(Parser(s).parse())


def test_single_command_is_stripped_leaf():
    assert parse("   ls -la  ") == "ls -la"


@pytest.mark.parametrize(
    "src, expected",
    [
        ("a | b", ("|", "a", "b")),
        ("a; b", (";", "a", "b")),
        # ';' binds weaker than '|'
        ("a | b; c", (";", ("|", "a", "b"), "c")),
        ("a; b | c", (";", "a", ("|", "b", "c"))),
        # left associativity
        ("a; b; c", (";", (";", "a", "b"), "c")),
        ("a | b | c", ("|", ("|", "a", "b"), "c")),
        # trailing ';'
        ("a; b;", (";", "a", "b")),
        ("a;", "a"),
    ],
)
def test_structure(src, expected):
    assert parse(src) == expected


def test_inner_nodes_keep_their_substring():
    root = Parser("a | b; c").parse()
    assert root.get_raw_cmd() == "a | b; c"
    assert root.get_left_node().get_raw_cmd() == "a | b"


@pytest.mark.parametrize(
    "src, expected",
    [
        ("{ a; b; } | c", ("|", (";", "a", "b"), "c")),
        # braces override left associativity
        ("a | {b|c}", ("|", "a", ("|", "b", "c"))),
        ("{ { a | b; }; c; } | d", ("|", (";", ("|", "a", "b"), "c"), "d")),
        # a group of one command collapses into a leaf
        ("{ ls; }", "ls"),
        # braces not at the start are part of the argument
        ("echo {x}", "echo {x}"),
    ],
)
def test_braces(src, expected):
    assert parse(src) == expected


@pytest.mark.parametrize(
    "src, expected",
    [
        ("echo 'a;b' | grep \"x|y\"", ("|", "echo 'a;b'", 'grep "x|y"')),
        ('echo "{"; echo "}"', (";", 'echo "{"', 'echo "}"')),
        (r"echo a\;b", r"echo a\;b"),
        # \" inside double quotes does not close them
        (r'echo "a\"; b"', r'echo "a\"; b"'),
        # \ inside single quotes is a plain character
        (r"echo 'a\'; b", (";", r"echo 'a\'", "b")),
    ],
)
def test_quotes_and_escapes(src, expected):
    assert parse(src) == expected


@pytest.mark.parametrize(
    "src",
    [
        "   ",  # empty input
        "a |",  # missing pipe operand
        "| a",
        "a;; b",  # empty command between separators
        "a; }",  # unmatched '}'
        "{ a; b",  # unterminated '{'
        'echo "abc',  # unterminated quote
        "{ a; } b",  # text after group
        "{ }",  # empty group
    ],
)
def test_errors(src):
    with pytest.raises(ParseError):
        Parser(src).parse()
