from __future__ import annotations

from copy import deepcopy
from enum import Enum
import io

from envscope import EnvScope
from fdtriple import FdTriple
import commands
from command import Command
from substitutor import split_into_arguments


class NodeType(Enum):
    NOT_INITIALIZED = "not_initialized"
    INNER = "inner"
    LEAF = "leaf"


class SplitType(Enum):
    NOT_INITIALIZED = "not_initialized"
    PIPE = "|"
    SEQ = ";"


class MasterClass:
    """Node of the command tree.

    An INNER node splits into left/right children by SplitType;
    a LEAF node holds a raw command string.
    """

    def __init__(self) -> None:
        self._node_type: NodeType = NodeType.NOT_INITIALIZED
        # for inner node
        self._split_type: SplitType = SplitType.NOT_INITIALIZED
        self._left_node: MasterClass | None = None
        self._right_node: MasterClass | None = None
        # also for pipe node
        self._pipe_fd: io.TextIOWrapper | None = None
        # for leaf node
        self._raw_cmd: str | None = None
        # execution context
        self._env_scope: EnvScope | None = None
        self._fd_triple: FdTriple = FdTriple()

    def set_node_type(self, node_type: NodeType) -> None:
        self._node_type = node_type

    def get_node_type(self) -> NodeType:
        return self._node_type

    def set_split_type(self, split_type: SplitType) -> None:
        self._split_type = split_type

    def get_split_type(self) -> SplitType:
        return self._split_type

    def set_left_node(self, node: MasterClass | None) -> None:
        self._left_node = node

    def get_left_node(self) -> MasterClass | None:
        return self._left_node

    def set_right_node(self, node: MasterClass | None) -> None:
        self._right_node = node

    def get_right_node(self) -> MasterClass | None:
        return self._right_node

    def set_raw_cmd(self, raw_cmd: str | None) -> None:
        self._raw_cmd = raw_cmd

    def get_raw_cmd(self) -> str | None:
        return self._raw_cmd

    def set_env_scope(self, env: EnvScope | None) -> None:
        self._env_scope = env

    def get_env_scope(self) -> EnvScope | None:
        return self._env_scope

    def set_fd_triple(self, fds: FdTriple | None) -> None:
        self._fd_triple = fds

    def get_fd_triple(self) -> FdTriple | None:
        return self._fd_triple

    def set_pipe_fd(self, fd: io.TextIOWrapper) -> None:
        self._pipe_fd = fd

    def get_pipe_fd(self) -> io.TextIOWrapper:
        return self._pipe_fd

    def preprocess(self) -> None:
        if self._node_type == NodeType.LEAF:
            return

        fds = self.get_fd_triple()
        if self._split_type == SplitType.SEQ:
            self._left_node.get_fd_triple().replace_nones(
                fds.get_in(), fds.get_out(), fds.get_err()
            )
            self._right_node.get_fd_triple().replace_nones(
                fds.get_in(), fds.get_out(), fds.get_err()
            )
            self._left_node.set_env_scope(self._env_scope)
            self._right_node.set_env_scope(self._env_scope)
        elif self._split_type == SplitType.PIPE:
            self._pipe_fd = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
            self._left_node.get_fd_triple().replace_nones(
                fds.get_in(), self._pipe_fd, fds.get_err()
            )
            self._right_node.get_fd_triple().replace_nones(
                self._pipe_fd, fds.get_out(), fds.get_err()
            )

            self._left_node.set_env_scope(deepcopy(self._env_scope))
            self._right_node.set_env_scope(deepcopy(self._env_scope))

        self._left_node.preprocess()
        self._right_node.preprocess()

    def process(self) -> None:
        assert self.is_valid()
        if self._node_type == NodeType.INNER:
            self._left_node.process()
            if self._split_type == SplitType.PIPE:
                self._pipe_fd.seek(0)
            self._right_node.process()
        else:
            args: list[str] = split_into_arguments(self._raw_cmd, self._env_scope)
            assert len(args) > 0
            cmd: Command | None = commands.lookup(args[0])
            if cmd:
                cmd(self._fd_triple, self._env_scope, args)

    def is_valid(self) -> bool:
        if self._node_type == NodeType.NOT_INITIALIZED:
            return False
        elif self._node_type == NodeType.INNER:
            if (
                self._split_type == SplitType.NOT_INITIALIZED
                or not self._left_node
                or not self._right_node
            ):
                return False
            if self._split_type == SplitType.PIPE and self._pipe_fd is None:
                return False
        elif self._node_type == NodeType.LEAF:
            if self._raw_cmd is None:
                return False

        if self._env_scope is None or self._fd_triple is None:
            return False

        if not self._fd_triple.all_fds_are_set():
            return False

        return True
