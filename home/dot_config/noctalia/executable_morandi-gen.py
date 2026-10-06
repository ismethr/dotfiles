#!/usr/bin/env python3
"""Morandi desktop colors, adapted from LanRhyme/dotfiles

Upstream commit: f3d9176e59f0333c4cb8ea0351708f0bed36952c
Scope: author desktop applications; no process restarts or privileged writes
"""
import argparse
import colorsys
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path.home()
NOCTALIA_COLORS = ROOT / '.config/noctalia/colors.json'
NIRI_COLORS_KDL = ROOT / '.config/niri/cfg/colors.kdl'
ALACRITTY_TOML = ROOT / '.config/alacritty/alacritty.toml'
ALACRITTY_THEME = ROOT / '.config/alacritty/themes/noctalia.toml'

def hex_to_hsl(hex_color):
    r = int(hex_color[1:3], 16) / 255
    g = int(hex_color[3:5], 16) / 255
    b = int(hex_color[5:7], 16) / 255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s * 100, l * 100

def hsl_to_hex(h, s, l):
    h = h % 360
    s = max(0, min(100, s)) / 100
    l = max(0, min(100, l)) / 100
    r, g, b = colorsys.hls_to_rgb(h / 360, l, s)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

def morandi(hex_color, sat_reduction=0.3, light_adjust=0, warm_shift=0, sat_cap=45):
    h, s, l = hex_to_hsl(hex_color)
    s = s * (1 - sat_reduction)
    h = (h + warm_shift) % 360
    l = max(0, min(100, l + light_adjust))
    s = min(s, sat_cap)
    return hsl_to_hex(h, s, l)

