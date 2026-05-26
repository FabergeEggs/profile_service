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
