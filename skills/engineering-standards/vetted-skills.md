# Vetted third-party skills

Skills are untrusted input until checked. This file records what was vetted, from where, at which commit, and how to vet the next one.

## Installed and vetted (9 Nov 2026)

Each folder was copied from a shallow clone at the pinned commit. Only the skill folder was copied, never repository hooks or scripts. SkillSpector static scan with `--no-llm`, plus a pattern sweep (prompt-injection phrases, shell download-and-run, exec/eval, base64, credential paths, persistence, zero-width or bidi characters, HTML comments) and a read of the SKILL.md files.

| Skill | Source repo (stars on 9 Nov 2026) | Commit | Scan result |
|---|---|---|---|
| codebase-design | mattpocock/skills (319K) | 4ae2317ddb22b046e26455e4f9c9b3aaaf62212d | 0/100 SAFE |
| improve-codebase-architecture | mattpocock/skills | 4ae2317ddb22b046e26455e4f9c9b3aaaf62212d | 0/100 SAFE |
| python-design-patterns | wshobson/agents (42K) | 9c61ab243def98f72da12abd41cfcf5bcd91af9d | 0/100 SAFE |
| python-anti-patterns | wshobson/agents | 9c61ab243def98f72da12abd41cfcf5bcd91af9d | 0/100 SAFE |
| python-project-structure | wshobson/agents | 9c61ab243def98f72da12abd41cfcf5bcd91af9d | 0/100 SAFE |
| python-type-safety | wshobson/agents | 9c61ab243def98f72da12abd41cfcf5bcd91af9d | 0/100 SAFE |
| python-error-handling | wshobson/agents | 9c61ab243def98f72da12abd41cfcf5bcd91af9d | 6/100 SAFE: one MEDIUM, an example `httpx.post` in the docs, teaching code |
| python-testing-patterns | wshobson/agents | 9c61ab243def98f72da12abd41cfcf5bcd91af9d | 15/100 SAFE: three MEDIUM, example `requests.post` and a file save in docs, teaching code |

Considered and left out: wshobson python-configuration (scan 26/100: its `.env` examples trip the credential rule, harmless but not needed), python-code-style (ruff covers it), mattpocock domain-modeling (DDD, add when a project needs it), addyosmani/agent-skills (overlaps with simplify and code-review, ships shell hooks), wondelai and sickn33 collections (below the star bar or an unvetted mega-collection).

## Other languages

Rust skills were added on 15 Nov 2026 (below). No Go or TypeScript skill is vetted yet. When a project picks one, search with `find-skills`, then vet. Candidates found on 9 Nov 2026 (installs per skills.sh, stars not yet checked): Go `samber/cc-skills-golang` (golang-code-style, golang-design-patterns, golang-error-handling, golang-testing, golang-concurrency, 43K to 46K installs each); TypeScript `cursor/plugins` typescript-best-practices (9.9K).

## How to vet a new skill

1. Pick by popularity and source: prefer 10K or more stars on the repo, an active maintainer, an open license. Stars are not safety.
2. Clone shallow into an empty folder outside the skills directory. Never run anything from it. Run any Python that reads it with `-I`. Note the commit SHA.
3. `skillspector scan <skill folder> --no-llm --format json > report.json` (no `--output` on Windows; redirect stdout to a file outside the target). Do not enable an LLM provider without asking the user.
4. Sweep for the patterns listed above and read every SKILL.md and referenced file. Any hidden instruction, hook, script, network call, credential access or persistence that is not clearly part of the stated purpose is a reject.
5. Copy the skill folder only (no hooks, no scripts you do not need) into `~/.claude/skills/<name>/`.
6. Add a row here with the commit and the result. No auto-update; update by repeating this process at a new commit.

## Added 15 Nov 2026

SkillSpector `--no-llm`, folder copied only, SKILL.md read where flagged.

