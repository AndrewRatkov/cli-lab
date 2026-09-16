class envScope:
    """Wrapper over a str -> str dictionary."""

    def __init__(self) -> None:
        self._vars: dict[str, str] = {}

    def Set(self, key: str, value: str) -> None:
        self._vars[key] = value

    def Get(self, key: str) -> str | None:
        return self._vars.get(key)
