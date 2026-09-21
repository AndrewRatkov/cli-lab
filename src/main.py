from interpreter import MasterClass, Parser
from runtime import EnvScope, FdTriple


def run(string: str, fds: FdTriple = FdTriple(), envs: EnvScope = EnvScope()) -> None:
    parser: Parser = Parser(string)
    masterclass_root: MasterClass = parser.parse()

    fds.replace_nones()
    masterclass_root.set_fd_triple(fds)
    masterclass_root.set_env_scope(envs)

    masterclass_root.preprocess()
    masterclass_root.process()


if __name__ == "__main__":
    string: str = input(">> ")
    run(string)
