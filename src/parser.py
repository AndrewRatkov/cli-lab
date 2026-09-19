from src.masterclass import MasterClass, NodeType, SplitType


class ParseError(Exception):
    pass


class Parser:
    """Parses the input and returns a tree of MaterClass
    """

    _LEVELS = ((';', SplitType.SEQ), ('|', SplitType.PIPE))


    def __init__(self, raw_string):
        self.s = raw_string


    def parse(self) -> MasterClass:
        return self._parse(self.s, allow_trailing=True)

    def _parse(self, s, allow_trailing=False) -> MasterClass:
        s = s.strip()
        if not s:
            raise ParseError("empty command")

        for sep, split_type in self._LEVELS:
            idx = self._top_positions(s, sep)
            # trailing ';' is allowed only for the whole input or a group body
            if sep == ';' and allow_trailing and idx and not s[idx[-1] + 1:].strip():
                s = s[:idx[-1]].rstrip()
                idx.pop()

            if idx:
                i = idx[-1]
                return self._inner(split_type, s,
                                   self._parse(s[:i]),
                                   self._parse(s[i + 1:]))

        return self._parse_atom(s)


    def _parse_atom(self, s) -> MasterClass:
        if s.startswith('{'):
            close = next(i for i, c, d in self._scan(s) if c == '}' and d == 0)
            if s[close + 1:].strip():
                raise ParseError(f"text after '}}' in {s!r}")
            return self._parse(s[1:close], allow_trailing=True)     # brackets are removed, content is parsed again
        return self._leaf(s)

    
    @staticmethod
    def _inner(split_type, raw, left, right) -> MasterClass:
        node = MasterClass()
        node.SetNodeType(NodeType.INNER)
        node.SetSplitType(split_type)
        node.SetRawCmd(raw)
        node.SetLeftNode(left)
        node.SetRightNode(right)
        return node


    @staticmethod
    def _leaf(raw) -> MasterClass:
        node = MasterClass()
        node.SetNodeType(NodeType.LEAF)
        node.SetRawCmd(raw)
        return node


    def _top_positions(self, s, sep):
        """Indices of sep at the top level (outside brackets and quotes)."""
        return [i for i, c, d in self._scan(s) if c == sep and d == 0]


    @staticmethod
    def _scan(s):
        """Returns (index, character, depth) for characters outside quotes.
        For paired '{' and '}' the depth is the same (outer level)."""
        depth, quote, i = 0, None, 0
        while i < len(s):
            c = s[i]
            if c == '\\' and quote != "'":       # escaping: skip 2 characters
                i += 2
                continue
            if quote:
                if c == quote:
                    quote = None
            elif c in "'\"":
                quote = c
            elif c == '{':
                yield i, c, depth
                depth += 1
            elif c == '}':
                depth -= 1
                if depth < 0:
                    raise ParseError(f"extra '}}' in position {i}")
                yield i, c, depth
            else:
                yield i, c, depth
            i += 1
        if quote:
            raise ParseError("unterminated quote")
        if depth:
            raise ParseError("unterminated '{'")


    def dump(self, node, indent=0):
        pad = "  " * indent
        if node.GetNodeType() == NodeType.LEAF:
            print(f"{pad}{node.GetRawCmd()!r}")
        else:
            print(f"{pad}[{node.GetSplitType().value}] {node.GetRawCmd()!r}")
            self.dump(node.GetLeftNode(), indent + 1)
            self.dump(node.GetRightNode(), indent + 1)