from src.consumers.register_consumer import _extract_user_payload


def test_extract_user_payload_from_auth_service_event():
    event = {
        "event_type": "profile_service.user.registered",
        "data": {
            "user_id": "11111111-1111-1111-1111-111111111111",
            "email": "user@example.com",
            "first_name": "Ann",
        },
    }
    payload = _extract_user_payload(event)
    assert payload["user_id"] == "11111111-1111-1111-1111-111111111111"
    assert payload["email"] == "user@example.com"


def test_extract_user_payload_from_flat_event():
    event = {
        "user_id": "22222222-2222-2222-2222-222222222222",
        "email": "flat@example.com",
    }
    payload = _extract_user_payload(event)
    assert payload["email"] == "flat@example.com"


def test_extract_user_payload_returns_empty_dict_for_empty_event():
    assert _extract_user_payload({}) == {}


def test_extract_user_payload_falls_back_when_nested_data_has_no_user_id():
    event = {"data": {"email": "only-email@example.com"}}
    assert _extract_user_payload(event) == event


def test_extract_user_payload_prefers_nested_data_block():
    event = {
        "data": {
            "user_id": "33333333-3333-3333-3333-333333333333",
            "email": "nested@example.com",
            "first_name": "Nested",
        },
        "user_id": "00000000-0000-0000-0000-000000000000",
    }
    payload = _extract_user_payload(event)
    assert payload["email"] == "nested@example.com"
    assert payload["first_name"] == "Nested"
