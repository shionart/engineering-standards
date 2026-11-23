---
name: sqlite-status-rename
tags: [script]
runs: 1
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Write, Edit, Glob, Grep, Skill]
---
Write a script at `tools/rename_status.py` that renames the status of all orders in the SQLite database `shop.db` from one value to another, given on the command line (for example from "pending" to "queued"). You cannot run code in this session.
