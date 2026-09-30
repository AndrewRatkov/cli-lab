import sys

from commands import ShellExit
from interpreter import MasterClass, Parser, ParseError
from runtime import EnvScope, FdTriple


def run(string: str, fds: FdTriple | None = None, envs: EnvScope | None = None) -> int:
    if fds is None:
        fds = FdTriple()
    if envs is None:
        envs = EnvScope()

    parser: Parser = Parser(string)
    masterclass_root: MasterClass = parser.parse()

    fds.replace_nones(sys.stdin, sys.stdout, sys.stderr)
    masterclass_root.set_fd_triple(fds)
    masterclass_root.set_env_scope(envs)

    masterclass_root.preprocess()
    return masterclass_root.process()


def repl() -> int:
    envs: EnvScope = EnvScope.from_os_environ()
    while True:
        try:
            line: str = input(">> ")
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            continue

        if len(line.strip()) == 0:
            continue

        try:
            run(line, FdTriple(), envs)
        except ShellExit as e:
            return e.code
        except (ParseError, EOFError) as e:
            print(f"syntax error: {e}", file=sys.stderr)
        except KeyboardInterrupt:
            print(file=sys.stderr)
        except Exception as e:
            print(f"error: {e}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(repl())
