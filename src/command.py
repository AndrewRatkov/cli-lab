from collections.abc import Callable
from dataclasses import dataclass

from envscope import envScope
from fdtriple import fdTriple

CommandFn = Callable[[fdTriple, envScope, list[str]], int]


@dataclass(frozen=True)
class Command:
    name: str
    run: CommandFn

    def __call__(self, fds: fdTriple, env: envScope, args: list[str]) -> int:
        assert len(args) > 0
        return self.run(fds, env, args)
