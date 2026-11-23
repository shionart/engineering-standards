---
type: regex
match: contains
pattern: 'WHERE\s+status\s*='
flags: i
target:
  source: file
  path: tools/rename_status.py
---
