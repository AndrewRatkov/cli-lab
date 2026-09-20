from parser import Parser
from masterclass import MasterClass
from fdtriple import fdTriple
from envscope import envScope


def run(string: str, fds: fdTriple = fdTriple(), envs: envScope = envScope()) -> None:
    parser: Parser = Parser(string)
    masterclass_root: MasterClass = parser.parse()

    masterclass_root.SetFdTriple(fds)
    masterclass_root.SetEnvScope(envs)

    masterclass_root.preprocess()
    masterclass_root.process()


if __name__ == "__main__":
    string: str = input(">> ")
    run(string)
