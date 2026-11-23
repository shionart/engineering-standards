"""Entry point of the engineering-standards gate, called by Claude Code hooks.

  hook.py gate    PreToolUse   blocks code writes until the skill was used by the calling agent
                               (off with ENG_STANDARDS_GATE=0; more file types via ENG_STANDARDS_EXTRA_EXTENSIONS)
  hook.py mark    PostToolUse  on the Skill tool: remembers that the calling agent used engineering-standards
  hook.py reset   SessionStart forgets it for the main agent and every subagent of the session, and deletes
                               session folders older than 7 days
  hook.py agent_stop SubagentStop forgets it for the subagent that just finished
  hook.py reply   Stop         (on by default, off with ENG_STANDARDS_REPLY_CHECK=0) sends a reply back when it lacks the closing block (Updated, Created,
                               Removed, Not done, Relevant skill(s) not used)

Subagents share the parent's session_id, so the flag is keyed by (session_id, agent_id). Hook input
carries agent_id only when the call happens inside a subagent; without it the caller is the main agent.

Exit code 2 blocks the tool call and shows the message to Claude. Any problem reading the
input allows the call: a broken hook must never lock every tool.
"""

import json
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass

from config import Config
from flagstore import FlagStore
from gate_rules import is_standards_skill, needs_gate
from reply_rules import SKILLS_LABEL, missing_sections
from transcript import last_reply_text

BLOCK_MESSAGE = (
    "BLOCKED by the engineering-standards gate. This call writes or changes code or a script, and the "
    "`engineering-standards` skill has not been used by this agent in this session (or the context was reset). "
    "Each agent must load it itself: a subagent does not inherit it from the main agent or from another subagent. "
    "Call the Skill tool with skill \"engineering-standards\", follow it (stack, plan, design, tests first), "
    "then retry this call. This rule comes from the project's engineering standards. "
    "To turn the gate off, set ENG_STANDARDS_GATE=0 (see the plugin README)."
)


REPLY_MESSAGE = (
    "Your reply is missing part of the required closing block: {missing}. The project's engineering standards require every reply to end "
    "with Updated, Created, Removed and Not done (write \"none\" when a list is empty) and a line "
    "\"" + SKILLS_LABEL + ": ...\" naming relevant skills you did not use (or \"none\"). "
    "Add the block now, then finish. To turn this check off, set ENG_STANDARDS_REPLY_CHECK=0."
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
    now: Callable[[], float] = time.time,
) -> Result:
    if mode == "reply":
        return _check_reply(payload, read_reply) if config.reply_check else Result(0)
    session = payload.get("session_id")
    if not session:
        return Result(0)
    agent = payload.get("agent_id") or None  # absent or empty: the main agent
    if mode == "reset":
        store.clear_session(session)
        store.prune(now())
    elif mode == "agent_stop":
        if agent:
            store.clear(session, agent)
    elif mode == "mark":
        if payload.get("tool_name") == "Skill" and is_standards_skill((payload.get("tool_input") or {}).get("skill")):
            store.mark(session, agent)
    elif mode == "gate" and config.gate:
        if store.has(session, agent):
            store.refresh(session, agent, now())  # a session in use is never pruned
        elif needs_gate(payload.get("tool_name", ""), payload.get("tool_input") or {}, config.code_extensions):
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
