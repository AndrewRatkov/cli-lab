from commands.command import Command
from commands.cat import cat
from commands.cd import cd
from commands.echo import echo
from commands.exit import ShellExit, exit
from commands.external import external
from commands.grep import grep
from commands.ls import ls
from commands.pwd import pwd
from commands.wc import wc

# Explicit registry of built-in utilities.
COMMANDS: list[Command] = [
    Command("echo", echo),
    Command("cat", cat),
    Command("wc", wc),
    Command("grep", grep),
    Command("pwd", pwd),
    Command("cd", cd),
    Command("ls", ls),
    Command("exit", exit),
]

EXTERNAL: Command = Command("external", external)

_by_name: dict[str, Command] = {cmd.name: cmd for cmd in COMMANDS}


def lookup(name: str) -> Command:
    return _by_name.get(name, EXTERNAL)
