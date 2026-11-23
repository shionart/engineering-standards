# engineering-standards

A Claude Code plugin with one skill, `engineering-standards`, and a set of hooks that make Claude load it before it writes code. It is for developers who want Claude to pick a fitting stack, plan, test first and verify its work on every task, including small scripts.

## Install

```
/plugin marketplace add shionart/engineering-standards
/plugin install engineering-standards@shionart
```

Then run `/engineering-standards:setup` to check which companion skills you have.

Manual alternative, skill only and without the gate: copy `skills/engineering-standards` into `~/.claude/skills/`.

## What the skill does

Before any code or script is written, Claude loads the skill and follows these steps in order:

0. Stack first: pick the technology by fit to the problem, not by what is installed, and record the decision.
1. Plan: small, verifiable steps; for large work, a fresh-eyes review of the plan by a subagent.
2. Design before code: reuse first (drop it, reuse it, use the standard library, use a dependency), then design the minimum.
3. Apply the rules below.
4. Test first: a failing test before the code for each rule.
5. Implement: the shortest diff that reaches every caller, test and config.
6. Simplify and review.
7. Verify: run the tests and the real thing before saying it is done.

The rules that always apply:

1. One reason to change per module; rules, I/O adapters and entry layer live apart.
2. Pure core, side effects at the edges.
3. Depend on abstractions and pass them in as parameters.
4. Extend by adding a unit, not by editing a long function.
5. Small interfaces: take only what you use.
6. Explicit types and specific errors; no silent failure.
7. Configuration in one place, read once.
8. No dead code, no duplicate tools, no leftovers.
9. Names say what things are; comments explain why.
10. Containers stay lean (Dockerfile checklist in `docker-images.md`).
11. A logo comes before frontend design when the project has none.

## The gate

The plugin registers five hooks (`hooks/hooks.json`):

- `PreToolUse` (`gate`): blocks a call that writes a code or script file until the calling agent has used the skill. It looks at the Edit, Write, NotebookEdit and MultiEdit tools, at Bash and PowerShell commands, and at MCP tools whose tool name (the part after the last `__`) has one of these as a whole word (`writeFile`, `update_file`; not `get_output`): write, edit, create, move, copy, append, patch, update, save, put, upload, insert, replace or rename and whose path argument is a code file. The hook matcher in `hooks.json` lets only these MCP tools start the hook, so MCP reads cost nothing.
- `PostToolUse` on the Skill tool (`mark`): records that the calling agent (main or subagent) used the skill.
- `SessionStart` (`reset`): forgets it again, for the main agent and every subagent, on a new session, resume, clear or compaction. It also deletes flag folders of sessions not used for 7 days. Every allowed gate check refreshes the caller's flag, so a session in use is never deleted.
- `SubagentStop` (`agent_stop`): forgets the flag of the subagent that finished.
- `Stop` (`reply`): sends a reply back if it lacks a closing block (Updated, Created, Removed, Not done, and a line naming relevant skills not used).

What counts as writing code:

- Files with a code extension: `rs py ts tsx js jsx mjs cjs sh bash ps1 bat cmd sql java go cs kt swift rb php css scss html svelte vue c h cpp hpp toml ipynb pl pm groovy gradle tf lua dart scala ex exs r zig nim`, plus `Dockerfile`, `Containerfile`, `Makefile`, `Jenkinsfile`, `*.Dockerfile` and `Dockerfile.<suffix>` (not backup suffixes: `bak`, `orig`, `old`, `tmp`, `swp`, `save` or a trailing `~`). YAML, JSON, Markdown and text files are not gated on purpose. Add more types with `ENG_STANDARDS_EXTRA_EXTENSIONS`.
- Shell commands that write such a file. A line is cut into its separate commands (at `;`, `&&`, `||`, `|` and newlines, not inside quotes), and each one is judged alone after removing wrappers (`env VAR=x`, `time`, `command`, `sudo`, `nohup`, `xargs`, `builtin`) and trailing redirections. The writers are `>` and `>>`, `tee`, `sed -i`, `cp`, `mv`, `install`, `curl` (`-o`, `--output`, or `-O` of a code-file URL), `wget` (`-O`, or a code-file URL without `-O`), a script that calls `write_text` or `open(..., "w")` on one, and the PowerShell cmdlets `Set-Content`, `Add-Content`, `Out-File`, `New-Item`, `Copy-Item` and `Move-Item`. A copy or move counts when the destination is a code file, or when it is a directory (or has no extension) and a source is a code file. Copying a code file to a backup name such as `x.py.bak` is not gated.
- `git apply` and `patch`, unless that command itself is a dry run (`--check`, `--stat`, `--summary`, `--dry-run`). The patch content is not read, so any other use counts as a code write.

Subagents share the parent's session id, so the flag is kept per agent. The main agent loading the skill does not unlock its subagents, and each subagent must load it itself.

Both checks are on by default. Turn the gate off with `ENG_STANDARDS_GATE=0` and the closing-block check on `Stop` with `ENG_STANDARDS_REPLY_CHECK=0`. With the gate off, the other hooks keep running but nothing is blocked.

