from tg_assistant.cli import build_parser


def test_search_args():
    args = build_parser().parse_args(
        ["search", "iphone", "--chat", "123", "--chat", "me", "--limit", "5"]
    )
    assert args.command == "search"
    assert args.query == "iphone"
    assert args.chat == ["123", "me"]
    assert args.limit == 5


def test_dialogs_default_limit():
    args = build_parser().parse_args(["dialogs"])
    assert args.command == "dialogs"
    assert args.limit == 100


def test_status_command():
    args = build_parser().parse_args(["status"])
    assert args.command == "status"
