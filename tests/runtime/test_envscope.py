from runtime import EnvScope


def test_set_then_get() -> None:
    scope = EnvScope()
    scope.set("univesity", "SPbU")
    assert scope.get("univesity") == "SPbU"


def test_set_overwrites_value() -> None:
    scope = EnvScope()
    scope.set("univesity", "HSE")
    scope.set("univesity", "SPbU")
    assert scope.get("univesity") == "SPbU"


def test_get_missing_key_returns_empty_string() -> None:
    scope = EnvScope()
    assert scope.get("university") == ""


def test_default_scopes_are_independent() -> None:
    EnvScope().set("university", "SPbU")
    assert EnvScope().get("university") == ""


def test_copy_is_independent() -> None:
    scope = EnvScope()
    scope.set("university", "SPbU")
    copy = scope.copy()
    copy.set("university", "HSE")
    assert scope.get("university") == "SPbU"


def test_from_os_environ(monkeypatch) -> None:
    monkeypatch.setenv("CLI_LAB_TEST", "42")
    assert EnvScope.from_os_environ().get("CLI_LAB_TEST") == "42"
