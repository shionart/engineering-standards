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
        # The closing-block check is on by default. Only an explicit "off" value turns it off.
        reply_setting = env.get("ENG_STANDARDS_REPLY_CHECK", "").strip().lower()
        reply_check = reply_setting not in ("0", "false", "off", "no")
        return cls(state_dir=state_dir, reply_check=reply_check)
