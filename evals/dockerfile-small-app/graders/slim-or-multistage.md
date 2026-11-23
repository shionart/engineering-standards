---
type: regex
match: contains
pattern: 'slim|alpine|^FROM\s+.+\s+AS\s+\w+'
flags: mi
target:
  source: file
  path: Dockerfile
---
