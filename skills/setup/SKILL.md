---
name: setup
description: Check which companion skills of the engineering-standards plugin are installed, which are covered by another installed skill, and which are missing, then offer to install the missing ones one by one.
disable-model-invocation: true
---

# Setup: check companion skills

Run only when the user invokes `/engineering-standards:setup`.

1. Read `companion-skills.md`. Its path relative to this skill is `../engineering-standards/companion-skills.md`; use the base directory shown when this skill was loaded.
2. Compare each default skill in the catalog with the list of available skills in your context. Superpowers skills count as installed under either name, `superpowers-brainstorming` or `superpowers:brainstorming`.
3. Print one table with the columns role, default, status and install command. Status is one of:
   - `installed`
   - `covered by <installed skill>` when another installed skill does the same job
   - `missing`
   - `built in` for skills that ship with Claude Code
   Leave the install command empty for installed and built-in rows.
4. Offer to install the missing ones. Ask the user about each item, or each plugin that covers several rows, and run its command from the catalog only after a yes. Skills marked "not yet" in the Vetted column are unvetted: say so when you ask.
5. After any plugin install, remind the user to restart Claude Code or run `/reload-plugins`.

Rules: never install anything the user did not approve in this run. Never install anything that is not in the catalog.
