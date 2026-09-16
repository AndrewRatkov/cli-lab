from command import Command
from commands.echo import echo

# Explicit registry of built-in utilities.
COMMANDS: list[Command] = [
    Command("echo", echo),
]

_by_name: dict[str, Command] = {cmd.name: cmd for cmd in COMMANDS}


def lookup(name: str) -> Command | None:
    return _by_name.get(name)
