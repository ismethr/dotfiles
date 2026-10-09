# Omarchy Dotfiles

我在 [Omarchy](https://omarchy.org/)（Arch Linux + Hyprland）上的个人配置。Omarchy 自带的默认配置（终端、状态栏、主题、Neovim 等）由 Omarchy 管理，这里只保存**在它之上的改动**：中文输入法、中文字体和中文界面。

基于 Omarchy 4.0.4、Hyprland 0.56 整理。

## 配置导航

| 用途 | 配置 |
| --- | --- |
| 输入法 | [Fcitx5](home/dot_config/fcitx5)、[Rime 自定义补丁](home/private_dot_local/private_share/private_fcitx5/rime) |
| 输入法皮肤 | [`omarchy-fcitx5-theme`](home/private_dot_local/bin/executable_omarchy-fcitx5-theme)、[主题／字体钩子](home/dot_config/omarchy/hooks) |
| 键盘 | [Hyprland `input.lua`](home/dot_config/hypr/input.lua) |
| 中文字体 | [`60-cjk-sc.conf`](home/dot_config/fontconfig/conf.d/60-cjk-sc.conf) |
| 中文界面 | [`90-locale.conf`](home/dot_config/environment.d/90-locale.conf) |

`home/` 是 chezmoi 的配置源目录；`dot_config` 会还原成 `~/.config`，`private_dot_local` 会还原成 `~/.local`。

## 输入法

- Fcitx5 + Rime + [雾凇拼音](https://github.com/iDvel/rime-ice)；默认小鹤双拼，F4 切换到全拼。
- 简体、半角字符，横向七个候选。
- 左 Shift 切换中英文，保留正在输入的原始编码。
- 空格选择当前候选，数字键选词，Tab／Shift+Tab 切换候选，`-`／`=` 或 Page Up／Page Down 翻页。
- Ctrl + Space 切换键盘和 Rime（Omarchy 中 Super + Space 是启动器）。
- 中英文状态按应用记忆，用户词库在本机学习。
- 候选框皮肤由 `omarchy-fcitx5-theme` 按当前 Omarchy 主题配色和字体生成：直角、强调色边框；`omarchy theme set`／`omarchy font set` 时通过钩子自动更新。

### 左 Shift 与大写锁定

Omarchy 默认把 CapsLock 用作 Compose 键，并用 `shift:both_capslock_cancel` 让双 Shift 开启大写锁定。这个选项会让单独按下的左 Shift 在松开时变成 `Caps_Lock`，Rime 因此不切换中英文。[`input.lua`](home/dot_config/hypr/input.lua) 改为 `shift:rshift_both_capslock_cancel`：

- 左 Shift：普通 Shift，单独按切换中英文；
- 大写锁定：先按住左 Shift 再按右 Shift；单独按右 Shift 取消；
- CapsLock：仍为 Compose 键（Omarchy 的 emoji 等快捷输入）。

### Fcitx5 服务

Omarchy 用 systemd 用户服务 `omarchy-fcitx5.service` 运行 Fcitx5（`Restart=always`）。重启请用 `systemctl --user restart omarchy-fcitx5`，不要手动运行 `fcitx5 -d` 或 `pkill fcitx5`，否则会和服务抢占输入法，导致按键异常。

## 中文字体与界面

- 中文黑体使用思源黑体 CN（`adobe-source-han-sans-cn-fonts`），宋体和等宽使用 Noto CJK SC。避免 fontconfig 回落到 Noto CJK KR／JP 时出现「骨、门、直、复」等字形不规范的问题。
- 网页请求苹方、黑体、思源黑体等字体时映射到思源黑体 CN；请求宋体时映射到 Noto Serif CJK SC；标注为日文、韩文、繁体的内容保留各自字形。
- 微软雅黑由安装脚本下载到 `~/.local/share/fonts/`，网页指定微软雅黑时直接使用；字体文件不进入仓库。
- 英文界面字体和等宽字体保持 Omarchy 的设置（Liberation Sans、`omarchy font set` 选择的 Nerd Font）。
- 图形会话使用 `zh_CN.UTF-8`（`LANGUAGE=zh_CN:en_US`）；`/etc/locale.conf` 保持英文，避免纯文本控制台无法显示汉字。

## 在新电脑恢复

前提：已安装 Omarchy。

```bash
git clone https://github.com/ismethr/dotfiles ~/dotfiles

# 1. 软件包
sudo pacman -S --needed - < <(grep -v '^#' ~/dotfiles/packages.txt)

# 2. 生成中文 locale
sudo sed -i 's/^#\s*zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen
sudo locale-gen

# 3. 预览配置变化
chezmoi --source="$HOME/dotfiles" diff
```

先停止 Fcitx5，再下载固定版本的雾凇词库和微软雅黑、应用配置。已有文件会备份到 `~/.local/share/dotfiles/backups/`。

```bash
systemctl --user stop omarchy-fcitx5
python3 ~/dotfiles/scripts/install-assets.py
chezmoi --source="$HOME/dotfiles" apply
omarchy-fcitx5-theme
systemctl --user start omarchy-fcitx5
hyprctl reload
```

注销并重新登录后，中文界面生效。

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

导出脚本只收集 [manifest.json](manifest.json) 中明确列出的文件，读取当前生效的配置，并删除仓库 `home/` 中不在清单里的文件。新增配置文件时，需要明确添加其目标路径和 chezmoi 源路径。不会自动上传整个主目录；默认手动更新 GitHub。

## 历史

本仓库最初是 CachyOS + Niri + Noctalia 的配置（基于 [LanRhyme/dotfiles](https://github.com/LanRhyme/dotfiles)）。迁移到 Omarchy 后移除了这些内容，需要时可在 Git 历史中找到（提交 `bb97e86` 及之前）。
