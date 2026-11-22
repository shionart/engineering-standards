# Companion skills

The workflow in `SKILL.md` names default skills for each area. This file is the single catalog: where each one comes from, how to install it, and whether it has been vetted.

Skills are not bundled with the plugin. Each has its own licence and update cycle, and we only vouch for the commits recorded in `vetted-skills.md`. Claude does not need every skill on this list. It checks which skills you have and substitutes, as described in "Skills by area" in `SKILL.md`. Run `/engineering-standards:setup` to see what is missing on your machine.

## How to read the Install column

- **Plugin** commands run inside Claude Code. Add the marketplace once, install the plugin, then restart or run `/reload-plugins`. A plugin follows its marketplace, so you get the latest version, not the vetted commit.
- **`npx skills`** is the vercel-labs/skills CLI (https://github.com/vercel-labs/skills). `-g -a claude-code` installs for your user account and Claude Code only. To pin, add a tag or full commit to the source: `npx skills add owner/repo@<commit> --skill <name> -g -a claude-code`. Without a pin you get the latest `main`. The CLI also lists a repo's skills with `npx skills add owner/repo --list`.
- **Manual copy** works for every plain skill repo: clone it, check out the commit, copy the skill folder to `~/.claude/skills/<name>/`, and copy only that folder, never the repo's hooks or scripts.
- **Built in** skills ship with Claude Code, so there is nothing to install.
- The superpowers plugin names its skills `superpowers:brainstorming` and so on. This catalog and `SKILL.md` write them as `superpowers-brainstorming`. Either name counts as installed.

## Plan and architecture

| Role | Default skill | Source | Install | Vetted |
|---|---|---|---|---|
| Clarify an unclear goal | `superpowers-brainstorming` | https://github.com/obra/superpowers | `/plugin install superpowers@claude-plugins-official` (or `/plugin marketplace add obra/superpowers-marketplace` then `/plugin install superpowers@superpowers-marketplace`) | not yet |
| Write a step-by-step plan | `superpowers-writing-plans` | https://github.com/obra/superpowers | same plugin as above | not yet |
| Design deep modules | `codebase-design` | https://github.com/mattpocock/skills | `npx skills add mattpocock/skills --skill codebase-design -g -a claude-code` (or plugin: `/plugin install mattpocock-skills@claude-plugins-official`) | yes, 4ae2317ddb22b046e26455e4f9c9b3aaaf62212d |
| Improve an existing codebase's structure | `improve-codebase-architecture` | https://github.com/mattpocock/skills | `npx skills add mattpocock/skills --skill improve-codebase-architecture -g -a claude-code` | yes, 4ae2317ddb22b046e26455e4f9c9b3aaaf62212d |

## UI/UX design

| Role | Default skill | Source | Install | Vetted |
|---|---|---|---|---|
| Logo before frontend design (rule 11) | `logo-design` | https://github.com/kaankiziltug/logo-design-skill | `/plugin marketplace add kaankiziltug/logo-design-skill` then `/plugin install logo-design@logo-design-skill` | yes, e9eaddc07895575253d6663320354a708f53e955 (plugin installs track latest) |
| Design, critique, audit, polish, UX copy, accessibility | `impeccable` | https://github.com/pbakaus/impeccable | `/plugin marketplace add pbakaus/impeccable`, then install Impeccable from `/plugin` | not yet |
| Style, palette and font data | `ui-ux-pro-max` | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill | `/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill` then `/plugin install ui-ux-pro-max@ui-ux-pro-max-skill` | not yet |
| Public pages: landing, marketing, portfolio | `design-taste-frontend` | https://github.com/Leonxlnx/taste-skill (skill folder `skills/taste-skill`) | `/plugin marketplace add Leonxlnx/taste-skill` then `/plugin install taste-skill@taste-skill`. The skill is named `taste-skill` in the repo; our install calls it `design-taste-frontend`, so a fresh install may show a different name. | not yet |
| Finishing details | `emil-design-eng` | https://github.com/emilkowalski/skills | `npx skills add emilkowalski/skills --skill emil-design-eng -g -a claude-code` | not yet |
| Design tokens | `design-system` | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (folder `.claude/skills/design-system`) | Manual copy of that folder. The repo's plugin installs only `ui-ux-pro-max`. | not yet |
| Gesture and spring-driven UI | `apple-design` | https://github.com/emilkowalski/skills | `npx skills add emilkowalski/skills --skill apple-design -g -a claude-code` | not yet |

## Frontend build

| Role | Default skill | Source | Install | Vetted |
|---|---|---|---|---|
| shadcn/ui and Tailwind | `ui-styling` | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (folder `.claude/skills/ui-styling`; also in https://github.com/mrgoonie/claudekit-skills) | Manual copy of that folder | not yet |
| Choose a component library | `pick-ui-library` | https://github.com/emilkowalski/skills | `npx skills add emilkowalski/skills --skill pick-ui-library -g -a claude-code` | not yet |
| Motion | `animate` | https://github.com/emilkowalski/skills | `npx skills add emilkowalski/skills --skill animate -g -a claude-code` | not yet |
| Motion performance | `animation-performance` | https://github.com/emilkowalski/skills | `npx skills add emilkowalski/skills --skill animation-performance -g -a claude-code` | not yet |
| Web app on a phone | `mobile-native` | https://github.com/emilkowalski/skills | `npx skills add emilkowalski/skills --skill mobile-native -g -a claude-code` | not yet |
| Toasts | `ask-sonner` | https://github.com/emilkowalski/skills | `npx skills add emilkowalski/skills --skill ask-sonner -g -a claude-code` | not yet |
| React Native | `animate-expo` | https://github.com/emilkowalski/skills | `npx skills add emilkowalski/skills --skill animate-expo -g -a claude-code` | not yet |
| Swift | `write-swift` | https://github.com/emilkowalski/skills | `npx skills add emilkowalski/skills --skill write-swift -g -a claude-code` | not yet |

## Python

All six come from the `python-development` plugin of wshobson/agents, and each is also a plain skill folder in that repo.

| Role | Default skill | Source | Install | Vetted |
|---|---|---|---|---|
| Design patterns | `python-design-patterns` | https://github.com/wshobson/agents (`plugins/python-development/skills/python-design-patterns`) | `npx skills add wshobson/agents --skill python-design-patterns -g -a claude-code` (or plugin: `/plugin marketplace add wshobson/agents` then `/plugin install python-development@claude-code-workflows`) | yes, 9c61ab243def98f72da12abd41cfcf5bcd91af9d |
| Project structure | `python-project-structure` | https://github.com/wshobson/agents | `npx skills add wshobson/agents --skill python-project-structure -g -a claude-code` | yes, 9c61ab243def98f72da12abd41cfcf5bcd91af9d |
| Error handling | `python-error-handling` | https://github.com/wshobson/agents | `npx skills add wshobson/agents --skill python-error-handling -g -a claude-code` | yes, 9c61ab243def98f72da12abd41cfcf5bcd91af9d |
| Type safety | `python-type-safety` | https://github.com/wshobson/agents | `npx skills add wshobson/agents --skill python-type-safety -g -a claude-code` | yes, 9c61ab243def98f72da12abd41cfcf5bcd91af9d |
| Testing | `python-testing-patterns` | https://github.com/wshobson/agents | `npx skills add wshobson/agents --skill python-testing-patterns -g -a claude-code` | yes, 9c61ab243def98f72da12abd41cfcf5bcd91af9d |
| Review for anti-patterns | `python-anti-patterns` | https://github.com/wshobson/agents | `npx skills add wshobson/agents --skill python-anti-patterns -g -a claude-code` | yes, 9c61ab243def98f72da12abd41cfcf5bcd91af9d |

## Rust

| Role | Default skill | Source | Install | Vetted |
|---|---|---|---|---|
| Idiomatic Rust | `rust-best-practices` | https://github.com/apollographql/skills | `npx skills add apollographql/skills --skill rust-best-practices -g -a claude-code` (or plugin: `/plugin marketplace add apollographql/skills` then `/plugin install apollo-skills@apollo-marketplace`) | yes, 9dda1397730370aeb8df4ff8f2015c34c86b5003 |
| Async Rust | `rust-async-patterns` | https://github.com/wshobson/agents (`plugins/systems-programming/skills/rust-async-patterns`) | `npx skills add wshobson/agents --skill rust-async-patterns -g -a claude-code` | yes, 9c61ab243def98f72da12abd41cfcf5bcd91af9d |
| Rust tests | `rust-testing` | https://github.com/affaan-m/ECC (`skills/rust-testing`) | `npx skills add affaan-m/ECC --skill rust-testing -g -a claude-code` (the repo's plugin, `/plugin marketplace add https://github.com/affaan-m/ECC` then `/plugin install ecc@ecc`, is a large bundle) | yes, d2ef2680594f9a17526a6e1a2e18b3d242c5d17b |

## Other backend

| Role | Default skill | Source | Install | Vetted |
|---|---|---|---|---|
| HTTP APIs | `postman:api-engineer` | https://github.com/postmanlabs/postman-plugin | `/plugin marketplace add anthropics/claude-plugins-official` then `/plugin install postman@claude-plugins-official` (the official marketplace pins a Postman commit) | not yet |
| LLM features | `claude-api` | built into Claude Code | nothing to install | built in |
| Boomi integrations | `bc-integration:boomi-integration` | https://github.com/OfficialBoomi/boomi-companion (plugin repo https://github.com/OfficialBoomi/bc-integration) | `/plugin marketplace add OfficialBoomi/boomi-companion` then `/plugin install bc-integration@boomi-companion` | not yet |

## Testing

| Role | Default skill | Source | Install | Vetted |
|---|---|---|---|---|
| Test-driven development | `superpowers-test-driven-development` | https://github.com/obra/superpowers | `/plugin install superpowers@claude-plugins-official` | not yet |
| API contract tests | `postman:api-testing` | https://github.com/postmanlabs/postman-plugin | same plugin as `postman:api-engineer` | not yet |
| UI worst-case data | `break-ui` | https://github.com/emilkowalski/skills | `npx skills add emilkowalski/skills --skill break-ui -g -a claude-code` | not yet |
| Run the real app and page | Playwright MCP or `run` | `run` is built in. The Playwright MCP server is https://github.com/microsoft/playwright-mcp | `run`: nothing to install. Playwright MCP: `claude mcp add playwright -- npx @playwright/mcp@latest` (from its README, not re-checked) | built in (`run`) |
| Unclear test failures | `superpowers-systematic-debugging` | https://github.com/obra/superpowers | `/plugin install superpowers@claude-plugins-official` | not yet |

## Review

| Role | Default skill | Source | Install | Vetted |
|---|---|---|---|---|
| Simplify changed code | `simplify` | built into Claude Code | nothing to install | built in |
| Review a diff | `code-review` | built into Claude Code | nothing to install | built in |
| Review pending changes for security | `security-review` | built into Claude Code | nothing to install | built in |
| Audit a whole codebase for security | `security-audit` | https://github.com/cloudflare/security-audit-skill | `npx skills add https://github.com/cloudflare/security-audit-skill --skill security-audit -g -a claude-code` | not yet |
| Review motion | `review-animations` | https://github.com/emilkowalski/skills | `npx skills add emilkowalski/skills --skill review-animations -g -a claude-code` | not yet |

## Done

| Role | Default skill | Source | Install | Vetted |
|---|---|---|---|---|
| Verify before claiming done | `superpowers-verification-before-completion` | https://github.com/obra/superpowers | `/plugin install superpowers@claude-plugins-official` | not yet |

## Related skills outside the table

| Role | Skill | Source | Install | Vetted |
|---|---|---|---|---|
| Plain, human-sounding prose | `humanizer` | https://github.com/blader/humanizer | `/plugin marketplace add blader/humanizer` then `/plugin install humanizer@humanizer` | not yet |
| Remove AI-writing tells | `no-ai-slop` | https://github.com/petergyang/no-ai-slop | `npx skills add petergyang/no-ai-slop --skill no-ai-slop --global --yes` | yes, 000650b156983f5159695b441477f4e63b25dc85 |
