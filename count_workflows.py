#!/usr/bin/env python
import re

content = open(r'D:\MyProjectSpace\01_Workflows\agent-runner-v2\agent_runner_v2\bootstrap\workflows\default\template_groups.py').read()

# Find TEMPLATE_GROUPS dict definition
match = re.search(r'TEMPLATE_GROUPS.*?=\s*\{', content)
if not match:
    print("Could not find TEMPLATE_GROUPS")
    exit(1)

# Extract from that point to end of file (all workflow defs are in this dict)
from_idx = match.end()
remaining = content[from_idx:]

# Find all top-level keys in TEMPLATE_GROUPS (indented with 4 spaces, quoted, followed by colon and brace)
pattern = r'^    "([^"]+_v\d+)":\s*\{'
matches = re.findall(pattern, remaining, re.MULTILINE)

print(f'Total workflow families found: {len(matches)}')
print('\nWorkflow families:')
for wf in sorted(set(matches)):
    print(f'  - {wf}')
