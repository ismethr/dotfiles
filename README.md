# CachyOS Dotfiles

我的 CachyOS 桌面配置，使用 **Niri + Noctalia + Morandi 配色**。从实际使用的配置导出，基于 [LanRhyme/dotfiles](https://github.com/LanRhyme/dotfiles) 适配，加入 **雾凇小鹤双拼、横向七个候选**。

## 配置导航

| 用途 | 软件／配置 |
| --- | --- |
| 窗口、工作区、快捷键 | [Niri](home/dot_config/niri) |
| 左侧状态栏、底部 Dock、动态配色 | [Noctalia](home/dot_config/noctalia) |
| 终端 | [Ghostty](home/dot_config/ghostty)、[Alacritty](home/dot_config/alacritty) |
| 命令行 | [Fish](home/dot_config/fish)、[Starship](home/dot_config/starship.toml) |
| 编辑器 | [Neovim](home/dot_config/nvim)、[Micro](home/dot_config/micro) |
| 输入法 | [Fcitx5](home/dot_config/fcitx5)、[Rime 自定义补丁](home/private_dot_local/private_share/private_fcitx5/rime)、[Omarchy 皮肤脚本](home/private_dot_local/bin/executable_omarchy-fcitx5-theme) |
| Omarchy | [Hyprland 输入设置](home/dot_config/hypr/input.lua)、[主题／字体钩子](home/dot_config/omarchy/hooks) |
| 环形菜单 | [Kando](home/dot_config/kando) |
| 文件和系统监控 | [superfile](home/dot_config/superfile)、[btop](home/dot_config/btop)、[CAVA](home/dot_config/cava)、[Fastfetch](home/dot_config/fastfetch) |
| 应用外观 | GTK、Kvantum Nordic、Qt、OBS、Krita、Fcitx5 竹简深色主题 |

`home/` 是 chezmoi 的配置源目录；`dot_config` 会还原成 `~/.config`，`private_dot_local` 会还原成 `~/.local`。带 `.tmpl` 的文件在部署时替换当前用户的主目录。

## 输入法

- 默认：雾凇小鹤双拼，简体、半角字符，横向七个候选。
- 左 Shift 切换中英文，保留正在输入的原始编码；Caps Lock 保持大写锁定功能。
- 空格选择当前候选，数字键选词，Tab／Shift+Tab 切换候选，`-`／`=` 或 Page Up／Page Down 翻页。
- Ctrl + Space 切换键盘和 Rime（Omarchy 中 Win + Space 是启动器）；F4 打开方案菜单，全拼作为备用。
- 中英文状态按应用记忆，用户词库在本机学习；换壁纸保持候选方向。
- 候选框皮肤由 `omarchy-fcitx5-theme` 按当前 Omarchy 主题配色和字体生成：直角、强调色边框；换主题或字体时通过 `theme-set`／`font-set` 钩子自动更新。

### Omarchy 上的左 Shift

Omarchy 默认键盘选项 `shift:both_capslock_cancel` 会让单独按下的左 Shift 在松开时变成 `Caps_Lock`，Rime 因此不切换中英文。[`input.lua`](home/dot_config/hypr/input.lua) 改为 `shift:rshift_both_capslock_cancel`：左 Shift 恢复正常；大写锁定为先按住左 Shift 再按右 Shift，单独按右 Shift 取消。

Omarchy 用 systemd 用户服务 `omarchy-fcitx5.service` 运行 Fcitx5，重启请用 `systemctl --user restart omarchy-fcitx5`，不要手动运行 `fcitx5 -d`。

## 在新电脑恢复

软件清单见 [packages.txt](packages.txt)。这是 CachyOS/Arch 的配置，部分软件来自 CachyOS 仓库或 AUR，按实际仓库安装。先安装 `chezmoi`、`git`、`python` 和所需桌面／输入法软件。

```bash
# 使用本仓库 GitHub 页面上的地址克隆
git clone <本仓库的克隆地址> ~/dotfiles
```

先检查 [显示器布局](home/dot_config/niri/cfg/display.kdl)，再预览配置变化：

```bash
chezmoi --source="$HOME/dotfiles" diff
```

关闭运行中的 Fcitx5，然后下载固定版本的词库、光标和本地 Neovim 插件。已有资源会备份到 `~/.local/share/dotfiles/backups/`。

```bash
fcitx5-remote -e
python3 ~/dotfiles/scripts/install-assets.py
chezmoi --source="$HOME/dotfiles" apply
fcitx5 -d
```

首次打开 Neovim 时，Lazy 按 `lazy-lock.json` 安装插件。Kando 的模拟按键功能使用 ydotool；需要正常的 input 组权限和 ydotool 用户服务。可按本机情况配置后注销并重新登录。

## 更新 GitHub 中的配置

修改电脑配置后，在普通终端执行：

```bash
python3 ~/dotfiles/scripts/sync.py
git -C ~/dotfiles diff
git -C ~/dotfiles add .
python3 ~/dotfiles/scripts/check-public.py
git -C ~/dotfiles commit -m "Update desktop configuration"
git -C ~/dotfiles push
```

导出脚本只收集 [manifest.json](manifest.json) 中明确列出的文件，读取当前生效的配置。新增配置文件时，需要明确添加其目标路径和 chezmoi 源路径。不会自动上传整个主目录；默认手动更新 GitHub。

## 首次发布

```bash
python3 ~/dotfiles/scripts/publish.py
```

如果 GitHub CLI 尚未登录，脚本会引导浏览器登录；随后在登录账户下创建公开的 `dotfiles` 仓库、推送并核对远端提交。已有同名且非空的仓库不会被覆盖，可传入其他名称：

```bash
python3 ~/dotfiles/scripts/publish.py dotfiles-cachyos
```

## 导出范围

仓库保存应用配置、主题、自定义输入方案和固定版本依赖说明。输入历史、用户词库、编译词库、缓存、密码、令牌及 SSH／云服务凭据目录不在导出清单中。大型上游词库、Bibata 光标和 vim-be-good 通过安装脚本下载。

本仓库保留当前双显示器布局和 AMD 环境适配。换机器时先检查显示器名称、缩放比例和软件依赖。Noctalia 使用 5.x 原生配置，不能直接用于旧版 QML 配置。

上游来源、版本和许可见 [THIRD_PARTY.md](THIRD_PARTY.md)。
