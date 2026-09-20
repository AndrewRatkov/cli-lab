from src.envscope import envScope


def test_set_then_get() -> None:
    scope = envScope()
    scope.Set("univesity", "SPbU")
    assert scope.Get("univesity") == "SPbU"


def test_set_overwrites_value() -> None:
    scope = envScope()
    scope.Set("univesity", "HSE")
    scope.Set("univesity", "SPbU")
    assert scope.Get("univesity") == "SPbU"


def test_get_missing_key_returns_empty_string() -> None:
    scope = envScope()
    assert scope.Get("university") == ""