def blend(c1, c2, ratio=0.5):
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * ratio)
    g = int(g1 + (g2 - g1) * ratio)
    b = int(b1 + (b2 - b1) * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"

def generate_palette(c):
    p = {}
    primary = c.get("mPrimary", c.get("primary"))
    secondary = c.get("mSecondary", c.get("secondary"))
    tertiary = c.get("mTertiary", c.get("tertiary"))
    error = c.get("mError", c.get("error"))
    surface = c.get("mSurface", c.get("surface"))
    on_surface = c.get("mOnSurface", c.get("on_surface"))
    surface_var = c.get("mSurfaceVariant", c.get("surface_variant"))
    outline = c.get("mOutline", c.get("outline"))

    p["base"] = morandi(surface, 0.5, -2)
    p["mantle"] = morandi(surface, 0.6, -5)
    p["surface0"] = morandi(surface_var, 0.4, 2)
    p["surface1"] = morandi(surface_var, 0.3, 5)
    p["surface2"] = morandi(surface_var, 0.2, 8)
    p["overlay0"] = morandi(outline, 0.3, -2)
    p["overlay1"] = morandi(outline, 0.2, 2)
    p["overlay2"] = morandi(outline, 0.1, 5)
    p["subtext0"] = morandi(on_surface, 0.4, -8)
    p["subtext1"] = morandi(on_surface, 0.3, -4)
    p["text"] = morandi(on_surface, 0.2, 0)
    p["love"] = morandi(error, 0.25, -15)
    p["rose"] = morandi(blend(primary, error, 0.6), 0.3, -15, 5)
    p["gold"] = morandi(blend(primary, "#d4a574", 0.3), 0.35, -10, 15)
    p["peach"] = morandi(blend(error, "#d4a574", 0.4), 0.3, -10, 10)
    p["pine"] = morandi(tertiary, 0.3, -18, -5)
    p["foam"] = morandi(secondary, 0.35, -18, -5)
    p["iris"] = morandi(primary, 0.25, -18)
    p["sky"] = morandi(tertiary, 0.35, -18, -10)

    h, s, l = hex_to_hsl(p["surface1"])
    p["fcitx5_bg"] = hsl_to_hex(h, s * 0.6, min(l, 20))
    p["fcitx5_bg_alt"] = hsl_to_hex(h, s * 0.5, min(l + 3, 22))
    ih, is_, il = hex_to_hsl(p["iris"])
    p["fcitx5_hl_bg"] = hsl_to_hex(ih, is_, min(il, 38))
    p["fcitx5_text"] = p["text"]
    p["fcitx5_hl_text"] = p["base"]
    # Normal terminal colors
    p["term_red"] = morandi(blend(primary, "#ff757f", 0.4), 0.5, -15)
    p["term_green"] = morandi(blend(primary, "#c3e88d", 0.4), 0.5, -15)
    p["term_yellow"] = morandi(blend(primary, "#ffc777", 0.4), 0.5, -15)
    p["term_blue"] = morandi(blend(primary, "#82aaff", 0.4), 0.5, -15)
    p["term_magenta"] = morandi(blend(primary, "#c099ff", 0.4), 0.5, -15)
    p["term_cyan"] = morandi(blend(primary, "#86e1fc", 0.4), 0.5, -15)

    # Bright terminal colors (slightly higher lightness, slightly higher saturation)
    p["term_bright_red"] = morandi(blend(primary, "#ff757f", 0.4), 0.45, -12)
    p["term_bright_green"] = morandi(blend(primary, "#c3e88d", 0.4), 0.45, -12)
    p["term_bright_yellow"] = morandi(blend(primary, "#ffc777", 0.4), 0.45, -12)
    p["term_bright_blue"] = morandi(blend(primary, "#82aaff", 0.4), 0.45, -12)
    p["term_bright_magenta"] = morandi(blend(primary, "#c099ff", 0.4), 0.45, -12)
    p["term_bright_cyan"] = morandi(blend(primary, "#86e1fc", 0.4), 0.45, -12)

    # Dim terminal colors (lower lightness, lower saturation)
    p["term_dim_red"] = morandi(blend(primary, "#ff757f", 0.4), 0.55, -18)
    p["term_dim_green"] = morandi(blend(primary, "#c3e88d", 0.4), 0.55, -18)
    p["term_dim_yellow"] = morandi(blend(primary, "#ffc777", 0.4), 0.55, -18)
    p["term_dim_blue"] = morandi(blend(primary, "#82aaff", 0.4), 0.55, -18)
    p["term_dim_magenta"] = morandi(blend(primary, "#c099ff", 0.4), 0.55, -18)
    p["term_dim_cyan"] = morandi(blend(primary, "#86e1fc", 0.4), 0.55, -18)

    # Terminal background: tinted with primary theme color, slightly lighter than base
    h_p, s_p, _ = hex_to_hsl(primary)
    h_b, s_b, l_b = hex_to_hsl(p["base"])
    p["term_bg"] = hsl_to_hex(h_p, min(s_b + 4, 18), max(l_b + 0, 4))

    return p

def write_niri(palette):
    kdl = f"""// Auto-generated by morandi-gen.py — do not edit manually
layout {{
    focus-ring {{
        width 1
        active-gradient from="{palette['iris']}" to="{palette['pine']}" angle=45 relative-to="workspace-view"
        inactive-gradient from="{palette['surface0']}" to="{palette['surface1']}" angle=45 relative-to="workspace-view"
    }}
    border {{
        off
    }}
    shadow {{
        color "{palette['surface0']}70"
    }}
    tab-indicator {{
        active-color "{palette['iris']}"
        inactive-color "{palette['surface1']}"
        urgent-color "{palette['love']}"
    }}
    insert-hint {{
        color "{palette['iris']}80"
    }}
}}
recent-windows {{
    highlight {{
        active-color "{palette['iris']}"
        urgent-color "{palette['love']}"
    }}
}}
"""
    with open(NIRI_COLORS_KDL, "w") as f:
        f.write(kdl)

def write_alacritty(palette):
    if not ALACRITTY_TOML.exists(): return

    ALACRITTY_THEME.parent.mkdir(parents=True, exist_ok=True)
    theme_content = f"""# Auto-generated Morandi theme by morandi-gen.py
[colors.primary]
background = '{palette["term_bg"]}'
foreground = '{palette["text"]}'

[colors.cursor]
text = '{palette["base"]}'
cursor = '{palette["iris"]}'

[colors.vi_mode_cursor]
text = '{palette["base"]}'
cursor = '{palette["foam"]}'

[colors.search.matches]
foreground = '{palette["base"]}'
background = '{palette["term_yellow"]}'

[colors.search.focused_match]
foreground = '{palette["base"]}'
background = '{palette["term_blue"]}'

[colors.footer_bar]
foreground = '{palette["text"]}'
background = '{palette["mantle"]}'

[colors.hints.start]
foreground = '{palette["base"]}'
background = '{palette["term_yellow"]}'

[colors.hints.end]
foreground = '{palette["base"]}'
background = '{palette["term_magenta"]}'

[colors.selection]
text = '{palette["text"]}'
background = '{palette["surface2"]}'

[colors.normal]
black = '{palette["surface1"]}'
red = '{palette["term_red"]}'
green = '{palette["term_green"]}'
yellow = '{palette["term_yellow"]}'
blue = '{palette["term_blue"]}'
magenta = '{palette["term_magenta"]}'
cyan = '{palette["term_cyan"]}'
white = '{palette["text"]}'

[colors.bright]
black = '{palette["surface2"]}'
red = '{palette["term_bright_red"]}'
green = '{palette["term_bright_green"]}'
yellow = '{palette["term_bright_yellow"]}'
blue = '{palette["term_bright_blue"]}'
magenta = '{palette["term_bright_magenta"]}'
cyan = '{palette["term_bright_cyan"]}'
white = '{palette["text"]}'

[colors.dim]
black = '{palette["surface0"]}'
red = '{palette["term_dim_red"]}'
green = '{palette["term_dim_green"]}'
yellow = '{palette["term_dim_yellow"]}'
blue = '{palette["term_dim_blue"]}'
magenta = '{palette["term_dim_magenta"]}'
cyan = '{palette["term_dim_cyan"]}'
white = '{palette["subtext0"]}'
"""
    ALACRITTY_THEME.write_text(theme_content)

    content = ALACRITTY_TOML.read_text()
    # Clean up redundant inline color blocks in alacritty.toml since themes/noctalia.toml is imported
    cleaned = re.sub(r"\[colors\.(?:primary|normal|bright|cursor|selection)\][\s\S]*?(?=\n\[|\Z)", "", content)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    if cleaned != content:
        ALACRITTY_TOML.write_text(cleaned)


STARSHIP_TOML = ROOT / '.config/starship.toml'
FCITX5_THEME = ROOT / '.local/share/fcitx5/themes/bamboo-dark/theme.conf'
FASTFETCH_CONFIG = ROOT / '.config/fastfetch/config.jsonc'
GHOSTTY_THEME = ROOT / '.config/ghostty/theme'
KDE_OUTPUT = ROOT / '.local/share/color-schemes/Morandi-dark.colors'

def write_starship(palette):
    if not STARSHIP_TOML.exists(): return
    with open(STARSHIP_TOML, "r") as f:
        content = f.read()
    keys = ["base", "mantle", "surface0", "surface1", "surface2", "overlay0", "overlay1", "overlay2", "subtext0", "subtext1", "text", "love", "gold", "peach", "rose", "pine", "foam", "iris", "sky"]
    new_palette = "[palettes.custom]\n" + "\n".join(f"{k} = '{palette[k]}'" for k in keys) + "\n"
    content, count = re.subn(r"\[palettes\.custom\][\s\S]*?(?=\n\[|\Z)", new_palette, content)
    if count == 0: content += "\n" + new_palette
    with open(STARSHIP_TOML, "w") as f:
        f.write(content)

def write_fcitx5(palette):
    theme_dir = FCITX5_THEME.parent
    theme_dir.mkdir(parents=True, exist_ok=True)
    tray_outline, tray_text = palette["surface0"], palette["text"]
    bg, hl = palette['fcitx5_bg'], palette['fcitx5_hl_bg']
    pine = palette.get('pine', '#a8aba0')
    bh, bs, bl = hex_to_hsl(bg)
    border = hsl_to_hex(bh, bs, min(bl + 5, 100))

    panel_svg = f'''<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="40" height="40" rx="8" fill="{bg}" fill-opacity="0.85"/>
<rect x="0.5" y="0.5" width="39" height="39" rx="8" stroke="{border}" stroke-opacity="1.0"/>
</svg>'''

    highlight_svg = f'''<svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M41 1V5.51948H36.5293V10.1667H41V31.8333H36.5293V36.8333H41V41H36.5293V36.8333H32.2V41H9.8V36.8333H5.21655V41H1V36.8333H5.21655V31.8333H1V10.1667H5.21655V5.51948H1V1H5.21655V5.51948H9.8V1H20.2H32.2V5.51948H36.5293V1H41Z" fill="{pine}" fill-opacity="0.2"/>
<path d="M5.21655 5.51948H1V1H5.21655V10.1667H1V31.8333H5.21655V41H1V36.8333H9.8V41H32.2V36.8333H41V41H36.5293V31.8333H41V10.1667H36.5293V1H41V5.51948H32.2V1H20.2H9.8V5.51948H5.21655Z" stroke="{pine}" stroke-width="2"/>
</svg>'''

    with open(theme_dir / "panel.svg", "w") as f: f.write(panel_svg)
    with open(theme_dir / "highlight.svg", "w") as f: f.write(highlight_svg)

    theme = f"""[Metadata]
Name=bamboo-dark
Version=0.0.1
Author=witt & morandi-gen
Description=古典竹简花纹 Morandi 主题

[InputPanel]
NormalColor={palette['fcitx5_text']}
HighlightColor={palette['fcitx5_hl_text']}
HighlightBackgroundColor={pine}
HighlightCandidateColor={pine}
EnableBlur=True
FullWidthHighlight=True
PageButtonAlignment=Bottom

[InputPanel/BlurMargin]
Left=2
Right=2
Top=2
Bottom=2

[InputPanel/Background]
Image=panel.svg
Color={bg}
BorderColor={border}
BorderWidth=0

[InputPanel/Background/Margin]
Left=12
Right=12
Top=12
Bottom=12

[InputPanel/Highlight]
Image=highlight.svg
Color={bg}
BorderColor={border}00
BorderWidth=0
Gravity="Top Left"

[InputPanel/Highlight/Margin]
Left=12
Right=12
Top=1
Bottom=1

[InputPanel/ContentMargin]
Left=10
Right=10
Top=10
Bottom=10

[InputPanel/TextMargin]
Left=10
Right=10
Top=4
Bottom=4

[Menu]
NormalColor={palette['fcitx5_text']}
HighlightCandidateColor={palette['fcitx5_text']}
Spacing=0

[Menu/Background]
Image=panel.svg
Color={bg}
BorderColor={border}
BorderWidth=0

[Menu/Background/Margin]
Left=6
Right=6
Top=6
Bottom=6

[Menu/Highlight]
Image=highlight.svg
Color={bg}
BorderColor={border}00
BorderWidth=0

[Menu/Highlight/Margin]
Left=4
Right=4
Top=2
Bottom=2

[Menu/Separator]
Color={palette['fcitx5_bg_alt']}
BorderColor={palette['fcitx5_bg_alt']}00
BorderWidth=0
"""
    with open(FCITX5_THEME, "w") as f: f.write(theme)
    classicui = ROOT / ".config/fcitx5/conf/classicui.conf"
    if classicui.exists():
        content = classicui.read_text()
        content = re.sub(r"^Theme=.*", "Theme=bamboo-dark", content, flags=re.MULTILINE)
        content = re.sub(r"^DarkTheme=.*", "DarkTheme=bamboo-dark", content, flags=re.MULTILINE)
        content = re.sub(r"^UseDarkTheme=.*", "UseDarkTheme=False", content, flags=re.MULTILINE)
        # Candidate direction is an input preference; preserve it across theme changes.
        content = re.sub(r"^TrayOutlineColor=.*", f"TrayOutlineColor={tray_outline}", content, flags=re.MULTILINE)
        content = re.sub(r"^TrayTextColor=.*", f"TrayTextColor={tray_text}", content, flags=re.MULTILINE)
        classicui.write_text(content)

def write_fastfetch(palette):
    if not FASTFETCH_CONFIG.exists():
        return
    sep = palette['overlay0']
    config = f"""{{
    "$schema": "https://github.com/fastfetch-cli/fastfetch/raw/dev/doc/json_schema.json",
    "logo": {{
        "type": "chafa",
        "source": "{ROOT}/.config/fastfetch/avatar.png",
        "width": 40,
        "height": 19,
        "padding": {{ "top": 2, "right": 2 }}
    }},
    "display": {{
        "separator": "  ",
        "disableLinewrap": true,
        "color": {{
            "keys": "{palette['iris']}",
            "title": "{palette['text']}"
        }}
    }},
    "modules": [
        {{ "type": "title", "color": {{ "user": "{palette['text']}", "at": "{palette['iris']}", "host": "{palette['pine']}" }} }},
        {{ "type": "separator", "string": "─", "times": 40, "outputColor": "{sep}" }},
        {{ "type": "os", "key": "  \uf30e OS" }},
        {{ "type": "kernel", "key": "  \uf331 Kernel" }},
        {{ "type": "uptime", "key": "  \uf017 Uptime" }},
        {{ "type": "packages", "key": "  \uf2dc Packages" }},
        {{ "type": "shell", "key": "  \uf489 Shell" }},
        {{ "type": "terminal", "key": "  \uf120 Terminal" }},
        {{ "type": "terminalfont", "key": "  \U000F0295 Font" }},
        {{ "type": "de", "key": "  \uf35e DE" }},
        {{ "type": "wm", "key": "  \uf2d2 WM" }},
        {{ "type": "separator", "string": "─", "times": 40, "outputColor": "{sep}" }},
        {{ "type": "host", "key": "  \U000F0A58 Host" }},
        {{ "type": "cpu", "key": "  \uf2db CPU" }},
        {{ "type": "gpu", "key": "  \uf26c GPU" }},
        {{ "type": "memory", "key": "  \uf0e4 Memory" }},
        {{ "type": "disk", "key": "  \uf0a0 Disk" }},
        {{ "type": "display", "key": "  \U000F0359 Display" }},
        {{ "type": "separator", "string": "─", "times": 40, "outputColor": "{sep}" }},
        {{ "type": "localip", "key": "  \U000F0A60 Local IP" }},
        {{ "type": "colors", "symbol": "circle", "paddingLeft": 2 }}
    ]
}}
"""
    FASTFETCH_CONFIG.write_text(config)

def write_ghostty(palette):
    GHOSTTY_THEME.parent.mkdir(parents=True, exist_ok=True)
    theme_content = f"""# Auto-generated Morandi theme by morandi-gen.py
palette = 0={palette["surface1"]}
palette = 1={palette["term_red"]}
palette = 2={palette["term_green"]}
palette = 3={palette["term_yellow"]}
palette = 4={palette["term_blue"]}
palette = 5={palette["term_magenta"]}
palette = 6={palette["term_cyan"]}
palette = 7={palette["text"]}
palette = 8={palette["surface2"]}
palette = 9={palette["term_bright_red"]}
palette = 10={palette["term_bright_green"]}
palette = 11={palette["term_bright_yellow"]}
palette = 12={palette["term_bright_blue"]}
palette = 13={palette["term_bright_magenta"]}
palette = 14={palette["term_bright_cyan"]}
palette = 15={palette["text"]}
background = {palette["term_bg"]}
foreground = {palette["text"]}
cursor-color = {palette["iris"]}
cursor-text = {palette["base"]}
selection-background = {palette["surface2"]}
selection-foreground = {palette["text"]}
"""
    GHOSTTY_THEME.write_text(theme_content)

def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def write_kde(colors):
    def rgb_str(c): return f"{c[0]},{c[1]},{c[2]}"
    bg, surface, surface_var = hex_to_rgb(colors["background"]), hex_to_rgb(colors["surface_container"]), hex_to_rgb(colors["surface_variant"])
    primary, primary_cont = hex_to_rgb(colors["primary"]), hex_to_rgb(colors["primary_container"])
    on_surface, on_surface_var, on_primary = hex_to_rgb(colors["on_surface"]), hex_to_rgb(colors["on_surface_variant"]), hex_to_rgb(colors["on_primary"])
    error, window_bg = hex_to_rgb(colors["error"]), hex_to_rgb(colors["surface_container_low"])
    content = f"""[General]\nName=Morandi Dark\nshadeSortColumn=true\n
[Colors:Button]
BackgroundNormal={rgb_str(surface)}\nBackgroundAlternate={rgb_str(surface)}
ForegroundNormal={rgb_str(on_surface)}\nForegroundInactive={rgb_str(on_surface_var)}
ForegroundActive={rgb_str(primary)}\nForegroundLink={rgb_str(primary)}\nForegroundNegative={rgb_str(error)}
DecorationFocus={rgb_str(primary_cont)}\nDecorationHover={rgb_str(primary)}
[Colors:View]
BackgroundNormal={rgb_str(bg)}\nBackgroundAlternate={rgb_str(surface_var)}
ForegroundNormal={rgb_str(on_surface)}\nForegroundInactive={rgb_str(on_surface_var)}
ForegroundActive={rgb_str(primary)}\nForegroundLink={rgb_str(primary)}\nForegroundNegative={rgb_str(error)}
DecorationFocus={rgb_str(primary_cont)}\nDecorationHover={rgb_str(primary)}
[Colors:Window]
BackgroundNormal={rgb_str(window_bg)}\nBackgroundAlternate={rgb_str(window_bg)}
ForegroundNormal={rgb_str(on_surface)}\nForegroundInactive={rgb_str(on_surface_var)}
ForegroundActive={rgb_str(primary)}\nForegroundLink={rgb_str(primary)}\nForegroundNegative={rgb_str(error)}
DecorationFocus={rgb_str(primary_cont)}\nDecorationHover={rgb_str(primary)}
[Colors:Selection]
BackgroundNormal={rgb_str(primary_cont)}\nBackgroundAlternate={rgb_str(primary_cont)}
ForegroundNormal={rgb_str(on_primary)}\nForegroundInactive={rgb_str(on_primary)}\nForegroundActive={rgb_str(on_primary)}
ForegroundLink={rgb_str(on_primary)}\nForegroundNegative={rgb_str(error)}
DecorationFocus={rgb_str(primary_cont)}\nDecorationHover={rgb_str(primary)}
[WM]
activeBackground={rgb_str(surface)}\nactiveForeground={rgb_str(on_surface)}
inactiveBackground={rgb_str(bg)}\ninactiveForeground={rgb_str(on_surface_var)}
activeTitleBtnBg={rgb_str(primary_cont)}\ninactiveTitleBtnBg={rgb_str(surface)}\n"""
    KDE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    KDE_OUTPUT.write_text(content)

def write_obs(palette):
    obs_theme_dir = ROOT / ".config/obs-studio/themes"
    obs_theme_dir.mkdir(parents=True, exist_ok=True)
    
    def rgb_str(hex_c):
        r, g, b = hex_to_rgb(hex_c)
        return f"rgb({r},{g},{b})"
        
    def darken(hex_c, amount=10):
        return morandi(hex_c, 0, -amount, 0, 100)

    obs_iris = darken(palette['iris'], 12)
    obs_foam = darken(palette['foam'], 12)
    obs_sky = darken(palette['sky'], 12)

    content = f"""@OBSThemeMeta {{
    name: 'Morandi';
    id: 'com.obsproject.Yami.Morandi';
    extends: 'com.obsproject.Yami';
    author: 'morandi-gen';
    dark: 'true';
}}

@OBSThemeVars {{
    --primary: {rgb_str(obs_iris)};
    --primary_light: {rgb_str(obs_foam)};
    --primary_lighter: {rgb_str(obs_sky)};
    --primary_dark: {rgb_str(palette['pine'])};
    --primary_darker: {rgb_str(palette['base'])};

    --blue1: {rgb_str(obs_sky)};
    --blue2: {rgb_str(obs_foam)};
    --blue3: {rgb_str(obs_iris)};
    --blue4: {rgb_str(palette['pine'])};
    --blue5: {rgb_str(palette['surface1'])};
    --blue6: {rgb_str(palette['surface0'])};

    --bg_base: {rgb_str(palette['mantle'])};
    --bg_window: {rgb_str(palette['base'])};
    --bg_preview: {rgb_str(palette['mantle'])};

    --border_color: {rgb_str(palette['surface1'])};

    --input_bg: {rgb_str(palette['surface0'])};
    --input_bg_hover: {rgb_str(palette['surface1'])};
    --input_bg_focus: {rgb_str(palette['surface1'])};

    --list_item_bg_selected: {rgb_str(palette['surface0'])};
    --list_item_bg_hover: {rgb_str(palette['surface1'])};

    --input_border: {rgb_str(palette['surface2'])};
    --input_border_hover: {rgb_str(obs_iris)};
    --input_border_focus: {rgb_str(obs_iris)};

    --button_bg: {rgb_str(palette['surface0'])};
    --button_bg_hover: {rgb_str(palette['surface1'])};
    --button_bg_down: {rgb_str(palette['surface2'])};
    --button_bg_disabled: {rgb_str(palette['mantle'])};

    --button_bg_red: {rgb_str(palette['love'])};
    --button_bg_red_hover: {rgb_str(palette['rose'])};
    --button_bg_red_down: {rgb_str(palette['love'])};

    --button_border: {rgb_str(palette['surface2'])};
    --button_border_hover: {rgb_str(obs_iris)};
    --button_border_focus: {rgb_str(obs_iris)};

    --tab_bg: {rgb_str(palette['surface0'])};
    --tab_bg_hover: {rgb_str(palette['surface1'])};
    --tab_bg_down: {rgb_str(palette['surface2'])};
    --tab_bg_disabled: {rgb_str(palette['mantle'])};

    --tab_border: {rgb_str(palette['surface0'])};
    --tab_border_hover: {rgb_str(palette['surface2'])};
    --tab_border_focus: {rgb_str(palette['surface2'])};
    --tab_border_selected: {rgb_str(obs_iris)};

    --scrollbar_handle: {rgb_str(palette['surface1'])};
    --scrollbar_hover: {rgb_str(palette['surface2'])};
    --scrollbar_down: {rgb_str(palette['surface0'])};
    --scrollbar_border: {rgb_str(palette['surface1'])};

    --toolbutton_bg: {rgb_str(palette['surface0'])};
    --toolbutton_bg_hover: {rgb_str(palette['surface1'])};
    --toolbutton_bg_down: {rgb_str(palette['surface2'])};
    --toolbutton_bg_disabled: {rgb_str(palette['mantle'])};
}}
"""
    (obs_theme_dir / "Yami_Morandi.ovt").write_text(content)
    
    obs_config = ROOT / ".config/obs-studio/global.ini"
    if obs_config.exists():
        conf = obs_config.read_text()
        conf = re.sub(r"^CurrentTheme3=.*", "CurrentTheme3=Yami_Morandi", conf, flags=re.MULTILINE)
        obs_config.write_text(conf)

def write_cava(palette):
    cava_dir = ROOT / ".config/cava"
    theme_dir = cava_dir / "themes"
    theme_dir.mkdir(parents=True, exist_ok=True)
    theme_path = theme_dir / "morandi"
    content = f"""; Auto-generated by morandi-gen.py — do not edit manually
[color]
background = 'default'
foreground = '{palette['iris']}'

gradient = 1
gradient_color_1 = '{palette['sky']}'
gradient_color_2 = '{palette['foam']}'
gradient_color_3 = '{palette['pine']}'
gradient_color_4 = '{palette['iris']}'
gradient_color_5 = '{palette['gold']}'
gradient_color_6 = '{palette['peach']}'
gradient_color_7 = '{palette['rose']}'
gradient_color_8 = '{palette['love']}'
"""
    theme_path.write_text(content)

def write_krita(palette):
    """Generate Krita Morandi color scheme (.colors) and theme JSON."""
    krita_colors_dir = ROOT / ".local/share/krita/color-schemes"
    krita_colors_dir.mkdir(parents=True, exist_ok=True)
    scheme_file = krita_colors_dir / "Morandi-System.colors"

    def rgb_str(hex_c):
        h = hex_c.lstrip("#")
        return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}"

    bg = palette["base"]
    bg_alt = palette["surface0"]
    fg = palette["text"]
    fg_inact = palette["subtext0"]
    highlight = palette["iris"]
    negative = palette["love"]
    neutral = palette["gold"]
    positive = palette["pine"]

    bg_rgb = rgb_str(bg)
    bg_alt_rgb = rgb_str(bg_alt)
    fg_rgb = rgb_str(fg)
    fg_inact_rgb = rgb_str(fg_inact)
    hl_rgb = rgb_str(highlight)
    neg_rgb = rgb_str(negative)
    neu_rgb = rgb_str(neutral)
    pos_rgb = rgb_str(positive)

    content = f"""[ColorEffects:Disabled]
Color={bg_rgb}
ColorAmount=0
ColorEffect=0
ContrastAmount=0.65
ContrastEffect=1
IntensityAmount=0.1
IntensityEffect=2

[ColorEffects:Inactive]
ChangeSelectionColor=false
Color={fg_inact_rgb}
ColorAmount=0.025
ColorEffect=2
ContrastAmount=0.1
ContrastEffect=2
Enable=false
IntensityAmount=0
IntensityEffect=0

[Colors:Button]
BackgroundAlternate={bg_alt_rgb}
BackgroundNormal={bg_rgb}
DecorationFocus={hl_rgb}
DecorationHover={hl_rgb}
ForegroundActive={hl_rgb}
ForegroundInactive={fg_inact_rgb}
ForegroundLink={hl_rgb}
ForegroundNegative={neg_rgb}
ForegroundNeutral={neu_rgb}
ForegroundNormal={fg_rgb}
ForegroundPositive={pos_rgb}
ForegroundVisited={hl_rgb}

[Colors:Complementary]
BackgroundAlternate={bg_alt_rgb}
BackgroundNormal={bg_rgb}
DecorationFocus={hl_rgb}
DecorationHover={hl_rgb}
ForegroundActive={hl_rgb}
ForegroundInactive={fg_inact_rgb}
ForegroundLink={hl_rgb}
ForegroundNegative={neg_rgb}
ForegroundNeutral={neu_rgb}
ForegroundNormal={fg_rgb}
ForegroundPositive={pos_rgb}
ForegroundVisited={hl_rgb}

[Colors:Header]
BackgroundAlternate={bg_alt_rgb}
BackgroundNormal={bg_rgb}
DecorationFocus={hl_rgb}
DecorationHover={hl_rgb}
ForegroundActive={hl_rgb}
ForegroundInactive={fg_inact_rgb}
ForegroundLink={hl_rgb}
ForegroundNegative={neg_rgb}
ForegroundNeutral={neu_rgb}
ForegroundNormal={fg_rgb}
ForegroundPositive={pos_rgb}
ForegroundVisited={hl_rgb}

[Colors:Selection]
BackgroundAlternate={hl_rgb}
BackgroundNormal={hl_rgb}
DecorationFocus={hl_rgb}
DecorationHover={hl_rgb}
ForegroundActive={bg_rgb}
ForegroundInactive={bg_rgb}
ForegroundLink={bg_rgb}
ForegroundNegative={neg_rgb}
ForegroundNeutral={neu_rgb}
ForegroundNormal={bg_rgb}
ForegroundPositive={pos_rgb}
ForegroundVisited={bg_rgb}

[Colors:Tooltip]
BackgroundAlternate={bg_alt_rgb}
BackgroundNormal={bg_rgb}
DecorationFocus={hl_rgb}
DecorationHover={hl_rgb}
ForegroundActive={hl_rgb}
ForegroundInactive={fg_inact_rgb}
ForegroundLink={hl_rgb}
ForegroundNegative={neg_rgb}
ForegroundNeutral={neu_rgb}
ForegroundNormal={fg_rgb}
ForegroundPositive={pos_rgb}
ForegroundVisited={hl_rgb}

[Colors:View]
BackgroundAlternate={bg_alt_rgb}
BackgroundNormal={bg_rgb}
DecorationFocus={hl_rgb}
DecorationHover={hl_rgb}
ForegroundActive={hl_rgb}
ForegroundInactive={fg_inact_rgb}
ForegroundLink={hl_rgb}
ForegroundNegative={neg_rgb}
ForegroundNeutral={neu_rgb}
ForegroundNormal={fg_rgb}
ForegroundPositive={pos_rgb}
ForegroundVisited={hl_rgb}

[Colors:Window]
BackgroundAlternate={bg_alt_rgb}
BackgroundNormal={bg_rgb}
DecorationFocus={hl_rgb}
DecorationHover={hl_rgb}
ForegroundActive={hl_rgb}
ForegroundInactive={fg_inact_rgb}
ForegroundLink={hl_rgb}
ForegroundNegative={neg_rgb}
ForegroundNeutral={neu_rgb}
ForegroundNormal={fg_rgb}
ForegroundPositive={pos_rgb}
ForegroundVisited={hl_rgb}

[General]
ColorScheme=Morandi-System
Name=Morandi System
shadeSortColumn=true

[KDE]
contrast=4

[WM]
activeBackground={bg_rgb}
activeBlend={fg_rgb}
activeForeground={fg_rgb}
inactiveBackground={bg_alt_rgb}
inactiveBlend={fg_inact_rgb}
inactiveForeground={fg_inact_rgb}
"""
    scheme_file.write_text(content)

    json_path = ROOT / ".config/krita/morandi_theme.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    theme_data = {
        "highlight": highlight,
        "background": bg,
        "alternate": bg_alt,
        "text": fg,
        "inactive_text": fg_inact,
        "iris": palette.get("iris", "#8c829e"),
        "gold": palette.get("gold", "#bfa980"),
        "rose": palette.get("rose", "#c48c90"),
        "pine": palette.get("pine", "#7b9c90"),
        "foam": palette.get("foam", "#809c95"),
        "peach": palette.get("peach", "#c79685"),
        "sky": palette.get("sky", "#7f9bb0")
    }
    json_path.write_text(json.dumps(theme_data, indent=2))

