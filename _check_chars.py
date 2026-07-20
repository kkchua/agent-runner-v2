import sys
path = 'D:/MyProjectSpace/01_Workflows/agent-runner-v2/docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b/README.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
results = []
for i, c in enumerate(content):
    if ord(c) > 127:
        line = content[:i].count('\n') + 1
        results.append(f'Line {line}: U+{ord(c):04X} ({repr(c)})')
        results.append(f'Context: {repr(content[max(0,i-20):i+20])}')
        break
if not results:
    results.append('No non-ASCII found')
print('\n'.join(results))