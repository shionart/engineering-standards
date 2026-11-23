"""Pure rules of the engineering-standards gate: what counts as writing code. No files, no clock, no environment.

The list of code extensions is a parameter, so the caller decides what counts as code. A shell command is cut
into its separate commands first, and each one is judged on its own.
"""

import re

CODE_EXTENSIONS = tuple(
    (
        "rs py ts tsx js jsx mjs cjs sh bash ps1 bat cmd sql java go cs kt swift rb php css scss html svelte vue "
        "c h cpp hpp toml ipynb pl pm groovy gradle tf lua dart scala ex exs r zig nim"
    ).split()
)
_BUILD_FILES = {"dockerfile", "containerfile", "makefile", "jenkinsfile"}
_BACKUP_SUFFIXES = {"bak", "orig", "old", "tmp", "swp", "save"}

_FILE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
_SHELL_TOOLS = {"Bash", "PowerShell"}
SKILL = "engineering-standards"

# Whole words of the tool part of an MCP tool name (after the last "__"). The PreToolUse matcher in hooks.json is
# broader on purpose, it only decides whether the hook runs; a test checks it accepts everything these rules gate.
_MCP_WRITE_VERBS = {
    "write", "edit", "create", "move", "copy", "append", "patch", "update", "save", "put", "upload", "insert",
    "replace", "rename",
}
_NAME_WORD = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+")
_MCP_PATH_KEYS = ("path", "file_path", "filePath", "filename", "destination", "target", "notebook_path")
_MCP_PATH_LISTS = ("paths",)
_MCP_ENTRY_LISTS = ("edits", "files")  # lists of objects that carry a "path"

_REDIRECT_TARGET = re.compile(r">>?\s*[\"']?([^\s|&;<>\"')]+)")
_EDIT_HELPER = re.compile(r"\bedit\(\s*[\"']([^\"']+)[\"']")  # our own tools/edit.py helper
# Language-level file writes only count when a code file is named somewhere in the command.
_WRITE_CALL = re.compile(r"write_text|write_bytes|\.write\(|open\([^)]*[\"'][wa]b?[\"']")
_NAMED_PATH = re.compile(r"[^\s|&;<>\"'(),=]+")

_WORD = re.compile(r"\"[^\"]*\"|'[^']*'|\S+")
_REDIRECT_WORD = re.compile(r"\d*(?:>>?|<<?)&?(.*)", re.DOTALL)
_ASSIGNMENT = re.compile(r"[A-Za-z_]\w*=")

# Words that only prefix another command, with the options of theirs that take a value.
_WRAPPERS: dict[str, frozenset[str]] = {
    "time": frozenset(), "command": frozenset(), "builtin": frozenset(), "exec": frozenset(),
    "nohup": frozenset(), "env": frozenset({"-u"}), "sudo": frozenset({"-u", "-g"}), "nice": frozenset({"-n"}),
    "xargs": frozenset({"-I", "-n", "-L", "-P", "-d", "-E", "-s", "-a"}),
    "then": frozenset(), "do": frozenset(), "else": frozenset(), "elif": frozenset(), "if": frozenset(),
    "while": frozenset(), "until": frozenset(), "!": frozenset(),
}
_SHELLS = {"bash", "sh", "zsh", "dash", "powershell", "pwsh", "cmd"}
_DESTINATION_OPTIONS = {"-t", "--target-directory", "-destination"}
_DRY_RUN_FLAGS = {"--check", "--stat", "--numstat", "--summary", "--dry-run"}


def _is_build_file(name: str) -> bool:
    lower = name.lower()
    if lower in _BUILD_FILES or lower.endswith(".dockerfile"):
        return True
    if lower.startswith("dockerfile."):
        return not lower.endswith("~") and lower.rsplit(".", 1)[1] not in _BACKUP_SUFFIXES
    return False


class _CodePaths:
    """Decides whether a path names a code file, for one list of extensions."""

    def __init__(self, extensions: tuple[str, ...]) -> None:
        names = "|".join(re.escape(ext) for ext in extensions)
        self._with_extension = re.compile(rf".*\.(?:{names})", re.IGNORECASE)

    def is_path(self, path: str) -> bool:
        name = re.split(r"[\\/]", path)[-1]
        return bool(name) and (self._with_extension.fullmatch(name) is not None or _is_build_file(name))


def is_code_path(path: str, extensions: tuple[str, ...]) -> bool:
    return _CodePaths(extensions).is_path(path)