## Requirements

Python 3.10 or newer and bash. On Windows, Claude Code runs hooks through Git Bash, so nothing more is needed there. Without a suitable Python the gate does nothing and the skill still works; at session start Claude is told "engineering-standards gate is inactive: Python 3.10+ not found."

## Configuration

All settings are read once from environment variables, and every feature is on by default.

| Variable | Effect |
|---|---|
| `ENG_STANDARDS_GATE` | The code-write gate on `PreToolUse`, on by default. Set to `0`, `false`, `off` or `no` (any case) to turn it off. Any other value, or unset, leaves it on. |
| `ENG_STANDARDS_EXTRA_EXTENSIONS` | Extra file types the gate treats as code, comma-separated, with or without the dot, for example `yaml,tpl`. Default: none. |
| `ENG_STANDARDS_REPLY_CHECK` | Closing-block check on the `Stop` hook, on by default. Set to `0`, `false`, `off` or `no` (any case) to turn it off. Any other value, or unset, leaves it on. |
| `ENG_STANDARDS_STATE_DIR` | Folder for the flag files (one folder per session, one file per agent). Default: `$CLAUDE_PLUGIN_DATA/state` when installed as a plugin, otherwise `~/.claude/engineering-standards-gate/state`. |

Set them in the `env` block of your Claude Code user settings file:

```json
{
  "env": {
    "ENG_STANDARDS_REPLY_CHECK": "0",
    "ENG_STANDARDS_EXTRA_EXTENSIONS": "yaml,tpl"
  }
}
```

## Companion skills

The workflow names other skills for specific areas. They are not bundled, because each has its own licence and update cycle and we only vouch for the commits we vetted. Claude uses the skills you already have and substitutes an installed skill that covers the same role, or follows the step without one. Run `/engineering-standards:setup` to see what is missing and install it, one item at a time with your approval. The full list, with source URLs and install commands, is in [`skills/engineering-standards/companion-skills.md`](skills/engineering-standards/companion-skills.md).

## Limits

A Bash command that hides the write in a way the patterns do not see (for example a script file that writes code) is not caught. The hook allows the call when its input cannot be read, or when no Python 3.10+ is found, so a bug here never locks every tool.

## Evals

The `evals/` folder holds four small cases for `claude plugin eval`. Each case copies a tiny fixture workspace, gives the agent a task, and scores the result with deterministic checks (regex on the files the agent wrote). The skill-fired check is only an indicator and is not scored.

| Case | What it checks |
|---|---|
| `fix-shared-rounding-bug` | The rounding bug is fixed once in the shared `to_cents`, not patched in its two callers, and a regression test is added. |
| `dockerfile-small-app` | Pinned non-`latest` slim or multi-stage base, non-root `USER`, non-empty `.dockerignore` that lists `.git`. |
| `sqlite-status-rename` | The script has a dry run or a backup, filters on the old value, and reports a row count. |
| `api-key-feature` | The key is not hard-coded, config lives in one module, and raised errors carry context. |

Run one case against the plugin and a no-plugin baseline (the default when the target is a plugin path):

```
claude plugin eval . --case dockerfile-small-app --runs 1 --scaffold --allow-tools Write Edit --trust-plugin --no-publish
```

Notes: `--scaffold` is needed so the fixture is copied in. Shell tools are not granted because this Windows build has no sandbox for them, so the agent cannot run code or Docker and the checks are static (no `hadolint` run). `--runs` defaults to 3.

Pilot, 23 Nov 2026, Claude Code 2.1.295, model claude-opus-5-5, 1 run per case and arm. Only the first two cases were run: a full pass of 4 cases x 2 arms was estimated at about 1M tokens (cache reads included), above the 400k budget for this pass.

| Case | With plugin | Without plugin | Tokens with / without | Cost with / without |
|---|---|---|---|---|
| `fix-shared-rounding-bug` | pass (1.0) | pass (1.0) | 98k / 66k | $0.19 / $0.13 |
| `dockerfile-small-app` | pass (1.0) | pass (1.0) | 81k / 48k | $0.16 / $0.10 |
| `sqlite-status-rename` | not run | not run | | |
| `api-key-feature` | not run | not run | | |

Token counts are input plus cache plus output, read from the run trace (the JSON reports cost, not tokens). Raw results are in `evals/results/`. The first pass of the rounding case scored 0.8 in both arms because one check matched a code comment; the check was tightened and the case rerun.

Sample size: one trial per case and arm. This is not statistically meaningful. It shows the suite runs and the checks are sound, not that the skill helps or does not help. On these two tasks the baseline model already did the right thing, so the cases do not yet separate the two arms; the skill cost about 50% more tokens. Harder cases and more runs are needed.

## Tests

```
cd hooks/gate
python -m unittest discover -s tests -t .
```

## Credits

The reuse-first ladder is adapted from DietrichGebert/ponytail (MIT). The fresh-context plan review is based on the idea in google/elephant-goldfish-model (Apache-2.0). Both were rewritten; no code was copied.

## License

MIT, see `LICENSE`.
