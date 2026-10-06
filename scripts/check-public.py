#!/usr/bin/env python3
"""Check the allowlisted configuration export and Git index for common secrets."""
from pathlib import Path
import json
import re
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]
entries = json.loads((REPO / 'manifest.json').read_text())
allowed = {entry['source'] for entry in entries}
patterns = [
    ('private key', re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')),
    ('GitHub token', re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})')),
    ('API token', re.compile(rb'\bsk-[A-Za-z0-9_-]{20,}')),
    ('AWS access key', re.compile(rb'\bAKIA[0-9A-Z]{16}\b')),
    ('credential assignment', re.compile(rb'''(?im)^\s*["']?(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password|passwd)["']?\s*[:=]\s*["']?[^\s"'#]{12,}''')),
]
problems = []
for path in (REPO / 'home').rglob('*'):
    if not path.is_file():
        continue
    name = path.relative_to(REPO / 'home').as_posix()
    plain = name.removesuffix('.tmpl')
    if plain not in allowed:
        problems.append((name, 'not in export manifest'))
    if path.is_symlink():
        problems.append((name, 'symbolic link'))
    raw = path.read_bytes()
    for label, pattern in patterns:
        if pattern.search(raw):
            problems.append((name, label))
    if re.search(rb'/home/[^/\s"\x27}]+', raw):
        problems.append((name, 'hardcoded home path'))
    if len(raw) > 10 * 1048576:
        problems.append((name, 'file exceeds 10 MiB'))
if (REPO / '.git').is_dir():
    names = subprocess.check_output(['git', '-C', str(REPO), 'ls-files', '-z']).decode().split('\0')
    sensitive = re.compile(r'(^|/)(?:\.ssh|\.aws|\.codex|\.pi|\.cache|build|backups|sync)(/|$)|\.(?:pem|key|userdb|history)$|(^|/)(?:user\.yaml|fish_variables|custom_phrase[^/]*\.txt|\.env(?:\..*)?)$')
    for name in filter(None, names):
        if sensitive.search(name):
            problems.append((name, 'sensitive or generated path in Git index'))
        blob = subprocess.check_output(['git', '-C', str(REPO), 'show', ':' + name])
        for label, pattern in patterns:
            if pattern.search(blob):
                problems.append((name, label + ' in Git index'))
if problems:
    for name, issue in sorted(set(problems)):
        print(f'BLOCKED: {name}: {issue}', file=sys.stderr)
    raise SystemExit(1)
print('Public export checks passed; input history, caches and credential directories are excluded.')
