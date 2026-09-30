from runtime import EnvScope, FdTriple


class ShellExit(Exception):

    def __init__(self, code: int = 0) -> None:
        super().__init__(code)
        self.code = code


def exit(fds: FdTriple, env: EnvScope, args: list[str]) -> int:
    code = 0
    if len(args) > 1:
        try:
            code = int(args[1])
        except ValueError:
            fds.get_err().write(f"exit: {args[1]}: numeric argument required\n")
            code = 2
    raise ShellExit(code)
