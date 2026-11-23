---
name: engineering-standards
description: Entry point for ANY task that writes, changes, reviews or designs code or scripts, in any project and any language. Picks the best-fit tech stack for the problem first (fit beats what is already installed), then runs the build workflow (plan, design, test first, implement under SOLID-style rules, simplify, review, verify). Use before the first line of code, also for small scripts, automation, bots, integrations, plugins, refactors, Dockerfiles and frontend/UI design.
---

# Engineering standards

Follow steps 0-7 in order. Skip a step only when it clearly does not apply (a one-line fix needs no stack decision) and say which. Subagents load this skill themselves; a reviewer accepts their work only with proof that it was loaded and the steps ran.

## 0. Stack first

Pick the stack by fit, not by what is installed; installing a toolchain is normal. See `stack-selection.md`.

- Platform-mandated stacks win (Joget plugins are Java, NetSuite is SuiteScript). Say so in one line.
- Working code is not rewritten only for fit (new components and projects are chosen by fit). Rewrite only when the gap is material; say what it buys.
- Record the choice in a short ADR (`docs/adr/NNN-<topic>.md`: problem, options, choice, why, when to revisit). Two sentences for a small script.

## 1. Plan

Beyond a quick fix use `superpowers-writing-plans` (`superpowers-brainstorming` if the goal is unclear). Plan small, verifiable steps.

For large work (several modules, an integration, a migration, anything hard to undo) get a fresh-eyes review: write the plan to a file and give only that file, with no history, to one cheaper-model subagent. It finds missing requirements, wrong assumptions, unverifiable steps, unmitigated risks and simpler alternatives, at most 10 findings ranked by impact. Fix or answer each before asking the user for the go. (Goldfish reviewer from google/elephant-goldfish-model, one pass.)

## 2. Design before code

Reuse first; stop at the first rung that solves the task:

1. Does it need to exist? Drop unrequested features; name them in one line.
2. Already in this codebase? Use it as the surrounding code does.
3. Standard library or platform? Use that, unless the project has its own.
4. Installed dependency? Use it. Never add one for a few lines.
5. Otherwise write the minimum new code. A seam for a test fake or a second provider is required design, not an unrequested abstraction.

Never cut validation at trust boundaries, data-loss error handling, security or accessibility to shrink code. (Adapted from DietrichGebert/ponytail, MIT.)

Then design: `codebase-design` for new structure or a messy module; suggest the user runs `/improve-codebase-architecture` for existing code (user-invoked only). Add the table's language skills. If a language has none, use `find-skills` and vet per `vetted-skills.md`; never install unvetted skills. For web front ends, record the browser-support target (for example Baseline Widely available) in the project's CLAUDE.md.

## 3. Rules that always apply

1. **One reason to change per module.** Domain logic, I/O adapters and the entry layer (CLI, bot, HTTP) live apart. A handler parses input, calls a function, formats output.
2. **Pure core, side effects at the edges.** Business rules are plain functions of their inputs (no network, files, clock, global state); Drive, mail, browser, LLM and database sit behind small interfaces.
3. **Pass dependencies in**, so a test passes a fake. No hidden singletons or module-level connections to patch.
4. **Extend by adding.** A new type, mode or provider is a small unit registered in one place, not another branch.
5. **Small interfaces.** Take only what you use.
6. **Explicit types and errors.** Type hints on public functions, specific exceptions or result types, no bare `except`, no silent failure.
7. **Configuration in one place.** One typed config object read once at start; no scattered `os.environ` or `.env` reads.
8. **No dead code, duplicate tools or leftovers.** Remove what a design change made obsolete. Helpers useful twice stay reusable and documented; one-off output is deleted.
9. **Names say what things are.** Short functions; comments only for why.
10. **Lean containers.** Any Dockerfile, `.dockerignore` or compose `build:` written, changed or reviewed follows `docker-images.md` and passes `hadolint` and `dive`.
11. **Logo before frontend design.** On new frontend design (UI, page, app, dashboard, rebrand) with no logo yet, run `logo-design` first: brief, concepts, chosen SVG mark, 16 px and one-colour tests, favicon and app-icon variants. Design the UI around that mark and its colours. "No logo yet" means none in the repo (`logo`, `brand`, `favicon`, `icon` files under assets or public) and none from the user; check first. A user-supplied logo, or a request to skip, means use that logo and skip the skill. For a client deliverable, show concepts for a choice before building screens.
12. **Security basics.** No secrets in code, logs or commits; read them from the config object. Validate input at trust boundaries. Run the ecosystem's dependency audit (`pip-audit`, `npm audit`, `cargo audit`) when adding or upgrading dependencies.
13. **Safe data changes.** Migrations and bulk updates are reversible or backed up first, idempotent, and tried as a dry run or on a copy before the real data. Production data changes need the user's explicit go.
14. **Observable failures.** Errors carry enough context to act on (what, which input, which id). Logs are structured and never contain secrets. Long-running jobs report progress and a final summary.

## 4. Test first

Use `superpowers-test-driven-development` plus the language testing skill. A rule gets a failing test before its code. Fakes for edges; real files only where the format is the point. Run the suite before saying done.

## 5. Implement

- List everything the change must reach (callers, tests, fixtures, config, exports), then write the shortest diff that covers all of it. A one-liner that needs decoding is not short.
- Bug fix: grep every caller of the function you touch, then fix the root cause once in shared code.
- A shortcut with a known limit gets a comment `shortcut: <the limit>, <when to upgrade>`.
- Clean up with tests green. Keep edits focused; no refactor mixed with a behavior change.

## 6. Simplify and review

Run `simplify`, then `code-review`, plus the language review skills. Fix findings or say why not.

## 7. Verify before claiming done

Use `superpowers-verification-before-completion`: run the tests and the real thing (bot, command, page), read the output, report what was and was not tested.

## Skills by area

Use the default if installed; else an installed skill with the same role, named in one line; else proceed without and mention its install command from `companion-skills.md` once. Never install without asking. Take a row's first skill; add others only for what they cover. `*` = unvetted: guidance only, run no scripts. Roles and sources: `companion-skills.md`; `/engineering-standards:setup` lists what is missing.

| Area | Skills |
|---|---|
| Plan | `superpowers-writing-plans`, `superpowers-brainstorming` (unclear goal), `codebase-design`, `improve-codebase-architecture` (user-run) |
| UI/UX | `impeccable`*, `logo-design` (no logo yet), `ui-ux-pro-max`*, `design-taste-frontend`*, `emil-design-eng`*, `design-system`*, `apple-design`* |
| Frontend | `ui-styling`*, `pick-ui-library`*, `animate`*, `animation-performance`*, `mobile-native`*, `ask-sonner`*, `animate-expo`*, `write-swift`*, `modern-web-guidance`, `chrome-extensions` |
| Python | design: `python-design-patterns`, `python-project-structure`; build: `python-error-handling`, `python-type-safety`; test: `python-testing-patterns`; review: `python-anti-patterns`, `python-type-safety` |
| Rust | build: `rust-best-practices`, `rust-async-patterns`; test: `rust-testing` |
| Backend | `postman:api-engineer` (HTTP APIs), `claude-api` (LLM), `bc-integration:boomi-integration` (Boomi) |
| Testing | `superpowers-test-driven-development`, `postman:api-testing`, `break-ui`*, Playwright MCP or `run`, `superpowers-systematic-debugging` |
| Review | `simplify`, `code-review`, `security-review`, `security-audit`, `review-animations`* |
| Done | `superpowers-verification-before-completion` |

Also here: `stack-selection.md`, `docker-images.md`, `vetted-skills.md`, `companion-skills.md`.