def _segments(command: str) -> list[str]:
    """The separate commands of a line: cut at ; | & and newlines, but not inside quotes."""
    segments: list[str] = []
    current: list[str] = []
    quote = ""
    i = 0
    while i < len(command):
        ch = command[i]
        if ch == "\n":  # a quote never runs past a line, so a stray apostrophe cannot hide later lines
            segments.append("".join(current))
            current, quote = [], ""
        elif ch == "\\" and quote != "'" and i + 1 < len(command) and command[i + 1] != "\n":
            current.append(command[i : i + 2])
            i += 1
        elif quote:
            current.append(ch)
            quote = "" if ch == quote else quote
        elif ch in "\"'":
            current.append(ch)
            quote = ch
        elif ch in ";|&":
            segments.append("".join(current))
            current = []
        else:
            current.append(ch)
        i += 1
    segments.append("".join(current))
    return segments


def _unquote(word: str) -> str:
    return word[1:-1] if len(word) >= 2 and word[0] == word[-1] and word[0] in "\"'" else word


def _words(segment: str) -> list[str]:
    """The words of one command, without redirections (2>/dev/null, > log) and without quote marks."""
    kept: list[str] = []
    skip_next = False
    for word in _WORD.findall(segment.strip(" \t()")):
        redirect = _REDIRECT_WORD.fullmatch(word)
        if skip_next:
            skip_next = False
        elif redirect:
            skip_next = not redirect.group(1)  # a bare operator: the next word is its target
        else:
            kept.append(_unquote(word))
    return kept


def _strip_wrappers(words: list[str]) -> list[str]:
    while words:
        word = words[0].lower()
        if _ASSIGNMENT.match(words[0]):
            words = words[1:]
        elif word in _WRAPPERS:
            value_options = _WRAPPERS[word]
            words = words[1:]
            while words and words[0].startswith("-") and len(words[0]) > 1:
                words = words[2:] if words[0] in value_options else words[1:]
        else:
            break
    return words


def _is_directory(path: str) -> bool:
    name = re.split(r"[\\/]", path)[-1]
    return path.endswith(("/", "\\")) or name in (".", "..") or "." not in name


def _copies_to_code(args: list[str], code: _CodePaths) -> bool:
    """cp, mv, install, Copy-Item, Move-Item: into a code file, or into a directory from a code file."""
    destination: str | None = None
    sources: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.lower() in _DESTINATION_OPTIONS and i + 1 < len(args):
            destination = args[i + 1]
            i += 1
        elif arg.lower().startswith("--target-directory="):
            destination = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            sources.append(arg)
        i += 1
    if destination is None:
        if len(sources) < 2:
            return False
        destination = sources.pop()
    return code.is_path(destination) or (_is_directory(destination) and any(code.is_path(s) for s in sources))


def _names_code_file(args: list[str], code: _CodePaths) -> bool:
    return any(code.is_path(arg) for arg in args if not arg.startswith("-"))


def _edits_in_place(args: list[str], code: _CodePaths) -> bool:
    in_place = any(arg == "--in-place" or re.match(r"-[A-Za-z]*i", arg) for arg in args if arg.startswith("-"))
    return in_place and _names_code_file(args, code)


def _applies_patch(args: list[str], code: _CodePaths) -> bool:
    return not any(arg in _DRY_RUN_FLAGS for arg in args)


def _git_writes_code(args: list[str], code: _CodePaths) -> bool:
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in ("-C", "-c") else 1
    subcommand, rest = (args[i], args[i + 1 :]) if i < len(args) else ("", [])
    if subcommand == "apply":
        return _applies_patch(rest, code)
    return subcommand == "mv" and _copies_to_code(rest, code)


def _url_names_code_file(url: str, code: _CodePaths) -> bool:
    return code.is_path(re.split(r"[?#]", url)[0])


def _curl_writes_code(args: list[str], code: _CodePaths) -> bool:
    outputs: list[str] = []
    urls: list[str] = []
    remote_name = False
    i = 0
    while i < len(args):
        arg = args[i]
        i += 1
        if arg.startswith("--"):
            option, equals, value = arg.partition("=")
            if option == "--output" and equals:
                outputs.append(value)
            elif option == "--output" and i < len(args):
                outputs.append(args[i])
                i += 1
            remote_name = remote_name or option in ("--remote-name", "--remote-name-all")
        elif re.fullmatch(r"-[A-Za-z]+", arg):
            remote_name = remote_name or "O" in arg
            if arg.endswith("o") and i < len(args):
                outputs.append(args[i])
                i += 1
        elif arg.startswith("-o"):
            outputs.append(arg[2:])
        elif not arg.startswith("-"):
            urls.append(arg)
    return any(code.is_path(out) for out in outputs) or (
        remote_name and any(_url_names_code_file(url, code) for url in urls)
    )


