from __future__ import annotations

from copy import deepcopy
from enum import Enum
import io

from envscope import envScope
from fdtriple import fdTriple
import commands
from command import Command
from substitutor import splitIntoArguments


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
        self._nodeType: NodeType = NodeType.NOT_INITIALIZED
        # for inner node
        self._splitType: SplitType = SplitType.NOT_INITIALIZED
        self._leftNode: MasterClass | None = None
        self._rightNode: MasterClass | None = None
        # also for pipe node
        self._pipeFd: io.TextIOWrapper | None = None
        # for leaf node
        self._rawCmd: str | None = None
        # execution context
        self._envScope: envScope | None = None
        self._fdTriple: fdTriple | None = None

    def SetNodeType(self, nodeType: NodeType) -> None:
        self._nodeType = nodeType

    def GetNodeType(self) -> NodeType:
        return self._nodeType

    def SetSplitType(self, splitType: SplitType) -> None:
        self._splitType = splitType

    def GetSplitType(self) -> SplitType:
        return self._splitType

    def SetLeftNode(self, node: MasterClass | None) -> None:
        self._leftNode = node

    def GetLeftNode(self) -> MasterClass | None:
        return self._leftNode

    def SetRightNode(self, node: MasterClass | None) -> None:
        self._rightNode = node

    def GetRightNode(self) -> MasterClass | None:
        return self._rightNode

    def SetRawCmd(self, rawCmd: str | None) -> None:
        self._rawCmd = rawCmd

    def GetRawCmd(self) -> str | None:
        return self._rawCmd

    def SetEnvScope(self, env: envScope | None) -> None:
        self._envScope = env

    def GetEnvScope(self) -> envScope | None:
        return self._envScope

    def SetFdTriple(self, fds: fdTriple | None) -> None:
        self._fdTriple = fds

    def GetFdTriple(self) -> fdTriple | None:
        return self._fdTriple

    def SetPipeFd(self, fd: io.TextIOWrapper) -> None:
        self._pipeFd = fd

    def GetPipeFd(self) -> io.TextIOWrapper:
        return self._pipeFd

    def preprocess(self) -> None:
        if self._nodeType == NodeType.LEAF:
            return

        fds = self.GetFdTriple()
        if self._splitType == SplitType.SEQ:
            self._leftNode.SetFdTriple(
                fdTriple(fds.GetIn(), fds.GetOut(), fds.GetErr())
            )
            self._rightNode.SetFdTriple(
                fdTriple(fds.GetIn(), fds.GetOut(), fds.GetErr())
            )
            self._leftNode.SetEnvScope(self._envScope)
            self._rightNode.SetEnvScope(self._envScope)
        elif self._splitType == SplitType.PIPE:
            self._pipeFd = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
            self._leftNode.SetFdTriple(
                fdTriple(fds.GetIn(), self._pipeFd, fds.GetErr())
            )
            self._rightNode.SetFdTriple(
                fdTriple(self._pipeFd, fds.GetOut(), fds.GetErr())
            )

            self._leftNode.SetEnvScope(deepcopy(self._envScope))
            self._rightNode.SetEnvScope(deepcopy(self._envScope))

        self._leftNode.preprocess()
        self._rightNode.preprocess()

    def process(self) -> None:
        assert self.isValid()
        if self._nodeType == NodeType.INNER:
            self._leftNode.process()
            if self._splitType == SplitType.PIPE:
                self._pipeFd.seek(0)
            self._rightNode.process()
        else:
            args: list[str] = splitIntoArguments(self._rawCmd, self._envScope)
            assert len(args) > 0
            cmd: Command | None = commands.lookup(args[0])
            if cmd:
                cmd(self._fdTriple, self._envScope, args)

    def isValid(self) -> bool:
        if self._nodeType == NodeType.NOT_INITIALIZED:
            return False
        elif self._nodeType == NodeType.INNER:
            if (
                self._splitType == SplitType.NOT_INITIALIZED
                or not self._leftNode
                or not self._rightNode
            ):
                return False
            if self._splitType == SplitType.PIPE and self._pipeFd is None:
                return False
        elif self._nodeType == NodeType.LEAF:
            if self._rawCmd is None:
                return False

        if self._envScope is None or self._fdTriple is None:
            return False

        return True
