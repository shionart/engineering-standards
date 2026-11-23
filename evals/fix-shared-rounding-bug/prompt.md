---
name: fix-shared-rounding-bug
tags: [bugfix]
runs: 1
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Write, Edit, Glob, Grep, Skill]
---
Customers report that an invoice for an item priced 0.29 shows 28 cents instead of 29, and some cart totals are one cent short. The code is in the `shop` package with tests in `tests/`. Fix the bug. You cannot run code in this session, so reason carefully and leave the repository in a state where `python -m unittest` would pass.
