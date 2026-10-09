#!/usr/bin/env python3
"""Download pinned large dependencies and build Rime, backing up changed files."""
from pathlib import Path
import datetime
import hashlib
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
YAHEI_REF = 'a835171ed5da7d6a85947d9ec349f163c04a96d8'
YAHEI_FILES = {
    'msyh.ttc': '1575bfede7e6ad00d72642c549cb944480cfd3ea51b0dd3fa24734149146f01c',
    'msyhbd.ttc': '97ad29cd8b7ed2ca18e0ef62e499918991d799d78e927222e838730d7672fdcb',
}
BACKUP = HOME / '.local/share/dotfiles/backups' / datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

def download(url):
    print('Download:', url, flush=True)
    req = urllib.request.Request(url, headers={'User-Agent': 'dotfiles-asset-installer'})
    with urllib.request.urlopen(req, timeout=300) as response:
        return response.read()

def extract(url, destination):
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(download(url)), mode='r:*') as archive:
        archive.extractall(destination, filter='data')

def backup(target):
    if target.exists() or target.is_symlink():
        saved = BACKUP / target.relative_to(HOME)
        saved.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            saved.symlink_to(os.readlink(target))
        else:
            shutil.copy2(target, saved)

def install_tree(source, destination):
    for item in source.rglob('*'):
        if not item.is_file() and not item.is_symlink():
            continue
        target = destination / item.relative_to(source)
        backup(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            target.unlink()
        if item.is_symlink():
            if target.exists(): target.unlink()
            target.symlink_to(os.readlink(item))
        else:
            shutil.copy2(item, target)

if not shutil.which('rime_deployer'):
    raise SystemExit('请先安装 packages.txt 中的软件包（fcitx5-rime、librime）。')
with tempfile.TemporaryDirectory(prefix='dotfiles-assets-') as temporary:
    work = Path(temporary)

    # Rime: rime-ice dictionaries plus this repo's patches, prebuilt for Xiaohe.
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

    # Microsoft YaHei: downloaded for local use only, never committed.
    fonts = HOME / '.local/share/fonts'
    fonts.mkdir(parents=True, exist_ok=True)
    for name, digest in YAHEI_FILES.items():
        data = download(f'https://github.com/fernvenue/microsoft-yahei/raw/{YAHEI_REF}/{name}')
        if hashlib.sha256(data).hexdigest() != digest:
            raise SystemExit(f'{name} 校验失败，未安装。')
        backup(fonts / name)
        (fonts / name).write_bytes(data)
    subprocess.run(['fc-cache', '-f', str(fonts)], check=True)
print('Assets installed; existing files backed up to:', BACKUP)
print('重启 Fcitx5 后使用小鹤双拼：systemctl --user restart omarchy-fcitx5')
