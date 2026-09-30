from commands.command import Command
from commands.cat import cat
from commands.echo import echo
from commands.exit import ShellExit, exit
from commands.external import external
from commands.pwd import pwd
from commands.wc import wc

# Explicit registry of built-in utilities.
COMMANDS: list[Command] = [
    Command("echo", echo),
    Command("cat", cat),
    Command("wc", wc),
    Command("pwd", pwd),
    Command("exit", exit),
]

EXTERNAL: Command = Command("external", external)

_by_name: dict[str, Command] = {cmd.name: cmd for cmd in COMMANDS}


def lookup(name: str) -> Command:
    return _by_name.get(name, EXTERNAL)
