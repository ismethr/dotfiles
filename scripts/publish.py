#!/usr/bin/env python3
"""Create a public GitHub repository for this reviewed local export."""
from pathlib import Path
import datetime
import json
import re
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]
def run(args, **kw):
    return subprocess.run(args, cwd=REPO, check=True, **kw)
def output(args):
    return subprocess.check_output(args, cwd=REPO, text=True).strip()

name = sys.argv[1] if len(sys.argv) > 1 else 'dotfiles'
if not re.fullmatch(r'[A-Za-z0-9_.-]+', name):
    raise SystemExit('仓库名只能包含字母、数字、点、横线和下划线。')
if subprocess.run(['gh', 'auth', 'status'], cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
    print('请在浏览器中登录你自己的 GitHub 账户。')
    run(['gh', 'auth', 'login', '--hostname', 'github.com', '--git-protocol', 'https', '--web'])
account = json.loads(output(['gh', 'api', 'user']))
login = account['login']
full_name = login + '/' + name
run(['git', 'config', '--local', 'user.name', login])
run(['git', 'config', '--local', 'user.email', str(account['id']) + '+' + login + '@users.noreply.github.com'])
print('发布到公开仓库：' + full_name, flush=True)
run(['python3', str(REPO / 'scripts/check-public.py')])
if output(['git', 'status', '--porcelain']):
    raise SystemExit('仓库有未提交的修改。请先检查、提交后再发布。')
existing = subprocess.run(['gh', 'repo', 'view', full_name, '--json', 'nameWithOwner,isEmpty,isPrivate'], cwd=REPO, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
if existing.returncode == 0:
    info = json.loads(existing.stdout)
    if info['isPrivate'] or not info['isEmpty']:
        raise SystemExit('已有同名仓库且不是空的公开仓库。请运行此脚本并传入新的仓库名，例如 dotfiles-cachyos。')
    expected = 'https://github.com/' + full_name + '.git'
    remotes = output(['git', 'remote']).splitlines()
    if 'origin' in remotes:
        if output(['git', 'remote', 'get-url', 'origin']) != expected:
            raise SystemExit('已有 origin 指向其他仓库，未更改。')
    else:
        run(['git', 'remote', 'add', 'origin', expected])
    run(['gh', 'auth', 'setup-git', '--hostname', 'github.com'])
    run(['git', 'push', '-u', 'origin', 'main'])
else:
    if output(['git', 'remote']):
        raise SystemExit('已有 Git remote，未创建新仓库。请检查 remote 或 GitHub 连接。')
    run(['gh', 'auth', 'setup-git', '--hostname', 'github.com'])
    run(['gh', 'repo', 'create', full_name, '--public', '--source', str(REPO), '--remote', 'origin', '--push', '--description', 'CachyOS / Niri / Noctalia / Morandi / Rime Xiaohe dotfiles'])
head = output(['git', 'rev-parse', 'HEAD'])
remote_head = output(['git', 'ls-remote', 'origin', 'refs/heads/main']).split()[0]
if head != remote_head:
    raise SystemExit('本地和远端提交不一致，请检查 push 输出。')
url = 'https://github.com/' + full_name
(REPO / '.publish-result.json').write_text(json.dumps({'url': url, 'commit': head, 'time': datetime.datetime.now().isoformat()}, indent=2) + '\n')
print('已发布并验证：' + url)
