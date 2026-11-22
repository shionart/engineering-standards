---
name: engineering-standards
description: Entry point for ANY task that writes, changes, reviews or designs code or scripts, in any project and any language. Picks the best-fit tech stack for the problem first (fit beats what is already installed), then runs the build workflow (plan, design, test first, implement under SOLID-style rules, simplify, review, verify). Use before the first line of code, also for small scripts, automation, bots, integrations, plugins, refactors, Dockerfiles and frontend/UI design.
---

# Engineering standards

One entry point. Load it before writing or changing code, then follow the steps in order. Skip a step only when it clearly does not apply to the task (a one-line fix does not need a stack decision), and say which step you skipped. The skills named below are defaults, listed with their sources and install commands in `companion-skills.md`; if one is not installed, "Skills by area" says what to do.

Subagents follow this skill too: each one that writes or reviews code loads it itself; a reviewer accepts a subagent's work only when its report shows the skill was loaded and the steps ran.

## 0. Stack first

Choose the tech stack by fit to the problem, not by what is already installed. Installing a toolchain is normal and expected: if Go, Rust, TypeScript, Java or anything else is the best match, it goes first and the toolchain gets installed. Read `stack-selection.md` in this folder for the rubric and the decision record.

- Platform-mandated stacks win over taste (Joget plugins are Java, NetSuite scripts are SuiteScript, Boomi is Boomi). Say so in one line.
- Existing working code is not rewritten only for fit. A new component or a new project is chosen by fit. Rewrite only when the gap is material, and then say what it buys.
- Write the decision down in a short ADR (`docs/adr/NNN-<topic>.md` in the project: problem, options considered, choice, why, when to revisit). Two sentences are enough for a small script.

## 1. Plan

For anything bigger than a quick fix, use `superpowers-writing-plans` (or `superpowers-brainstorming` when the goal itself is unclear). Plan small steps, each one verifiable.

**Fresh-eyes review for large work** (several modules, an integration, a migration, anything hard to undo). Write the plan to a file, then give only that file, with no conversation history, to one subagent on a cheaper model. Its brief: find missing requirements, wrong or unstated assumptions, steps that cannot be verified, risks without a mitigation, and simpler alternatives; report at most 10 findings ranked by impact. Fix or answer every finding in the plan before asking the user for the go. (The "goldfish reviewer" idea from google/elephant-goldfish-model, as one pass rather than its multi-stage loop.)

## 2. Design before code

**Reuse first.** Before designing anything new, stop at the first rung that fully solves the task:

1. Does it need to exist? Drop features, options and flexibility nobody asked for, and name them in one line.
2. Is it already in this codebase (a helper, component, service or pattern)? Use it the way the surrounding code does.
3. Does the standard library or the platform do it? Use that, unless the project has its own.
4. Does an installed dependency do it? Use it. Never add a dependency for a few lines.
5. Otherwise, design the minimum new code under the rules in step 3. A seam needed for a test fake or a second provider is required design, not an unrequested abstraction.

Never cut validation at trust boundaries, error handling that prevents data loss, security or accessibility to make code smaller. (Adapted from DietrichGebert/ponytail, MIT.)

**Then design.** New structure or a messy module: use `codebase-design`, and for existing code suggest the user runs `/improve-codebase-architecture` (it is user-invoked only, so you cannot call it yourself). Add the language skills from the table. If the language has none, look for one with `find-skills` and vet it as described in `vetted-skills.md` before installing. Do not install unvetted skills.

## 3. Rules that always apply (SOLID in practice)

