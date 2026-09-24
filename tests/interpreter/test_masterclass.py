import io
import sys

from interpreter import MasterClass, NodeType, SplitType
from runtime import EnvScope, FdTriple


def make_fd() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO(), encoding="utf-8")


def test_default_call() -> None:
    m = MasterClass()
    m.set_node_type(NodeType.LEAF)
    m.set_env_scope(EnvScope())
    m.set_raw_cmd("echo hello")

    fds = FdTriple()
    fd_out = make_fd()
    fds.set_out(fd_out)
    fds.replace_nones()
    assert fd_out == fds.get_out()
    assert not m.is_valid()

    m.set_fd_triple(fds)
    assert m.is_valid()

    m.process()

    fd_out.seek(0)
    assert fd_out.read() == "hello\n"


def test_default_envscope_usage() -> None:
    m = MasterClass()
    m.set_node_type(NodeType.LEAF)
    m.set_env_scope(EnvScope({"x": "hello"}))
    m.set_raw_cmd("echo $x")

    fds = FdTriple()
    fd_out = make_fd()
    fds.set_out(fd_out)
    fds.replace_nones()
    assert fd_out == fds.get_out()
    assert not m.is_valid()

    m.set_fd_triple(fds)
    assert m.is_valid()

    m.process()

    fd_out.seek(0)
    assert fd_out.read() == "hello\n"


# echo hello | cat
def test_default_pipe() -> None:
    envscope = EnvScope()
    res_fd = make_fd()
    fds: FdTriple = FdTriple(sys.stdin, res_fd, sys.stderr)

    mc_echo = MasterClass()
    mc_echo.set_node_type(NodeType.LEAF)
    mc_echo.set_env_scope(envscope)
    mc_echo.set_raw_cmd("echo hello")

    mc_cat = MasterClass()
    mc_cat.set_node_type(NodeType.LEAF)
    mc_cat.set_env_scope(envscope)
    mc_cat.set_raw_cmd("cat")

    pipe_fd, res_fd = make_fd(), make_fd()
    mc_echo.set_fd_triple(FdTriple(sys.stdin, pipe_fd, sys.stderr))
    mc_cat.set_fd_triple(FdTriple(pipe_fd, res_fd, sys.stderr))

    assert mc_echo.is_valid()
    assert mc_cat.is_valid()

    mc_main = MasterClass()
    mc_main.set_node_type(NodeType.INNER)
    mc_main.set_split_type(SplitType.PIPE)
    mc_main.set_env_scope(envscope)

    mc_main.set_fd_triple(FdTriple(sys.stdin, res_fd, sys.stderr))
    mc_main.set_pipe_fd(pipe_fd)

    mc_main.set_left_node(mc_echo)
    mc_main.set_right_node(mc_cat)

    assert mc_main.is_valid()

    mc_main.process()

    res_fd.seek(0)
    assert res_fd.read() == "hello\n"


# echo hello; echo world
def test_default_seq() -> None:
    envscope = EnvScope()
    res_fd = make_fd()
    fds: FdTriple = FdTriple(sys.stdin, res_fd, sys.stderr)

    mc_left = MasterClass()
    mc_left.set_node_type(NodeType.LEAF)
    mc_left.set_env_scope(envscope)
    mc_left.set_raw_cmd("echo hello")
    mc_left.set_fd_triple(fds)

    mc_right = MasterClass()
    mc_right.set_node_type(NodeType.LEAF)
    mc_right.set_env_scope(envscope)
    mc_right.set_raw_cmd("echo world")
    mc_right.set_fd_triple(fds)

    mc_main = MasterClass()
    mc_main.set_node_type(NodeType.INNER)
    mc_main.set_split_type(SplitType.SEQ)
    mc_main.set_env_scope(envscope)
    mc_main.set_fd_triple(fds)

    mc_main.set_left_node(mc_left)
    mc_main.set_right_node(mc_right)

    assert mc_left.is_valid()
    assert mc_right.is_valid()
    assert mc_main.is_valid()

    mc_main.process()

    res_fd.seek(0)
    assert res_fd.read() == "hello\nworld\n"


def test_preprocess_pipe() -> None:
    envscope = EnvScope()

    mc_left = MasterClass()
    mc_left.set_node_type(NodeType.LEAF)
    mc_left.set_raw_cmd("echo hello")

    mc_right = MasterClass()
    mc_right.set_node_type(NodeType.LEAF)
    mc_right.set_raw_cmd("cat")

    mc_main = MasterClass()
    mc_main.set_node_type(NodeType.INNER)
    mc_main.set_split_type(SplitType.PIPE)

    mc_main.set_env_scope(envscope)
    res_fd = make_fd()
    mc_main.set_fd_triple(FdTriple(sys.stdin, res_fd, sys.stderr))

    mc_main.set_left_node(mc_left)
    mc_main.set_right_node(mc_right)

    mc_main.preprocess()
    assert mc_main.is_valid()
    assert mc_left.is_valid()
    assert mc_right.is_valid()

    mc_main.process()
    res_fd.seek(0)
    assert res_fd.read() == "hello\n"


def test_preprocess_seq() -> None:
    envscope = EnvScope()

    mc_left = MasterClass()
    mc_left.set_node_type(NodeType.LEAF)
    mc_left.set_raw_cmd("echo hello")

    mc_right = MasterClass()
    mc_right.set_node_type(NodeType.LEAF)
    mc_right.set_raw_cmd("echo world")

    mc_main = MasterClass()
    mc_main.set_node_type(NodeType.INNER)
    mc_main.set_split_type(SplitType.SEQ)

    mc_main.set_env_scope(envscope)
    res_fd = make_fd()
    mc_main.set_fd_triple(FdTriple(sys.stdin, res_fd, sys.stderr))

    mc_main.set_left_node(mc_left)
    mc_main.set_right_node(mc_right)

    mc_main.preprocess()
    assert mc_main.is_valid()
    assert mc_left.is_valid()
    assert mc_right.is_valid()

    mc_main.process()
    res_fd.seek(0)
    assert res_fd.read() == "hello\nworld\n"
