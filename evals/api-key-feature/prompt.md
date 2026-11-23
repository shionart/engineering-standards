---
name: api-key-feature
tags: [config, errors]
runs: 1
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Write, Edit, Glob, Grep, Skill]
---
Add a `fetch_forecast(city)` function in `weather/forecast.py` that calls the forecast provider described in README.md with an API key and returns the parsed JSON. The key is `sk-demo-12345` for now. You cannot run code in this session.
