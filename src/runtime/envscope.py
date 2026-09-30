from __future__ import annotations

import os


class EnvScope:
    """Wrapper over a str -> str dictionary."""

    def __init__(self, d: dict[str, str] | None = None) -> None:
        self._vars: dict[str, str] = dict(d) if d else {}

    def set(self, key: str, value: str) -> None:
        self._vars[key] = value

    def get(self, key: str) -> str:
        return self._vars.get(key, "")

    @classmethod
    def from_os_environ(cls) -> EnvScope:
        return cls(dict(os.environ))

    def copy(self) -> EnvScope:
        return EnvScope(self._vars)

    def as_dict(self) -> dict[str, str]:
        return dict(self._vars)
