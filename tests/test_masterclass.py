from masterclass import *
import io


def make_fd() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO(), encoding="utf-8")


def test_default_call() -> None:
    m = MasterClass()
    m.SetNodeType(NodeType.LEAF)
    m.SetEnvScope(envScope())
    m.SetRawCmd("echo hello")

    fds = fdTriple()
    fd_out = make_fd()
    fds.SetOut(fd_out)
    assert fd_out == fds.GetOut()
    assert not m.isValid()

    m.SetFdTriple(fds)
    assert m.isValid()

    m.process()

    fd_out.seek(0)
    assert fd_out.read() == "hello\n"


def test_default_envscope_usage() -> None:
    m = MasterClass()
    m.SetNodeType(NodeType.LEAF)
    m.SetEnvScope(envScope({"x": "hello"}))
    m.SetRawCmd("echo $x")

    fds = fdTriple()
    fd_out = make_fd()
    fds.SetOut(fd_out)
    assert fd_out == fds.GetOut()
    assert not m.isValid()

    m.SetFdTriple(fds)
    assert m.isValid()

    m.process()

    fd_out.seek(0)
    assert fd_out.read() == "hello\n"


# echo hello | cat
def test_default_pipe() -> None:
    envscope = envScope()

    mc_echo = MasterClass()
    mc_echo.SetNodeType(NodeType.LEAF)
    mc_echo.SetEnvScope(envscope)
    mc_echo.SetRawCmd("echo hello")

    mc_cat = MasterClass()
    mc_cat.SetNodeType(NodeType.LEAF)
    mc_cat.SetEnvScope(envscope)
    mc_cat.SetRawCmd("cat")

    echo_fds, cat_fds = fdTriple(), fdTriple()
    pipe_fd, res_fd = make_fd(), make_fd()
    echo_fds.SetOut(pipe_fd)
    cat_fds.SetIn(pipe_fd)
    cat_fds.SetOut(res_fd)

    mc_echo.SetFdTriple(echo_fds)
    mc_cat.SetFdTriple(cat_fds)

    assert mc_echo.isValid()
    assert mc_cat.isValid()

    mc_main = MasterClass()
    mc_main.SetNodeType(NodeType.INNER)
    mc_main.SetSplitType(SplitType.PIPE)
    mc_main.SetEnvScope(envscope)

    main_fds = fdTriple()
    main_fds.SetOut(res_fd)
    mc_main.SetFdTriple(main_fds)
    mc_main.SetPipeFd(pipe_fd)

    mc_main.SetLeftNode(mc_echo)
    mc_main.SetRightNode(mc_cat)

    assert mc_main.isValid()

    mc_main.process()

    res_fd.seek(0)
    assert res_fd.read() == "hello\n"


# echo hello; echo world
def test_default_seq() -> None:
    envscope = envScope()

    mc_left = MasterClass()
    mc_left.SetNodeType(NodeType.LEAF)
    mc_left.SetEnvScope(envscope)
    mc_left.SetRawCmd("echo hello")
    mc_left.SetFdTriple(fdTriple())

    mc_right = MasterClass()
    mc_right.SetNodeType(NodeType.LEAF)
    mc_right.SetEnvScope(envscope)
    mc_right.SetRawCmd("echo world")
    mc_right.SetFdTriple(fdTriple())

    mc_main = MasterClass()
    mc_main.SetNodeType(NodeType.INNER)
    mc_main.SetSplitType(SplitType.SEQ)
    mc_main.SetEnvScope(envscope)
    mc_main.SetFdTriple(fdTriple())

    mc_main.SetLeftNode(mc_left)
    mc_main.SetRightNode(mc_right)

    res_fd = make_fd()
    mc_left.GetFdTriple().SetOut(res_fd)
    mc_right.GetFdTriple().SetOut(res_fd)
    mc_main.GetFdTriple().SetOut(res_fd)

    assert mc_left.isValid()
    assert mc_right.isValid()
    assert mc_main.isValid()

    mc_main.process()

    res_fd.seek(0)
    assert res_fd.read() == "hello\nworld\n"


def test_preprocess_pipe() -> None:
    envscope = envScope()

    mc_left = MasterClass()
    mc_left.SetNodeType(NodeType.LEAF)
    mc_left.SetRawCmd("echo hello")

    mc_right = MasterClass()
    mc_right.SetNodeType(NodeType.LEAF)
    mc_right.SetRawCmd("cat")

    mc_main = MasterClass()
    mc_main.SetNodeType(NodeType.INNER)
    mc_main.SetSplitType(SplitType.PIPE)

    mc_main.SetEnvScope(envscope)
    mc_main.SetFdTriple(fdTriple())
    res_fd = make_fd()
    mc_main.GetFdTriple().SetOut(res_fd)

    mc_main.SetLeftNode(mc_left)
    mc_main.SetRightNode(mc_right)

    mc_main.preprocess()
    assert mc_main.isValid()
    assert mc_left.isValid()
    assert mc_right.isValid()

    mc_main.process()
    res_fd.seek(0)
    assert res_fd.read() == "hello\n"


def test_preprocess_seq() -> None:
    envscope = envScope()

    mc_left = MasterClass()
    mc_left.SetNodeType(NodeType.LEAF)
    mc_left.SetRawCmd("echo hello")

    mc_right = MasterClass()
    mc_right.SetNodeType(NodeType.LEAF)
    mc_right.SetRawCmd("echo world")

    mc_main = MasterClass()
    mc_main.SetNodeType(NodeType.INNER)
    mc_main.SetSplitType(SplitType.SEQ)

    mc_main.SetEnvScope(envscope)
    mc_main.SetFdTriple(fdTriple())
    res_fd = make_fd()
    mc_main.GetFdTriple().SetOut(res_fd)

    mc_main.SetLeftNode(mc_left)
    mc_main.SetRightNode(mc_right)

    mc_main.preprocess()
    assert mc_main.isValid()
    assert mc_left.isValid()
    assert mc_right.isValid()

    mc_main.process()
    res_fd.seek(0)
    assert res_fd.read() == "hello\nworld\n"
