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
