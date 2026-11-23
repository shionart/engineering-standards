---
type: regex
match: contains
pattern: 'environ|getenv|dataclass|BaseSettings'
flags: i
target:
  source: file
  path: weather/config.py
---
