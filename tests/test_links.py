from tg_assistant.links import chat_username, excerpt, message_link


def test_message_link_with_username():
    assert (
        message_link(message_id=42, chat_id=-1001, username="foo")
        == "https://t.me/foo/42"
    )


def test_message_link_private_channel():
    assert (
        message_link(message_id=7, chat_id=-1001234567890)
        == "https://t.me/c/1234567890/7"
    )


def test_message_link_unsupported_peer():
    assert message_link(message_id=1, chat_id=12345) is None
    assert message_link(message_id=1, chat_id=-12345) is None


def test_excerpt_empty_and_short():
    assert excerpt(None) == ""
    assert excerpt("  hi  ") == "hi"


def test_excerpt_truncates():
    assert excerpt("x" * 10, max_len=5) == "xxxx…"


def test_chat_username():
    class Entity:
        username = "bar"

    assert chat_username(Entity()) == "bar"
    assert chat_username(object()) is None
