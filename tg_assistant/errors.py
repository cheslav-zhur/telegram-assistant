"""Structured JSON errors for machine-readable CLI commands."""

from __future__ import annotations

import json
import sys
from typing import Any


def emit_json(payload: dict[str, Any], *, file=None) -> None:
    out = sys.stdout if file is None else file
    json.dump(payload, out, ensure_ascii=False, default=str)
    out.write("\n")
    out.flush()


def fail(
    error: str,
    message: str,
    *,
    seconds: int | None = None,
    exit_code: int = 1,
    **extra: Any,
) -> int:
    payload: dict[str, Any] = {
        "ok": False,
        "error": error,
        "message": message,
    }
    if seconds is not None:
        payload["seconds"] = seconds
    payload.update(extra)
    emit_json(payload)
    return exit_code


def ok_payload(**fields: Any) -> dict[str, Any]:
    return {"ok": True, **fields}
