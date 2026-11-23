---
name: dockerfile-small-app
tags: [docker]
runs: 1
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Write, Edit, Glob, Grep, Skill]
---
Add a Dockerfile for this small Python web app (served with gunicorn on port 8000, module `app:app`). Create the Dockerfile and anything else a good container build needs. You cannot run Docker in this session.
