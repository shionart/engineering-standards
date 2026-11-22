"""Reads the final assistant message out of a Claude Code transcript (a JSON Lines file)."""

import json
from pathlib import Path


def last_reply_text(transcript_path: str) -> str | None:
    """The text of the last assistant message, or None when there is none, it has no text, or the file is unreadable."""
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("type") != "assistant":
            continue
        content = (entry.get("message") or {}).get("content")
        blocks = content if isinstance(content, list) else []
        texts = [b.get("text", "") for b in blocks if isinstance(b, dict) and b.get("type") == "text"]
        joined = "\n".join(t for t in texts if t)
        return joined or None
    return None
