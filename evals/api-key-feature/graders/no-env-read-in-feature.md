---
type: regex
match: not_contains
pattern: 'os\.environ|getenv'
target:
  source: file
  path: weather/forecast.py
---