def write_noctalia(palette):
    # Noctalia v5 custom palettes use the v4 m-prefixed role format
    roles = {
        'mPrimary': 'iris', 'mOnPrimary': 'base',
        'mSecondary': 'foam', 'mOnSecondary': 'base',
        'mTertiary': 'pine', 'mOnTertiary': 'base',
        'mError': 'love', 'mOnError': 'base',
        'mSurface': 'base', 'mOnSurface': 'text',
        'mSurfaceVariant': 'surface0', 'mOnSurfaceVariant': 'subtext0',
        'mOutline': 'overlay0', 'mShadow': 'mantle',
        'mHover': 'surface1', 'mOnHover': 'text',
    }
    dark = {role: palette[key] for role, key in roles.items()}
    terminal = {
        'background': palette['term_bg'], 'foreground': palette['text'],
        'cursor': palette['iris'], 'cursorText': palette['base'],
        'selectionBg': palette['surface2'], 'selectionFg': palette['text'],
    }
    for group, prefix in [('normal', 'term_'), ('bright', 'term_bright_')]:
        terminal[group] = {name: palette[prefix + name] for name in ('red', 'green', 'yellow', 'blue', 'magenta', 'cyan')}
        terminal[group].update(black=palette['surface1' if group == 'normal' else 'surface2'], white=palette['text'])
    dark['terminal'] = terminal
    target = ROOT / '.config/noctalia/palettes/Morandi.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps({'dark': dark}, indent=2) + '\n'
    if not target.exists() or target.read_text() != content:
        fd, temporary = tempfile.mkstemp(dir=target.parent, prefix='.Morandi-')
        try:
            with os.fdopen(fd, 'w') as stream:
                stream.write(content)
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

