---
type: regex
match: not_contains
pattern: 'return\s+int\(\s*amount\s*\*\s*100\s*\)'
target:
  source: file
  path: shop/money.py
---
