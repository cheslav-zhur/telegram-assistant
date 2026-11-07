import io
import json

from tg_assistant.errors import emit_json, fail, ok_payload


def test_ok_payload():
    assert ok_payload(count=2, hits=[]) == {"ok": True, "count": 2, "hits": []}


def test_emit_json_writes_one_line():
    buf = io.StringIO()
    emit_json({"ok": True, "n": 1}, file=buf)
    assert json.loads(buf.getvalue().strip()) == {"ok": True, "n": 1}


def test_fail_emits_envelope(capsys):
    code = fail("flood_wait", "wait", seconds=30)
    assert code == 1
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload == {
        "ok": False,
        "error": "flood_wait",
        "message": "wait",
        "seconds": 30,
    }
