#!/usr/bin/env python3
"""Export the explicitly listed live configs, without changing the desktop."""
from pathlib import Path
import json
import os
import subprocess

REPO = Path(__file__).resolve().parents[1]
HOME = Path.home()
manifest = json.loads((REPO / 'manifest.json').read_text())
source_root = REPO / 'home'
expected = set()
total = 0
for entry in manifest:
    relative = Path(entry['target'])
    if relative.is_absolute() or '..' in relative.parts:
        raise SystemExit('Invalid target in manifest')
    target = HOME / relative
    if target.is_symlink():
        raise SystemExit('Refusing to export a symbolic link: ' + str(relative))
    base = source_root / entry['source']
    if source_root not in base.resolve().parents:
        raise SystemExit('Invalid source in manifest')
    if not target.is_file():
        print('Missing, omitted:', relative)
        continue
    data = target.read_bytes()
    destination = base
    try:
        content = data.decode()
    except UnicodeDecodeError:
        content = None
    if content is not None:
        if str(HOME) in content:
            content = content.replace('{{', '{{ "{{" }}')
            content = content.replace(str(HOME), '{{ .chezmoi.homeDir }}')
            destination = base.with_name(base.name + '.tmpl')
        data = content.encode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    os.chmod(destination, 0o755 if 'executable_' in destination.name else 0o644)
    expected.add(destination)
    total += len(data)
# Remove only previously generated files, never repository documentation.
for existing in source_root.rglob('*'):
    if existing.is_file() and existing not in expected:
        existing.unlink()
subprocess.run(['python3', str(REPO / 'scripts/check-public.py')], check=True)
print(f'Exported {len(expected)} configuration files, {total / 1048576:.2f} MiB.')
