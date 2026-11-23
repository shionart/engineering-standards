"""The one place configuration is read: environment variables, loaded once at start."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from gate_rules import CODE_EXTENSIONS

DEFAULT_STATE_DIR = Path.home() / ".claude" / "engineering-standards-gate" / "state"
_OFF_VALUES = ("0", "false", "off", "no")


def _is_on(env: Mapping[str, str], name: str) -> bool:
    """On by default. Only an explicit "off" value turns a switch off."""
    return env.get(name, "").strip().lower() not in _OFF_VALUES


def _extensions(text: str) -> tuple[str, ...]:
    names = (part.strip().lstrip(".").lower() for part in text.split(","))
    return tuple(name for name in names if name)


@dataclass(frozen=True)
class Config:
    state_dir: Path
    reply_check: bool
    gate: bool = True
    code_extensions: tuple[str, ...] = CODE_EXTENSIONS

    @classmethod
    def from_env(cls, env: Mapping[str, str] = os.environ) -> "Config":
        if env.get("ENG_STANDARDS_STATE_DIR"):
            state_dir = Path(env["ENG_STANDARDS_STATE_DIR"])
        elif env.get("CLAUDE_PLUGIN_DATA"):
            state_dir = Path(env["CLAUDE_PLUGIN_DATA"]) / "state"
        else:
            state_dir = DEFAULT_STATE_DIR
        return cls(
            state_dir=state_dir,
            reply_check=_is_on(env, "ENG_STANDARDS_REPLY_CHECK"),
            gate=_is_on(env, "ENG_STANDARDS_GATE"),
            code_extensions=tuple(
                dict.fromkeys(CODE_EXTENSIONS + _extensions(env.get("ENG_STANDARDS_EXTRA_EXTENSIONS", "")))
            ),
        )
