"""Remembers, per Claude Code session, that the engineering-standards skill was used."""

import re
from pathlib import Path


class FlagStore:
    def __init__(self, folder: Path) -> None:
        self._folder = folder

    def _file(self, session_id: str) -> Path:
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", session_id)
        return self._folder / f"{safe}.flag"

    def has(self, session_id: str) -> bool:
        return self._file(session_id).exists()

    def mark(self, session_id: str) -> None:
        self._folder.mkdir(parents=True, exist_ok=True)
        self._file(session_id).write_text("engineering-standards used\n", encoding="utf-8", newline="\n")

    def clear(self, session_id: str) -> None:
        self._file(session_id).unlink(missing_ok=True)