1. **One reason to change per module.** Rules/domain logic, I/O adapters and the entry layer (CLI, bot handlers, HTTP) live apart. A handler parses input, calls a function, formats output. Nothing else.
2. **Pure core, edges for side effects.** Business rules are plain functions of their inputs (no network, files, clock, or global state inside). Drive, mail, browser, LLM, database sit behind small interfaces.
3. **Depend on abstractions, pass them in.** Dependencies come in as parameters or constructor arguments, so a test passes a fake. No hidden singletons or module-level connections that tests must patch.
4. **Extend by adding, not editing.** A new document type, mode or provider is a new small unit registered in one place, not another branch inside a long function.
5. **Small interfaces.** A function or class takes only what it uses.
6. **Explicit types and errors.** Type hints (or the language's equivalent) on public functions, specific exceptions or result types, no bare `except`, no silent failure.
7. **Configuration in one place.** One typed config object read once at start. No scattered `os.environ` or `.env` reads.
8. **No dead code, no duplicate tools, no leftovers.** Remove what a design change made obsolete. A test or helper that is useful twice stays reusable and documented; one-off output is deleted.
9. **Names say what things are.** Short functions, comments only for why, never for what.
10. **Containers are lean.** Any Dockerfile, `.dockerignore` or compose `build:` that is written, changed or reviewed follows `docker-images.md` in this folder and passes its `hadolint` and `dive` checks.
11. **Logo before frontend design.** When frontend design starts (a new UI, page, app, dashboard or rebrand) and the project has no logo yet, run `logo-design` first: brief, concepts, the chosen SVG mark, its 16 px and one-colour tests, and favicon and app-icon variants. Then design the UI around that mark and its colours. "No logo yet" means none in the repo (for example `logo`, `brand`, `favicon` or `icon` files under assets or public) and none supplied by the user; check before deciding. If the user provides a logo or says to skip it, use that logo and do not run the skill. For a client deliverable, present the logo concepts for a choice before building screens on them.

## 4. Test first

Use `superpowers-test-driven-development`, plus the language testing skill from the table. A rule gets a failing test before its code. Fakes for edges, real files only where the format is the point. Run the suite before saying anything is done.

## 5. Implement

- List everything the change must reach first: callers, tests, fixtures, config, exports. Then write the shortest diff that makes the test pass and covers all of them. A one-liner that needs decoding is not short.
- Bug fix: grep every caller of the function you touch, then fix the root cause once in the shared code.
- A shortcut with a known limit gets a comment `shortcut: <the limit>, <when to upgrade>`.
- Clean up with the tests green. Keep commits and edits focused; do not mix a refactor with a behavior change.

## 6. Simplify and review

Run `simplify` over what changed, then `code-review`, plus the language review skills from the table. Fix findings or say why not.

## 7. Verify before claiming done

Use `superpowers-verification-before-completion`: run the tests and the real thing (the bot, the command, the page) and read the output. Report what was tested and what was not.

## Skills by area

Each row names an area and the default skills for it. Before each step, check the list of available skills in your context. Use the default if it is installed; if not, use an installed skill that covers the same role and say which one in one line. If nothing installed covers the role, follow the step without a skill and mention the missing default once, with its install command from `companion-skills.md`. Never install a skill without asking the user. Pick the first skill in a row by default and add the others only for what they cover. Skills marked * have not been vetted yet (see `vetted-skills.md`): use their guidance, but do not run their scripts until they have been scanned.

| Area | Skills |
|---|---|
| Plan and architecture | `superpowers-brainstorming` (goal unclear), `superpowers-writing-plans`, `codebase-design`, `improve-codebase-architecture` |
| UI/UX design | `logo-design` (first when no logo exists, rule 11), `impeccable`* (design, critique, audit, polish, UX copy, accessibility), `ui-ux-pro-max`* (style, palette and font data), `design-taste-frontend`* (public pages: landing, marketing, portfolio), `emil-design-eng`* (finishing details), `design-system`* (tokens), `apple-design`* (gesture and spring-driven UI) |
| Frontend build | `ui-styling`* (shadcn/ui and Tailwind), `pick-ui-library`* (choosing a component library), `animate`* plus `animation-performance`* (motion), `mobile-native`* (web app on a phone), `ask-sonner`* (toasts), `animate-expo`* (React Native), `write-swift`* (Swift) |
| Python | design: `python-design-patterns`, `python-project-structure`; build: `python-error-handling`, `python-type-safety`; test: `python-testing-patterns`; review: `python-anti-patterns`, `python-type-safety` |
| Rust | build: `rust-best-practices`, `rust-async-patterns`; test: `rust-testing` |
| Other backend | HTTP APIs: `postman:api-engineer`. LLM features: `claude-api`. Boomi: `bc-integration:boomi-integration` |
| Testing | `superpowers-test-driven-development` first, then `postman:api-testing` (API contracts), `break-ui`* (UI worst-case data), the Playwright MCP or `run` (real app and page), `superpowers-systematic-debugging` (when a test fails for an unclear reason) |
| Review | `simplify`, `code-review`, `security-review` (pending changes), `security-audit`* (whole codebase), `review-animations`* (motion) |
| Done | `superpowers-verification-before-completion` |

## Where things live

- Stack rubric and ADR template: `stack-selection.md`.
- Dockerfile checklist and image checks: `docker-images.md`.
- Vetted third-party skills, pinned commits, sources and how to vet new ones: `vetted-skills.md`.
- Source, install command and vetting status of every default skill: `companion-skills.md`. To see what is missing on this machine, run `/engineering-standards:setup`.
