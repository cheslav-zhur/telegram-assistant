from types import SimpleNamespace

from tg_assistant.auth_cmd import _identity, _mask_phone


def test_mask_phone_short():
    assert _mask_phone(None) is None
    assert _mask_phone("12") == "***"
    assert _mask_phone("+123") == "***"


def test_mask_phone_keeps_last_four():
    assert _mask_phone("+79161234567") == "+*******4567"


def test_identity():
    me = SimpleNamespace(
        id=1,
        username="sec",
        phone="+79161234567",
        first_name="Sec",
    )
    assert _identity(me) == {
        "id": 1,
        "username": "sec",
        "phone_masked": "+*******4567",
        "first_name": "Sec",
    }
