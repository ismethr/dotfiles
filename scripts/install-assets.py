#!/usr/bin/env python3
"""Download pinned large dependencies and build Rime, backing up changed files."""
from pathlib import Path
import datetime
import io
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request

REPO = Path(__file__).resolve().parents[1]
HOME = Path.home()
RIME_REF = 'da1fbe602e38f26db846fa10120ee64c2b0324c0'
VIM_REF = '0ae3de14eb8efc6effe7704b5e46495e91931cc5'
BACKUP = HOME / '.local/share/dotfiles/backups' / datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

def extract(url, destination):
    print('Download:', url, flush=True)
    req = urllib.request.Request(url, headers={'User-Agent': 'dotfiles-asset-installer'})
    with urllib.request.urlopen(req, timeout=120) as response:
        data = response.read()
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:*') as archive:
        archive.extractall(destination, filter='data')

def install_tree(source, destination):
    for item in source.rglob('*'):
        if not item.is_file() and not item.is_symlink():
            continue
        target = destination / item.relative_to(source)
        if target.exists() or target.is_symlink():
            saved = BACKUP / target.relative_to(HOME)
            saved.parent.mkdir(parents=True, exist_ok=True)
            if target.is_symlink():
                saved.symlink_to(os.readlink(target))
            else:
                shutil.copy2(target, saved)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            target.unlink()
        if item.is_symlink():
            if target.exists(): target.unlink()
            target.symlink_to(os.readlink(item))
        else:
            shutil.copy2(item, target)

if not shutil.which('rime_deployer'):
    raise SystemExit('请先安装 fcitx5-rime 和 librime。')
with tempfile.TemporaryDirectory(prefix='dotfiles-assets-') as temporary:
    work = Path(temporary)
    extract(f'https://codeload.github.com/iDvel/rime-ice/tar.gz/{RIME_REF}', work / 'ice')
    source = work / 'ice' / ('rime-ice-' + RIME_REF)
    compiled = work / 'rime'
    compiled.mkdir()
    for item in source.iterdir():
        if item.name in {'lua', 'opencc', 'cn_dicts', 'en_dicts'}:
            shutil.copytree(item, compiled / item.name)
        elif item.is_file() and item.suffix in {'.yaml', '.txt', '.lua'} and not item.name.endswith('.custom.yaml'):
            shutil.copy2(item, compiled / item.name)
    entries = json.loads((REPO / 'manifest.json').read_text())
    for entry in entries:
        target = Path(entry['target'])
        if target.parent.as_posix() == '.local/share/fcitx5/rime' and target.name.endswith('.custom.yaml'):
            # Decode the source attributes (e.g. private_) using the target name.
            shutil.copy2(REPO / 'home' / entry['source'], compiled / target.name)
    subprocess.run(['rime_deployer', '--build', str(compiled), '/usr/share/rime-data', str(compiled / 'build')], check=True)
    subprocess.run(['rime_deployer', '--set-active-schema', 'double_pinyin_flypy'], cwd=compiled, check=True)
    # No live user dictionary or input history is replaced.
    install_tree(compiled, HOME / '.local/share/fcitx5/rime')
    extract('https://github.com/ful1e5/Bibata_Cursor/releases/download/v2.0.7/Bibata-Modern-Classic.tar.xz', work / 'cursor')
    themes = list((work / 'cursor').rglob('index.theme'))
    if len(themes) != 1: raise SystemExit('Unexpected Bibata archive layout')
    install_tree(themes[0].parent, HOME / '.local/share/icons/Bibata-Modern-Classic')
    extract(f'https://codeload.github.com/ThePrimeagen/vim-be-good/tar.gz/{VIM_REF}', work / 'vim')
    install_tree(work / 'vim' / ('vim-be-good-' + VIM_REF), HOME / '.local/share/nvim/vim-be-good')
print('Assets installed; existing files backed up to:', BACKUP)
print('重新部署 Rime 或重启 Fcitx5 后使用小鹤双拼。')
