"""Remembers, per Claude Code session and per agent, that the engineering-standards skill was used.

Layout: <folder>/<session>/main.flag for the main agent and <folder>/<session>/agent-<id>.flag for
each subagent, so one session folder can be wiped in a single step.
"""

import os
import re
import shutil
from pathlib import Path

_MAIN_FLAG = "main.flag"
MAX_AGE_SECONDS = 7 * 24 * 3600


def _safe(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", text)


def _newest_mtime(folder: Path) -> float:
    return max([folder.stat().st_mtime, *(child.stat().st_mtime for child in folder.iterdir())])


class FlagStore:
    def __init__(self, folder: Path) -> None:
        self._folder = folder

    def _session_folder(self, session_id: str) -> Path:
        return self._folder / _safe(session_id)

    def _file(self, session_id: str, agent_id: str | None) -> Path:
        name = _MAIN_FLAG if agent_id is None else f"agent-{_safe(agent_id)}.flag"
        return self._session_folder(session_id) / name

    def has(self, session_id: str, agent_id: str | None = None) -> bool:
        return self._file(session_id, agent_id).exists()

    def mark(self, session_id: str, agent_id: str | None = None) -> None:
        path = self._file(session_id, agent_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("engineering-standards used\n", encoding="utf-8", newline="\n")

    def clear(self, session_id: str, agent_id: str | None = None) -> None:
        self._file(session_id, agent_id).unlink(missing_ok=True)

    def clear_session(self, session_id: str) -> None:
        shutil.rmtree(self._session_folder(session_id), ignore_errors=True)

    def refresh(self, session_id: str, agent_id: str | None, now: float) -> None:
        """Mark the flag as used just now, so an active session is never pruned. `now` is the clock."""
        try:
            os.utime(self._file(session_id, agent_id), (now, now))
        except FileNotFoundError:
            pass

    def prune(self, now: float) -> None:
        """Delete session folders whose newest file or folder is older than MAX_AGE_SECONDS. `now` is the clock."""
        if not self._folder.is_dir():
            return
        for entry in self._folder.iterdir():
            try:
                if entry.is_dir() and _newest_mtime(entry) < now - MAX_AGE_SECONDS:
                    shutil.rmtree(entry, ignore_errors=True)
            except OSError:  # removed by another process in the meantime
                continue