def _wget_writes_code(args: list[str], code: _CodePaths) -> bool:
    outputs: list[str] = []
    urls: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        i += 1
        short = re.fullmatch(r"-[A-Za-z]*O(.*)", arg)
        if arg.startswith("--output-document"):
            option, equals, value = arg.partition("=")
            if option == "--output-document":
                if not equals and i < len(args):
                    value, i = args[i], i + 1
                outputs.append(value)
        elif short:
            value = short.group(1)
            if not value and i < len(args):
                value, i = args[i], i + 1
            outputs.append(value)
        elif not arg.startswith("-"):
            urls.append(arg)
    if outputs:  # without an output name, wget saves under the name in the URL
        return any(code.is_path(out) for out in outputs)
    return any(_url_names_code_file(url, code) for url in urls)


_HANDLERS = {
    "cp": _copies_to_code, "mv": _copies_to_code, "install": _copies_to_code, "copy": _copies_to_code,
    "move": _copies_to_code, "cpi": _copies_to_code, "copy-item": _copies_to_code, "move-item": _copies_to_code,
    "tee": _names_code_file, "set-content": _names_code_file, "add-content": _names_code_file,
    "out-file": _names_code_file, "new-item": _names_code_file,
    "sed": _edits_in_place, "patch": _applies_patch, "git": _git_writes_code,
    "curl": _curl_writes_code, "wget": _wget_writes_code,
}


def _segment_writes_code(segment: str, code: _CodePaths) -> bool:
    words = _strip_wrappers(_words(segment))
    if not words:
        return False
    name = re.split(r"[\\/]", words[0])[-1].lower().removesuffix(".exe")
    if name in _SHELLS:  # bash -c "...", powershell -Command "...": look inside the script text
        return any(_writes_code(arg, code) for arg in words[1:] if " " in arg)
    handler = _HANDLERS.get(name)
    return handler is not None and handler(words[1:], code)


def _writes_code(command: str, code: _CodePaths) -> bool:
    if any(code.is_path(target) for target in _REDIRECT_TARGET.findall(command)):
        return True
    if any(code.is_path(target) for target in _EDIT_HELPER.findall(command)):
        return True
    if _WRITE_CALL.search(command) and any(code.is_path(path) for path in _NAMED_PATH.findall(command)):
        return True
    return any(_segment_writes_code(segment, code) for segment in _segments(command))


def command_writes_code(command: str, extensions: tuple[str, ...]) -> bool:
    """True when a Bash or PowerShell command writes a code file or applies a patch."""
    return _writes_code(command, _CodePaths(extensions))


def _paths_in(tool_input: dict) -> list[str]:
    """Every string in the input that sits in a field known to hold a file path."""
    found = [tool_input.get(key) for key in _MCP_PATH_KEYS]
    for key in _MCP_PATH_LISTS:
        value = tool_input.get(key)
        found.extend(value if isinstance(value, list) else [])
    for key in _MCP_ENTRY_LISTS:
        value = tool_input.get(key)
        entries = value if isinstance(value, list) else []
        found.extend(entry.get("path") for entry in entries if isinstance(entry, dict))
    return [item for item in found if isinstance(item, str)]


def _is_mcp_write_tool(tool_name: str) -> bool:
    words = {word.lower() for word in _NAME_WORD.findall(tool_name.rsplit("__", 1)[-1])}
    return not words.isdisjoint(_MCP_WRITE_VERBS)


def needs_gate(tool_name: str, tool_input: dict, extensions: tuple[str, ...]) -> bool:
    """True when this tool call writes or changes code or a script."""
    if tool_name in _FILE_TOOLS:
        return is_code_path(str(tool_input.get("file_path") or tool_input.get("notebook_path") or ""), extensions)
    if tool_name in _SHELL_TOOLS:
        return command_writes_code(str(tool_input.get("command") or ""), extensions)
    if tool_name.startswith("mcp__") and _is_mcp_write_tool(tool_name):
        code = _CodePaths(extensions)
        return any(code.is_path(path) for path in _paths_in(tool_input))
    return False


def is_standards_skill(name: str | None) -> bool:
    return bool(name) and (name == SKILL or name.endswith(f":{SKILL}"))
