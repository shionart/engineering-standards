"""Entry point of the engineering-standards gate, called by Claude Code hooks.

  hook.py gate    PreToolUse   blocks code writes until the skill was used in this session
  hook.py mark    PostToolUse  on the Skill tool: remembers that engineering-standards was used
  hook.py reset   SessionStart forgets it again (new session, resume, compaction, clear)
  hook.py reply   Stop         (only when ENG_STANDARDS_REPLY_CHECK=1) sends a reply back when it lacks the closing block (Updated, Created,
                               Removed, Not done, Relevant skill(s) not used)

Exit code 2 blocks the tool call and shows the message to Claude. Any problem reading the
input allows the call: a broken hook must never lock every tool.
"""

import json
import sys
from collections.abc import Callable
from dataclasses import dataclass

from config import Config
from flagstore import FlagStore
from gate_rules import is_standards_skill, needs_gate
from reply_rules import SKILLS_LABEL, missing_sections
from transcript import last_reply_text

BLOCK_MESSAGE = (
    "BLOCKED by the engineering-standards gate. This call writes or changes code or a script, and the "
    "`engineering-standards` skill has not been used in this session (or the context was reset). "
    "Call the Skill tool with skill \"engineering-standards\", follow it (stack, plan, design, tests first), "
    "then retry this call. This rule comes from the project's engineering standards and has no exceptions."
)


REPLY_MESSAGE = (
    "Your reply is missing part of the required closing block: {missing}. The project's engineering standards require every reply to end "
    "with Updated, Created, Removed and Not done (write \"none\" when a list is empty) and a line "
    "\"" + SKILLS_LABEL + ": ...\" naming relevant skills you did not use (or \"none\"). "
    "Add the block now, then finish."
)


@dataclass(frozen=True)
class Result:
    exit_code: int
    message: str = ""


def handle(
    mode: str,
    payload: dict,
    store: FlagStore,
    config: Config,
    read_reply: Callable[[str], str | None] = last_reply_text,
) -> Result:
    if mode == "reply":
        return _check_reply(payload, read_reply) if config.reply_check else Result(0)
    session = payload.get("session_id")
    if not session:
        return Result(0)
    if mode == "reset":
        store.clear(session)
    elif mode == "mark":
        if payload.get("tool_name") == "Skill" and is_standards_skill((payload.get("tool_input") or {}).get("skill")):
            store.mark(session)
    elif mode == "gate":
        if needs_gate(payload.get("tool_name", ""), payload.get("tool_input") or {}) and not store.has(session):
            return Result(2, BLOCK_MESSAGE)
    return Result(0)


def _check_reply(payload: dict, read_reply: Callable[[str], str | None]) -> Result:
    if payload.get("stop_hook_active"):  # already sent back once: never loop
        return Result(0)
    text = read_reply(str(payload.get("transcript_path") or ""))
    if not text:
        return Result(0)
    missing = missing_sections(text)
    if not missing:
        return Result(0)
    return Result(2, REPLY_MESSAGE.format(missing=", ".join(missing)))


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else ""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0
    config = Config.from_env()
    result = handle(mode, payload, FlagStore(config.state_dir), config)
    if result.message:
        print(result.message, file=sys.stderr)
    return result.exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