| Skill | Source repo (stars) | Commit | Scan result |
|---|---|---|---|
| rust-best-practices | apollographql/skills (130, below the 10K bar, user approved) | 9dda1397730370aeb8df4ff8f2015c34c86b5003 | 0/100 SAFE |
| rust-async-patterns | wshobson/agents (42K) | 9c61ab243def98f72da12abd41cfcf5bcd91af9d | 25/100 CAUTION: one HIGH AE1 at SKILL.md:77, false positive (pointer to references/details.md) |
| rust-testing | affaan-m/ecc (303K) | d2ef2680594f9a17526a6e1a2e18b3d242c5d17b | 0/100 SAFE |
| no-ai-slop | petergyang/no-ai-slop (13K) | 000650b156983f5159695b441477f4e63b25dc85 | 0/100 SAFE, SKILL.md read in full; agents/openai.yaml not copied |

Rejected: yetone/kill-ai-slop (1.4K stars) scored 75/100 DO_NOT_INSTALL (4 HIGH, ships scripts/scan.mjs).

## Added 21 Nov 2026

SkillSpector `--no-llm`, SKILL.md and every script read, folder copied only (minus the maintainer-only `scripts/build_catalog.py`).

| Skill | Source repo (stars) | Commit | Scan result |
|---|---|---|---|
| logo-design | kaankiziltug/logo-design-skill (7.5K, MIT, below the 10K bar, user approved by naming it) | e9eaddc07895575253d6663320354a708f53e955 | Score 100/100 DO_NOT_INSTALL, but all findings reviewed by hand and judged false positives. The full scan hit a MemoryError on its 1,432 library SVGs (0% coverage), which produced 49 HIGH "reference failed" findings (AE1); a rescan without the SVGs reached 90% coverage. Remaining HIGH: AR2 x2 (the phrase "never judge a logo" read as an injection phrase) and PE3 (temp dir in `scripts/render_png.py`). MEDIUM: subprocess calls to local renderers (rsvg-convert, inkscape, headless Chrome, qlmanage, taskkill). No network calls, no credentials, no hooks, no API key needed. Scripts write only to the user-chosen output paths. Library SVGs grepped for script, event handlers, external hrefs: none. |

## Adopted as rule text, not installed (22 Nov 2026)

Both repos were cloned and scanned (SkillSpector 100/100 on each; every finding traced was a false positive: maintainer CI and benchmark scripts, test data, template comments). Only the idea was taken, rewritten in our own words in `SKILL.md`; no files were copied.

| Idea | Source repo (stars) | Commit | Where it went |
|---|---|---|---|
| Reuse-first ladder and "never cut" list | DietrichGebert/ponytail (196K, MIT) | 96608e078b2d5ea607c5c3b8b5a54d1c1fba6846 | Step 2 "Reuse first", step 5 bullets. The plugin was not installed: its always-on hooks inject an instruction to edit `~/.claude/settings.json` and read session history. |
| Fresh-context ("goldfish") plan review | google/elephant-goldfish-model (21.9K, Apache-2.0) | 7d1b721e51448518cc9b0336465041230200dd10 | Step 1 "Fresh-eyes review for large work", one pass instead of its five-stage subagent loop. |

## Installed before the vetting rule, not yet scanned (listed 19 Nov 2026)

These were installed in Oct 2026 without a SkillSpector scan. `engineering-standards` marks them with * in its "Skills by area" table. Their guidance may be used, but their scripts must not run until they have been scanned with the process above.

| Skills | Source |
|---|---|
| animate, animate-expo, animation-performance, animation-vocabulary, apple-design, ask-sonner, break-ui, emil-design-eng, find-animation-opportunities, improve-animations, review-animations, mobile-native, pick-ui-library, prototype, write-swift | emilkowalski/skills (via `npx skills`) |
| impeccable | pbakaus/impeccable |
| design-taste-frontend | leonxlnx/taste-skill |
| security-audit | cloudflare/security-audit-skill |
| banner-design, brand, design, design-system, slides, ui-styling | claudekit |
| ui-ux-pro-max | no source recorded |
| superpowers-* (14) | obra/superpowers |
| understand, understand-* (8) | Understand-Anything repo |
| graphify, reverse-engineer-anything, caveman, find-skills | graphify package, unknown, JuliusBrussee/caveman, vercel-labs/skills |
