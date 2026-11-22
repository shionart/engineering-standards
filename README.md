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

- `PreToolUse` (`gate`): blocks Edit, Write, NotebookEdit, MultiEdit and Bash calls that write a code or script file until the calling agent has used the skill.
- `PostToolUse` on the Skill tool (`mark`): records that the calling agent (main or subagent) used the skill.
- `SessionStart` (`reset`): forgets it again, for the main agent and every subagent, on a new session, resume, clear or compaction.
- `SubagentStop` (`agent_stop`): forgets the flag of the subagent that finished.
- `Stop` (`reply`): sends a reply back if it lacks a closing block (Updated, Created, Removed, Not done, and a line naming relevant skills not used).

Subagents share the parent's session id, so the flag is kept per agent. The main agent loading the skill does not unlock its subagents, and each subagent must load it itself.

The closing-block check on `Stop` is on by default. Turn it off with `ENG_STANDARDS_REPLY_CHECK=0`.

## Requirements

Python 3.10 or newer and bash. On Windows, Claude Code runs hooks through Git Bash, so nothing more is needed there. Without a suitable Python the hooks do nothing and the skill still works.

## Configuration

| Variable | Effect |
|---|---|
| `ENG_STANDARDS_STATE_DIR` | Folder for the flag files (one folder per session, one file per agent). Default: `$CLAUDE_PLUGIN_DATA/state` when installed as a plugin, otherwise `~/.claude/engineering-standards-gate/state`. |
| `ENG_STANDARDS_REPLY_CHECK` | Closing-block check on the `Stop` hook, on by default. Set to `0`, `false`, `off` or `no` (any case) to turn it off. Any other value, or unset, leaves it on. |

Set them in the `env` block of your Claude Code user settings file:

```json
{
  "env": {
    "ENG_STANDARDS_REPLY_CHECK": "0"
  }
}
```

## Companion skills

The workflow names other skills for specific areas. They are not bundled, because each has its own licence and update cycle and we only vouch for the commits we vetted. Claude uses the skills you already have and substitutes an installed skill that covers the same role, or follows the step without one. Run `/engineering-standards:setup` to see what is missing and install it, one item at a time with your approval. The full list, with source URLs and install commands, is in [`skills/engineering-standards/companion-skills.md`](skills/engineering-standards/companion-skills.md).

## Limits

A Bash command that hides the write in a way the patterns do not see (for example a script file that writes code) is not caught. The hook allows the call when its input cannot be read, or when no Python 3.10+ is found, so a bug here never locks every tool.

## Tests

```
cd hooks/gate
python -m unittest discover -s tests -t .
```

## Credits

The reuse-first ladder is adapted from DietrichGebert/ponytail (MIT). The fresh-context plan review is based on the idea in google/elephant-goldfish-model (Apache-2.0). Both were rewritten; no code was copied.

## License

MIT, see `LICENSE`.
