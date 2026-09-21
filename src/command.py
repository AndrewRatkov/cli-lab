from collections.abc import Callable
from dataclasses import dataclass

from envscope import EnvScope
from fdtriple import FdTriple

CommandFn = Callable[[FdTriple, EnvScope, list[str]], int]


@dataclass(frozen=True)
class Command:
    name: str
    run: CommandFn

    def __call__(self, fds: FdTriple, env: EnvScope, args: list[str]) -> int:
        assert len(args) > 0
        return self.run(fds, env, args)
