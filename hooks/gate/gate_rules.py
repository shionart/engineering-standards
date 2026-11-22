"""Pure rules of the engineering-standards gate: what counts as writing code. No files, no clock."""

import re

CODE_EXTENSIONS = (
    "rs py ts tsx js jsx mjs cjs sh bash ps1 bat cmd sql java go cs kt swift rb php css scss html svelte vue "
    "c h cpp hpp toml"
).split()
_EXT = "|".join(CODE_EXTENSIONS)

_CODE_PATH = re.compile(rf"\.(?:{_EXT})$", re.IGNORECASE)
_PATH_TOKEN = rf"[^\s|&;<>\"')]*\.(?:{_EXT})\b"

# A redirect whose target is a code file, tee, sed -i, or our own tools/edit.py helper.
_WRITE_TO_CODE = [
    re.compile(rf">>?\s*[\"']?{_PATH_TOKEN}", re.IGNORECASE),
    re.compile(rf"\btee\b[^|;&]*{_PATH_TOKEN}", re.IGNORECASE),
    re.compile(rf"\bsed\s+-[a-z]*i[^|;&]*{_PATH_TOKEN}", re.IGNORECASE),
    re.compile(rf"\bedit\(\s*[\"'][^\"']*\.(?:{_EXT})[\"']", re.IGNORECASE),
]
# Language-level file writes only count when a code file is named somewhere in the command.
_WRITE_CALL = re.compile(r"write_text|write_bytes|\.write\(|open\([^)]*[\"'][wa]b?[\"']")
_ANY_CODE_PATH = re.compile(_PATH_TOKEN, re.IGNORECASE)

_FILE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
SKILL = "engineering-standards"


def is_code_path(path: str) -> bool:
    return bool(path) and bool(_CODE_PATH.search(path))


def bash_writes_code(command: str) -> bool:
    if any(rule.search(command) for rule in _WRITE_TO_CODE):
        return True
    return bool(_WRITE_CALL.search(command)) and bool(_ANY_CODE_PATH.search(command))


def needs_gate(tool_name: str, tool_input: dict) -> bool:
    """True when this tool call writes or changes code or a script."""
    if tool_name in _FILE_TOOLS:
        return is_code_path(str(tool_input.get("file_path") or tool_input.get("notebook_path") or ""))
    if tool_name == "Bash":
        return bash_writes_code(str(tool_input.get("command") or ""))
    return False


def is_standards_skill(name: str | None) -> bool:
    return bool(name) and (name == SKILL or name.endswith(f":{SKILL}"))
