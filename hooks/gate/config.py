"""The one place configuration is read: environment variables, loaded once at start."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

DEFAULT_STATE_DIR = Path.home() / ".claude" / "engineering-standards-gate" / "state"


@dataclass(frozen=True)
class Config:
    state_dir: Path
    reply_check: bool

    @classmethod
    def from_env(cls, env: Mapping[str, str] = os.environ) -> "Config":
        if env.get("ENG_STANDARDS_STATE_DIR"):
            state_dir = Path(env["ENG_STANDARDS_STATE_DIR"])
        elif env.get("CLAUDE_PLUGIN_DATA"):
            state_dir = Path(env["CLAUDE_PLUGIN_DATA"]) / "state"
        else:
            state_dir = DEFAULT_STATE_DIR
        return cls(state_dir=state_dir, reply_check=env.get("ENG_STANDARDS_REPLY_CHECK") == "1")
