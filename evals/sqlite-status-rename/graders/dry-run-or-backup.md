---
type: regex
match: contains
pattern: 'dry[-_ ]?run|backup|\.bak|shutil\.copy|\.backup\('
flags: i
target:
  source: file
  path: tools/rename_status.py
---
