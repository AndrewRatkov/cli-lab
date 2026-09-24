from interpreter.masterclass import MasterClass, NodeType, SplitType


class ParseError(Exception):
    pass


class Parser:
    """Parses the input and returns a tree of MaterClass"""

    _LEVELS = ((";", SplitType.SEQ), ("|", SplitType.PIPE))

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
            if sep == ";" and allow_trailing and idx and not s[idx[-1] + 1 :].strip():
                s = s[: idx[-1]].rstrip()
                idx.pop()

            if idx:
                i = idx[-1]
                return self._inner(
                    split_type, s, self._parse(s[:i]), self._parse(s[i + 1 :])
                )

        return self._parse_atom(s)

    def _parse_atom(self, s) -> MasterClass:
        if s.startswith("{"):
            close = next(i for i, c, d in self._scan(s) if c == "}" and d == 0)
            if s[close + 1 :].strip():
                raise ParseError(f"text after '}}' in {s!r}")
            return self._parse(
                s[1:close], allow_trailing=True
            )  # brackets are removed, content is parsed again
        return self._leaf(s)

    @staticmethod
    def _inner(split_type, raw, left, right) -> MasterClass:
        node = MasterClass()
        node.set_node_type(NodeType.INNER)
        node.set_split_type(split_type)
        node.set_raw_cmd(raw)
        node.set_left_node(left)
        node.set_right_node(right)
        return node

    @staticmethod
    def _leaf(raw) -> MasterClass:
        node = MasterClass()
        node.set_node_type(NodeType.LEAF)
        node.set_raw_cmd(raw)
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
            if c == "\\" and quote != "'":  # escaping: skip 2 characters
                i += 2
                continue
            if quote:
                if c == quote:
                    quote = None
            elif c in "'\"":
                quote = c
            elif c == "{":
                yield i, c, depth
                depth += 1
            elif c == "}":
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
        if node.get_node_type() == NodeType.LEAF:
            print(f"{pad}{node.get_raw_cmd()!r}")
        else:
            print(f"{pad}[{node.get_split_type().value}] {node.get_raw_cmd()!r}")
            self.dump(node.get_left_node(), indent + 1)
            self.dump(node.get_right_node(), indent + 1)
