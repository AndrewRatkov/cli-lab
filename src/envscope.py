class EnvScope:
    """Wrapper over a str -> str dictionary."""

    def __init__(self, d: dict[str, str] = {}) -> None:
        self._vars: dict[str, str] = d

    def set(self, key: str, value: str) -> None:
        self._vars[key] = value

    def get(self, key: str) -> str:
        return self._vars.get(key, "")
