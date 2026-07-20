import sys
base = 'D:/MyProjectSpace/01_Workflows/agent-runner-v2/docs/system/00_governance/foundation/runs/01GF-20260719-4e51c88b'
files = ['README.md', 'LAYER_MODEL.md', 'DOCUMENT_AUTHORITY.md', 'BUNDLE_TAXONOMY.md', 'GOVERNANCE_LIFECYCLE.md', 'METADATA_STANDARD.md']
results = []
for f in files:
    path = base + '/' + f
    try:
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        is_ascii = content.isascii()
        results.append(f + ': isascii=' + str(is_ascii))
        if not is_ascii:
            for i, c in enumerate(content):
                if ord(c) > 127:
                    line = content[:i].count('\n') + 1
                    results.append('  Line ' + str(line) + ': U+' + format(ord(c), '04X') + ' ' + repr(c))
                    break
    except Exception as e:
        results.append(f + ': ERROR ' + str(e))
print('\n'.join(results))