def main():
    global ROOT, NOCTALIA_COLORS, NIRI_COLORS_KDL, ALACRITTY_TOML, ALACRITTY_THEME, STARSHIP_TOML, FCITX5_THEME, FASTFETCH_CONFIG, GHOSTTY_THEME, KDE_OUTPUT
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path.home())
    parser.add_argument('--colors', type=Path)
    args = parser.parse_args()
    ROOT = args.root.resolve()
    NOCTALIA_COLORS = args.colors or ROOT / '.config/noctalia/colors.json'
    NIRI_COLORS_KDL = ROOT / '.config/niri/cfg/colors.kdl'
    ALACRITTY_TOML = ROOT / '.config/alacritty/alacritty.toml'
    ALACRITTY_THEME = ROOT / '.config/alacritty/themes/noctalia.toml'
    STARSHIP_TOML = ROOT / '.config/starship.toml'
    FCITX5_THEME = ROOT / '.local/share/fcitx5/themes/bamboo-dark/theme.conf'
    FASTFETCH_CONFIG = ROOT / '.config/fastfetch/config.jsonc'
    GHOSTTY_THEME = ROOT / '.config/ghostty/theme'
    KDE_OUTPUT = ROOT / '.local/share/color-schemes/Morandi-dark.colors'
    colors = json.loads(NOCTALIA_COLORS.read_text())
    palette = generate_palette(colors)
    NIRI_COLORS_KDL.parent.mkdir(parents=True, exist_ok=True)
    write_niri(palette)
    write_alacritty(palette)
    write_noctalia(palette)
    write_starship(palette)
    write_fcitx5(palette)
    write_fastfetch(palette)
    write_ghostty(palette)
    write_kde(colors)
    write_cava(palette)
    write_obs(palette)
    write_krita(palette)
    # Niri and Alacritty watch their configs; Noctalia may need an IPC reload
    if ROOT == Path.home():
        try:
            subprocess.run(['noctalia', 'msg', 'config-reload'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, check=False)
        except (OSError, subprocess.TimeoutExpired):
            pass
    print('Morandi: Niri, Alacritty and Noctalia palettes updated')

if __name__ == '__main__':
    main()
