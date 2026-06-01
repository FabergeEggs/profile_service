from src.domain.display_name import build_display_name


def test_build_display_name_from_first_and_last() -> None:
    assert build_display_name(first_name="Ann", last_name="Bee") == "Ann Bee"


def test_build_display_name_falls_back_to_username() -> None:
    assert build_display_name(username="alice") == "alice"


def test_build_display_name_falls_back_to_email() -> None:
    assert build_display_name(email="alice@example.com") == "alice@example.com"


def test_build_display_name_returns_empty_when_no_data() -> None:
    assert build_display_name() == ""


def test_build_display_name_ignores_whitespace_only_parts() -> None:
    assert build_display_name(first_name="  ", last_name="", username="nick") == "nick"
