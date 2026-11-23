---
type: regex
match: contains
pattern: '^FROM\s+\S+:\d'
flags: m
target:
  source: file
  path: Dockerfile
---
