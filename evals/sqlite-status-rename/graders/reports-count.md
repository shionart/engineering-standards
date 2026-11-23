---
type: regex
match: contains
pattern: 'rowcount|changes\(\)|SELECT\s+COUNT'
flags: i
target:
  source: file
  path: tools/rename_status.py
---
