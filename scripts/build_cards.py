"""Generates the game-engine-editor style SVG panels used in README.md.

Run from the repo root:  python scripts/build_cards.py
Screenshots are read from assets/src/*.jpg and embedded as base64, because
GitHub blocks external images inside SVGs.
"""
import base64
import html
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "src")

SANS = "'Segoe UI','Inter','Helvetica Neue',Arial,sans-serif"
MONO = "'Cascadia Code','Consolas','Courier New',monospace"

# Editor palette
BG = "#1e1e1e"        # window background
PANEL = "#282828"     # panel body
TABBAR = "#1b1b1b"    # tab strip
TAB = "#3a3a3a"       # active tab
FIELD = "#2a2a2a"     # input field
FIELD_BORDER = "#212121"
ROW_ALT = "#2d2d2d"
LINE = "#141414"
TEXT = "#d4d4d4"
LABEL = "#a6a6a6"
DIM = "#7a7a7a"
BLUE = "#4a9eff"
SELECT = "#2c5d87"


def esc(s):
    return html.escape(s, quote=True)


def img64(name):
    with open(os.path.join(SRC, name), "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


def tw(s, size, mono=False):
    """Rough text width estimate."""
    return len(s) * size * (0.6 if mono else 0.56)


def write(path, svg):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"{path}  {len(svg) // 1024} KB")


def open_svg(w, h):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
            f'<rect width="{w}" height="{h}" rx="6" fill="{BG}"/>']


def kebab(x, y):
    return "".join(f'<circle cx="{x}" cy="{y + i * 5}" r="1.3" fill="{DIM}"/>' for i in range(3))


def tabs(x, y, w, labels, active=0, right_text=""):
    """Editor tab strip. labels: list of (icon, text)."""
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="26" fill="{TABBAR}"/>']
    tx = x
    for i, (icon, label) in enumerate(labels):
        width = int(tw(label, 12) + 40)
        if i == active:
            s.append(f'<rect x="{tx}" y="{y}" width="{width}" height="26" fill="{TAB}"/>'
                     f'<rect x="{tx}" y="{y}" width="{width}" height="2" fill="{BLUE}"/>')
        col = TEXT if i == active else DIM
        s.append(f'<text x="{tx + 12}" y="{y + 17}" font-family="{SANS}" font-size="11" fill="{col}">{icon}</text>'
                 f'<text x="{tx + 26}" y="{y + 17}" font-family="{SANS}" font-size="12" fill="{col}">{esc(label)}</text>')
        tx += width
    if right_text:
        s.append(f'<text x="{x + w - 28}" y="{y + 17}" text-anchor="end" font-family="{SANS}" font-size="11" fill="{DIM}">{esc(right_text)}</text>')
    s.append(kebab(x + w - 14, y + 8))
    return "".join(s)


def dropdown(x, y, w, text, h=20):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#3c3c3c" stroke="{FIELD_BORDER}"/>'
            f'<text x="{x + 8}" y="{y + h / 2 + 4}" font-family="{SANS}" font-size="12" fill="{TEXT}">{esc(text)}</text>'
            f'<path d="M{x + w - 14},{y + h / 2 - 2} l4,4 l4,-4" fill="none" stroke="{LABEL}" stroke-width="1.4"/>')


def field(x, y, w, text, h=20, color=TEXT):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{FIELD}" stroke="{FIELD_BORDER}"/>'
            f'<text x="{x + 8}" y="{y + h / 2 + 4}" font-family="{SANS}" font-size="12" fill="{color}">{esc(text)}</text>')


def checkbox(x, y, on=True):
    s = f'<rect x="{x}" y="{y}" width="14" height="14" rx="2" fill="#3c3c3c" stroke="{FIELD_BORDER}"/>'
    if on:
        s += f'<path d="M{x + 3},{y + 7} l3,3 l5,-6" fill="none" stroke="{TEXT}" stroke-width="1.8"/>'
    return s


def chips(items, x, y, max_x):
    out = []
    for t in items:
        w = int(tw(t, 11) + 16)
        if x + w > max_x:
            break
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="18" rx="9" fill="#3a3a3a"/>'
                   f'<text x="{x + w / 2}" y="{y + 13}" text-anchor="middle" font-family="{SANS}" font-size="11" fill="{LABEL}">{esc(t)}</text>')
        x += w + 6
    return "".join(out)


def cube(x, y, s=14, color=BLUE):
    """Small isometric cube icon (GameObject / prefab)."""
    h = s / 2
    return (f'<path d="M{x},{y + h / 2} L{x + h},{y} L{x + s},{y + h / 2} L{x + h},{y + h} Z" fill="{color}" opacity=".95"/>'
            f'<path d="M{x},{y + h / 2} L{x + h},{y + h} L{x + h},{y + s} L{x},{y + s - h / 2} Z" fill="{color}" opacity=".65"/>'
            f'<path d="M{x + s},{y + h / 2} L{x + h},{y + h} L{x + h},{y + s} L{x + s},{y + s - h / 2} Z" fill="{color}" opacity=".45"/>')


def play_button(x, y):
    return (f'<rect x="{x}" y="{y}" width="30" height="22" rx="3" fill="{SELECT}" stroke="{FIELD_BORDER}">'
            f'<animate attributeName="fill" values="{SELECT};#3b78ad;{SELECT}" dur="2s" repeatCount="indefinite"/></rect>'
            f'<path d="M{x + 11},{y + 6} L{x + 20},{y + 11} L{x + 11},{y + 16} Z" fill="#fff"/>')


# ─────────────────────────────── HEADER: toolbar + game view with banner ───────────────────────────────
def header():
    W, H = 900, 412
    s = open_svg(W, H)
    s.append(f'<rect x="0" y="0" width="{W}" height="36" rx="6" fill="#2b2b2b"/><rect x="0" y="30" width="{W}" height="6" fill="#2b2b2b"/>')
    mx = 14
    for m in ["File", "Edit", "Assets", "GameObject", "Window"]:
        s.append(f'<text x="{mx}" y="23" font-family="{SANS}" font-size="12" fill="{TEXT}">{m}</text>')
        mx += tw(m, 12) * 1.1 + 18
    cx = W / 2 - 48
    s.append(play_button(cx, 7))
    s.append(f'<rect x="{cx + 33}" y="7" width="30" height="22" rx="3" fill="#3c3c3c" stroke="{FIELD_BORDER}"/>'
             f'<rect x="{cx + 44}" y="13" width="3" height="10" fill="{TEXT}"/><rect x="{cx + 50}" y="13" width="3" height="10" fill="{TEXT}"/>')
    s.append(f'<rect x="{cx + 66}" y="7" width="30" height="22" rx="3" fill="#3c3c3c" stroke="{FIELD_BORDER}"/>'
             f'<path d="M{cx + 76},13 L{cx + 83},18 L{cx + 76},23 Z" fill="{TEXT}"/><rect x="{cx + 84}" y="13" width="2.5" height="10" fill="{TEXT}"/>')
    s.append(f'<text x="{W - 14}" y="23" text-anchor="end" font-family="{SANS}" font-size="12" fill="{LABEL}">SHK_Profile — Main.scene</text>')
    y0 = 42
    s.append(f'<rect x="6" y="{y0}" width="{W - 12}" height="{H - y0 - 6}" fill="{PANEL}"/>')
    s.append(tabs(6, y0, W - 12, [("#", "Scene"), ("▶", "Game")], active=1))
    ty = y0 + 26
    s.append(f'<rect x="6" y="{ty}" width="{W - 12}" height="26" fill="#323232"/><rect x="6" y="{ty + 26}" width="{W - 12}" height="1" fill="{LINE}"/>')
    s.append(dropdown(12, ty + 3, 92, "Display 1"))
    s.append(dropdown(110, ty + 3, 104, "Free Aspect"))
    s.append(f'<text x="226" y="{ty + 17}" font-family="{SANS}" font-size="12" fill="{LABEL}">Scale</text>'
             f'<rect x="262" y="{ty + 12}" width="80" height="3" rx="1.5" fill="#1a1a1a"/><circle cx="270" cy="{ty + 13.5}" r="5" fill="#9a9a9a"/>'
             f'<text x="352" y="{ty + 17}" font-family="{SANS}" font-size="12" fill="{LABEL}">1x</text>')
    for lab, rx, on in [("Play Maximized", W - 300, False), ("Stats", W - 180, True), ("Gizmos", W - 120, False)]:
        s.append(f'<text x="{rx}" y="{ty + 17}" font-family="{SANS}" font-size="12" fill="{TEXT if on else LABEL}">{lab}</text>')
    by = ty + 30
    bw = W - 20
    bh = round(bw / 3)
    s.append(f'<image href="{img64("banner.jpg")}" x="10" y="{by}" width="{bw}" height="{bh}" preserveAspectRatio="xMidYMid slice"/>')
    s.append(f'<rect x="10" y="{by}" width="{bw}" height="{bh}" fill="none" stroke="{BLUE}" stroke-opacity=".5" stroke-width="2">'
             f'<animate attributeName="stroke-opacity" values=".15;.6;.15" dur="3s" repeatCount="indefinite"/></rect>')
    sx, sy = W - 196, by + 12
    s.append(f'<rect x="{sx}" y="{sy}" width="176" height="74" rx="4" fill="#000" fill-opacity=".55"/>'
             f'<text x="{sx + 10}" y="{sy + 18}" font-family="{SANS}" font-size="11" font-weight="700" fill="#fff">Statistics</text>'
             f'<text x="{sx + 10}" y="{sy + 36}" font-family="{MONO}" font-size="11" fill="#cfcfcf">FPS: <tspan fill="#7CFC9A">60</tspan> (16.6ms)</text>'
             f'<text x="{sx + 10}" y="{sy + 52}" font-family="{MONO}" font-size="11" fill="#cfcfcf">Batches: 42  Tris: 18.2k</text>'
             f'<text x="{sx + 10}" y="{sy + 67}" font-family="{MONO}" font-size="11" fill="#cfcfcf">Bugs: <tspan fill="#7CFC9A">0</tspan> (hopefully)</text>')
    s.append("</svg>")
    write("assets/editor/header.svg", "".join(s))


# ─────────────────────────────── INSPECTOR ───────────────────────────────
def inspector():
    W = 900
    rows = [
        ("Role", "text", "Game Developer · Gameplay Programmer"),
        ("Main Engine", "drop", "Unity"),
        ("Languages", "chips", ["C#", "C++", "TypeScript", "JavaScript"]),
        ("Also Builds In", "chips", ["Unreal Engine", "Godot", "Raylib", "SFML"]),
        ("Background", "text", "Game Design & Animation"),
        ("Publishes On", "chips", ["itch.io", "Playgama", "Web", "Windows", "Android"]),
        ("Home Base", "text", "Bengaluru, India"),
        ("Always Learning", "check", True),
        ("Current Quest", "caret", "Shipping polished web games & Unity editor tools"),
    ]
    y_comp = 132
    H = y_comp + 34 + 30 + len(rows) * 30 + 60
    s = open_svg(W, H)
    s.append(f'<rect x="6" y="6" width="{W - 12}" height="{H - 12}" fill="{PANEL}"/>')
    s.append(tabs(6, 6, W - 12, [("ⓘ", "Inspector"), ("☀", "Lighting")], active=0))
    s.append(f'<clipPath id="av"><rect x="20" y="44" width="58" height="58" rx="4"/></clipPath>'
             f'<image href="{img64("avatar.jpg")}" x="20" y="44" width="58" height="58" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>'
             f'<rect x="20" y="44" width="58" height="58" rx="4" fill="none" stroke="{FIELD_BORDER}" stroke-width="2"/>')
    s.append(checkbox(92, 48))
    s.append(field(114, 45, W - 236, "Shanmukha Srinivasa", 22))
    s.append(checkbox(W - 108, 49) + f'<text x="{W - 88}" y="61" font-family="{SANS}" font-size="12" fill="{TEXT}">Static</text>'
             f'<path d="M{W - 40},56 l4,4 l4,-4" fill="none" stroke="{LABEL}" stroke-width="1.4"/>')
    s.append(f'<text x="92" y="93" font-family="{SANS}" font-size="12" fill="{LABEL}">Tag</text>')
    s.append(dropdown(124, 79, 220, "Developer"))
    s.append(f'<text x="368" y="93" font-family="{SANS}" font-size="12" fill="{LABEL}">Layer</text>')
    s.append(dropdown(410, 79, 220, "Gameplay"))
    s.append(f'<rect x="6" y="{y_comp - 14}" width="{W - 12}" height="1" fill="{LINE}"/>')
    y = y_comp
    s.append(f'<rect x="6" y="{y}" width="{W - 12}" height="26" fill="#323232"/>'
             f'<path d="M16,{y + 10} l5,7 l5,-7 Z" fill="{LABEL}"/>' + checkbox(34, y + 6) +
             f'<rect x="56" y="{y + 6}" width="14" height="14" rx="2" fill="#5a8a3c"/><text x="63" y="{y + 17}" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="700" fill="#fff">#</text>'
             f'<text x="78" y="{y + 18}" font-family="{SANS}" font-size="12" font-weight="700" fill="{TEXT}">Player Profile (Script)</text>')
    s.append(kebab(W - 22, y + 8))
    y += 34
    LX, VX = 36, 230
    s.append(f'<text x="{LX}" y="{y + 14}" font-family="{SANS}" font-size="12" fill="{DIM}">Script</text>')
    s.append(f'<rect x="{VX}" y="{y}" width="{W - VX - 24}" height="20" rx="3" fill="#262626" stroke="{FIELD_BORDER}"/>'
             f'<rect x="{VX + 6}" y="{y + 4}" width="12" height="12" rx="2" fill="#5a8a3c"/>'
             f'<text x="{VX + 26}" y="{y + 14}" font-family="{SANS}" font-size="12" fill="{DIM}">PlayerProfile</text>')
    y += 30
    for i, (label, kind, val) in enumerate(rows):
        d = f'{0.2 + i * 0.12:.2f}s'
        g = [f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".35s" begin="{d}" fill="freeze"/>']
        g.append(f'<text x="{LX}" y="{y + 14}" font-family="{SANS}" font-size="12" fill="{LABEL}">{esc(label)}</text>')
        if kind == "text":
            g.append(field(VX, y, W - VX - 24, val))
        elif kind == "drop":
            g.append(dropdown(VX, y, 220, val))
        elif kind == "chips":
            g.append(chips(val, VX, y + 1, W - 24))
        elif kind == "check":
            g.append(checkbox(VX, y + 3, val))
        elif kind == "caret":
            g.append(f'<rect x="{VX}" y="{y}" width="{W - VX - 24}" height="20" rx="3" fill="{FIELD}" stroke="{BLUE}"/>'
                     f'<text x="{VX + 8}" y="{y + 14}" font-family="{SANS}" font-size="12" fill="{TEXT}">{esc(val)}</text>'
                     f'<rect x="{VX + 10 + tw(val, 12) * 0.98:.0f}" y="{y + 4}" width="1.5" height="12" fill="{TEXT}">'
                     f'<animate attributeName="opacity" values="1;1;0;0" dur="1s" repeatCount="indefinite"/></rect>')
        g.append("</g>")
        s.append("".join(g))
        y += 30
    bx = W / 2 - 110
    s.append(f'<rect x="6" y="{y + 4}" width="{W - 12}" height="1" fill="{LINE}"/>')
    s.append(f'<rect x="{bx}" y="{y + 16}" width="220" height="26" rx="4" fill="#3c3c3c" stroke="{FIELD_BORDER}"/>'
             f'<text x="{W / 2}" y="{y + 33}" text-anchor="middle" font-family="{SANS}" font-size="12" fill="{TEXT}">Add Component</text>')
    s.append("</svg>")
    write("assets/editor/inspector.svg", "".join(s))


# ─────────────────────────────── HIERARCHY (games index) ───────────────────────────────
def hierarchy(games):
    W = 900
    H = 90 + len(games) * 24 + 14
    s = open_svg(W, H)
    s.append(f'<rect x="6" y="6" width="{W - 12}" height="{H - 12}" fill="{PANEL}"/>')
    s.append(tabs(6, 6, W - 12, [("☰", "Hierarchy")], right_text=f"{len(games)} games"))
    s.append(f'<text x="16" y="53" font-family="{SANS}" font-size="17" fill="{TEXT}">+</text>'
             f'<path d="M30,46 l3,3 l3,-3" fill="none" stroke="{LABEL}" stroke-width="1.3"/>')
    s.append(f'<rect x="46" y="38" width="{W - 70}" height="20" rx="10" fill="{FIELD}" stroke="{FIELD_BORDER}"/>'
             f'<circle cx="60" cy="47" r="4.5" fill="none" stroke="{DIM}" stroke-width="1.5"/><path d="M63,50 l4,4" stroke="{DIM}" stroke-width="1.5"/>'
             f'<text x="74" y="52" font-family="{SANS}" font-size="12" fill="{DIM}">Search…</text>')
    y = 64
    s.append(f'<path d="M16,{y + 8} l5,7 l5,-7 Z" fill="{LABEL}"/>'
             f'<path d="M32,{y + 5} h14 v12 h-14 Z" fill="none" stroke="{LABEL}" stroke-width="1.4"/>'
             f'<text x="54" y="{y + 16}" font-family="{SANS}" font-size="12" font-weight="700" fill="{TEXT}">Games.scene</text>')
    y += 24
    n = len(games)
    ys = ";".join(str(y + i * 24) for i in range(n))
    s.append(f'<rect x="6" y="{y}" width="{W - 12}" height="24" fill="{SELECT}">'
             f'<animate attributeName="y" values="{ys}" dur="{n * 1.2}s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    for g in games:
        s.append(f'<path d="M36,{y + 8} l6,4 l-6,4 Z" fill="{DIM}"/>' + cube(48, y + 5, 14, g["color"]))
        s.append(f'<text x="70" y="{y + 16}" font-family="{SANS}" font-size="12.5" fill="{TEXT}">{esc(g["title"])}</text>')
        s.append(f'<text x="360" y="{y + 16}" font-family="{SANS}" font-size="12" fill="{LABEL}">{esc(g["genre"])}</text>')
        s.append(f'<text x="{W - 20}" y="{y + 16}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{DIM}">{esc(g["platform"])}</text>')
        y += 24
    s.append("</svg>")
    write("assets/editor/hierarchy.svg", "".join(s))


# ─────────────────────────────── GAME VIEW CARD ───────────────────────────────
def game_card(g):
    W, H = 440, 372
    s = open_svg(W, H)
    s.append(f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" fill="{PANEL}"/>')
    s.append(tabs(4, 4, W - 8, [("▶", "Game")], right_text=g["title"]))
    ty = 30
    s.append(f'<rect x="4" y="{ty}" width="{W - 8}" height="24" fill="#323232"/>')
    s.append(dropdown(10, ty + 3, 80, "Display 1", 18))
    s.append(dropdown(96, ty + 3, 60, "16:9", 18))
    s.append(f'<text x="168" y="{ty + 16}" font-family="{SANS}" font-size="11" fill="{LABEL}">Scale 1x</text>')
    s.append(play_button(W - 44, ty + 1))
    iy = ty + 28
    ih = round((W - 16) * 9 / 16)
    s.append(f'<image href="{img64(g["slug"] + ".jpg")}" x="8" y="{iy}" width="{W - 16}" height="{ih}" preserveAspectRatio="xMidYMid slice"/>')
    s.append(f'<rect x="8" y="{iy}" width="{W - 16}" height="{ih}" fill="none" stroke="{g["color"]}" stroke-opacity=".6" stroke-width="2">'
             f'<animate attributeName="stroke-opacity" values=".15;.7;.15" dur="3s" repeatCount="indefinite"/></rect>')
    y = iy + ih + 8
    s.append(cube(14, y + 4, 16, g["color"]))
    s.append(f'<text x="38" y="{y + 17}" font-family="{SANS}" font-size="17" font-weight="700" fill="#fff">{esc(g["title"])}</text>')
    s.append(f'<text x="{W - 14}" y="{y + 17}" text-anchor="end" font-family="{SANS}" font-size="11.5" fill="{g["color"]}">{esc(g["genre"])}</text>')
    s.append(f'<text x="14" y="{y + 38}" font-family="{SANS}" font-size="12" fill="{LABEL}">{esc(g["tagline"])}</text>')
    s.append(chips(g["tech"], 14, y + 48, W - 14))
    s.append("</svg>")
    write(f"assets/games/{g['slug']}.svg", "".join(s))


# ─────────────────────────────── PACKAGE MANAGER (tools) ───────────────────────────────
def package_row(t, i):
    W, H = 900, 128
    s = open_svg(W, H)
    s.append(f'<rect x="6" y="6" width="{W - 12}" height="{H - 12}" fill="{PANEL}"/>')
    s.append(f'<clipPath id="pc"><rect x="18" y="12" width="184" height="104" rx="4"/></clipPath>'
             f'<image href="{img64(t["slug"] + ".jpg")}" x="18" y="12" width="184" height="104" clip-path="url(#pc)" preserveAspectRatio="xMidYMid slice"/>'
             f'<rect x="18" y="12" width="184" height="104" rx="4" fill="none" stroke="{FIELD_BORDER}" stroke-width="2"/>')
    s.append(f'<text x="222" y="34" font-family="{SANS}" font-size="17" font-weight="700" fill="#fff">{esc(t["title"])}</text>')
    s.append(f'<text x="222" y="54" font-family="{SANS}" font-size="12" fill="{DIM}">by Shanmukha · {esc(t["kind"])}</text>')
    s.append(f'<text x="222" y="76" font-family="{SANS}" font-size="13" fill="{TEXT}">{esc(t["desc"])}</text>')
    s.append(chips(t["tech"], 222, 90, W - 170))
    bw = int(tw(t["button"], 12) + 30)
    bx = W - 24 - bw
    s.append(f'<rect x="{bx}" y="20" width="{bw}" height="26" rx="4" fill="{SELECT}" stroke="{FIELD_BORDER}"/>'
             f'<text x="{bx + bw / 2}" y="37" text-anchor="middle" font-family="{SANS}" font-size="12" font-weight="600" fill="#fff">{esc(t["button"])}</text>')
    s.append(f'<circle cx="{W - 30}" cy="102" r="5" fill="#5cb85c"><animate attributeName="opacity" values="1;.35;1" dur="2s" begin="{i * .4:.1f}s" repeatCount="indefinite"/></circle>'
             f'<text x="{W - 42}" y="106" text-anchor="end" font-family="{SANS}" font-size="11.5" fill="{LABEL}">{esc(t["status"])}</text>')
    s.append("</svg>")
    write(f"assets/editor/package-{t['slug']}.svg", "".join(s))


def packages_header():
    W, H = 900, 62
    s = open_svg(W, H)
    s.append(f'<rect x="6" y="6" width="{W - 12}" height="{H - 6}" fill="{PANEL}"/>')
    s.append(tabs(6, 6, W - 12, [("▣", "Package Manager")]))
    s.append(f'<rect x="6" y="32" width="{W - 12}" height="28" fill="#323232"/>')
    s.append(dropdown(12, 36, 150, "Packages: My Tools"))
    s.append(dropdown(170, 36, 100, "Sort: Name"))
    s.append(f'<rect x="{W - 240}" y="36" width="220" height="20" rx="10" fill="{FIELD}" stroke="{FIELD_BORDER}"/>'
             f'<text x="{W - 226}" y="50" font-family="{SANS}" font-size="12" fill="{DIM}">Search…</text>')
    s.append("</svg>")
    write("assets/editor/packages-header.svg", "".join(s))


# ─────────────────────────────── CONSOLE (skills) ───────────────────────────────
def console():
    logs = [
        ("i", "Gameplay systems ready: combat, upgrades, waves, quests, economy"),
        ("i", "Game feel tuned: screen shake, hit-stop, juicy feedback"),
        ("i", "Enemy AI online: state machines, auto-targeting, boss phases"),
        ("i", "Procedural generation seeded: endless levels, word grids"),
        ("i", "Object pooling enabled. GC spikes: 0"),
        ("i", "Shaders compiled: HLSL, Shader Graph"),
        ("i", "Multiplayer: Photon PUN 2 room joined (2/2 players)"),
        ("i", "WebGL builds published to itch.io and Playgama"),
        ("i", "Art pipeline: Blender and Maya assets imported"),
        ("i", "Editor tools loaded: Smart AutoSave"),
        ("w", "Coffee level low. Shipping anyway."),
    ]
    W = 900
    H = 64 + len(logs) * 24 + 36
    s = open_svg(W, H)
    s.append(f'<rect x="6" y="6" width="{W - 12}" height="{H - 12}" fill="{PANEL}"/>')
    s.append(tabs(6, 6, W - 12, [("▤", "Console"), ("▦", "Project")], active=0))
    s.append(f'<rect x="6" y="32" width="{W - 12}" height="26" fill="#323232"/>')
    bx = 12
    for b in ["Clear", "Collapse", "Error Pause"]:
        w = int(tw(b, 12) + 18)
        s.append(f'<rect x="{bx}" y="36" width="{w}" height="18" rx="3" fill="#3c3c3c" stroke="{FIELD_BORDER}"/>'
                 f'<text x="{bx + w / 2}" y="49" text-anchor="middle" font-family="{SANS}" font-size="11.5" fill="{TEXT}">{b}</text>')
        bx += w + 6
    infos = sum(1 for k, _ in logs if k == "i")
    warns = len(logs) - infos
    cx = W - 150
    s.append(f'<circle cx="{cx}" cy="45" r="7" fill="none" stroke="#cfcfcf" stroke-width="1.5"/><text x="{cx}" y="49" text-anchor="middle" font-family="{SANS}" font-size="10" font-weight="700" fill="#cfcfcf">i</text>'
             f'<text x="{cx + 12}" y="49" font-family="{SANS}" font-size="12" fill="{TEXT}">{infos}</text>'
             f'<path d="M{cx + 44},51 l7,-13 l7,13 Z" fill="#e8b339"/><text x="{cx + 51}" y="50" text-anchor="middle" font-family="{SANS}" font-size="9" font-weight="700" fill="#222">!</text>'
             f'<text x="{cx + 64}" y="49" font-family="{SANS}" font-size="12" fill="{TEXT}">{warns}</text>'
             f'<circle cx="{cx + 96}" cy="45" r="7" fill="#d9534f"/><text x="{cx + 96}" y="49" text-anchor="middle" font-family="{SANS}" font-size="10" font-weight="700" fill="#fff">×</text>'
             f'<text x="{cx + 108}" y="49" font-family="{SANS}" font-size="12" fill="{TEXT}">0</text>')
    y = 60
    for i, (kind, msg) in enumerate(logs):
        d = f"{0.25 + i * 0.22:.2f}s"
        g = [f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".2s" begin="{d}" fill="freeze"/>']
        if i % 2:
            g.append(f'<rect x="6" y="{y}" width="{W - 12}" height="24" fill="{ROW_ALT}"/>')
        if kind == "i":
            g.append(f'<circle cx="24" cy="{y + 12}" r="7" fill="none" stroke="#cfcfcf" stroke-width="1.5"/>'
                     f'<text x="24" y="{y + 16}" text-anchor="middle" font-family="{SANS}" font-size="10" font-weight="700" fill="#cfcfcf">i</text>')
            col = TEXT
        else:
            g.append(f'<path d="M17,{y + 18} l7,-13 l7,13 Z" fill="#e8b339"/>'
                     f'<text x="24" y="{y + 17}" text-anchor="middle" font-family="{SANS}" font-size="9" font-weight="700" fill="#222">!</text>')
            col = "#e8b339"
        g.append(f'<text x="40" y="{y + 16}" font-family="{MONO}" font-size="12" fill="{DIM}">[09:{i * 3:02d}:{(i * 17) % 60:02d}]</text>'
                 f'<text x="118" y="{y + 16}" font-family="{MONO}" font-size="12" fill="{col}">{esc(msg)}</text>')
        g.append("</g>")
        s.append("".join(g))
        y += 24
    s.append(f'<rect x="6" y="{y + 2}" width="{W - 12}" height="1" fill="{LINE}"/>'
             f'<text x="16" y="{y + 22}" font-family="{MONO}" font-size="12" fill="{BLUE}">&gt;</text>'
             f'<rect x="30" y="{y + 11}" width="8" height="14" fill="{TEXT}"><animate attributeName="opacity" values="1;1;0;0" dur="1s" repeatCount="indefinite"/></rect>')
    s.append("</svg>")
    write("assets/editor/console.svg", "".join(s))


# ─────────────────────────────── PREFAB CARDS (prototypes) ───────────────────────────────
def prefab(p):
    W, H = 440, 150
    s = open_svg(W, H)
    s.append(f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" fill="{PANEL}"/>')
    s.append(tabs(4, 4, W - 8, [("▦", "Project")], right_text=f"Prototypes/{p['file']}"))
    s.append(f'<rect x="18" y="44" width="80" height="80" rx="6" fill="#323232"/>' + cube(34, 58, 48, p["color"]))
    s.append(f'<text x="114" y="64" font-family="{SANS}" font-size="16" font-weight="700" fill="#fff">{esc(p["title"])}</text>')
    s.append(f'<text x="114" y="86" font-family="{SANS}" font-size="12" fill="{LABEL}">{esc(p["desc"])}</text>')
    s.append(chips(p["tech"], 114, 102, W - 14))
    s.append("</svg>")
    write(f"assets/editor/{p['slug']}.svg", "".join(s))


# ─────────────────────────────── SECTION HEADER + STATUS BAR ───────────────────────────────
def section(slug, icon, label, path):
    W, H = 900, 30
    w = int(tw(label, 12.5) + 44)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'<rect width="{W}" height="{H}" rx="5" fill="{TABBAR}"/>',
         f'<rect x="0" y="0" width="{w}" height="{H}" rx="5" fill="{TAB}"/><rect x="0" y="0" width="{w}" height="2" fill="{BLUE}"/>',
         f'<text x="12" y="20" font-family="{SANS}" font-size="12" fill="{TEXT}">{icon}</text>',
         f'<text x="28" y="20" font-family="{SANS}" font-size="12.5" font-weight="600" fill="{TEXT}">{esc(label)}</text>',
         f'<text x="{w + 14}" y="20" font-family="{MONO}" font-size="11.5" fill="{DIM}">{esc(path)}</text>',
         "</svg>"]
    write(f"assets/editor/section-{slug}.svg", "".join(s))


def status_bar():
    W, H = 900, 30
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'<rect width="{W}" height="{H}" rx="5" fill="#2b2b2b"/>',
         f'<circle cx="16" cy="15" r="6" fill="#5cb85c"/><path d="M13,15 l2,2 l4,-4" fill="none" stroke="#fff" stroke-width="1.6"/>',
         f'<text x="30" y="19.5" font-family="{SANS}" font-size="12" fill="{TEXT}">Build succeeded · Thanks for visiting · Always learning, always building</text>',
         f'<rect x="{W - 190}" y="11" width="120" height="8" rx="4" fill="#1a1a1a"/>',
         f'<rect x="{W - 190}" y="11" width="0" height="8" rx="4" fill="{BLUE}"><animate attributeName="width" values="0;120;120" keyTimes="0;.8;1" dur="4s" repeatCount="indefinite"/></rect>',
         f'<text x="{W - 14}" y="19.5" text-anchor="end" font-family="{SANS}" font-size="11" fill="{LABEL}">Ready</text>',
         "</svg>"]
    write("assets/editor/status-bar.svg", "".join(s))


GAMES = [
    dict(slug="haunted-hotel", title="Haunted Hotel Empire", genre="3D Idle Tycoon", tagline="Check in. Never check out.", tech=["Unity", "C#", "Idle Economy", "WebGL"], platform="WEB · PLAYGAMA", color="#a78bfa"),
    dict(slug="last-bunker", title="Last Bunker", genre="Idle Zombie Defense", tagline="Hold the line. Survive the night.", tech=["Unity", "C#", "Wave Spawning", "Pooling"], platform="WEB · PLAYGAMA", color="#f87171"),
    dict(slug="arcane-ascent", title="Arcane Ascent", genre="Puzzle Platformer", tagline="The Void Tower awaits. The only way out is up.", tech=["Unity", "C#", "HLSL", "2D Physics"], platform="WEB · WIN · ITCH", color="#c084fc"),
    dict(slug="orbit-rogue", title="Orbit Rogue", genre="Boss Rush · Bullet Hell", tagline="Stuck in orbit. Destined for glory.", tech=["Unity", "C#", "Roguelite", "AI FSM"], platform="WEB · WIN · ITCH", color="#22d3ee"),
    dict(slug="word-hunter", title="Word Hunter", genre="Word Puzzle", tagline="The ultimate test of vocabulary and speed.", tech=["Unity", "C#", "UI Toolkit", "Algorithms"], platform="WEB · WIN · ITCH", color="#34d399"),
    dict(slug="tic-tac-toe", title="Tic-Tac-Toe Online", genre="Online Multiplayer", tagline="A classic rebuilt around real-time netcode.", tech=["Unity", "C#", "Photon PUN 2"], platform="WEB · WIN · ITCH", color="#f472b6"),
    dict(slug="last-service", title="Last Service", genre="Psychological Horror", tagline="The station is closed. One final task remains.", tech=["Unity", "C#", "3D", "Narrative"], platform="WIN · ITCH", color="#94a3b8"),
    dict(slug="zombie-rush", title="Zombie Rush", genre="FPS · Wave Survival", tagline="Survive the horde. Adapt or be overrun.", tech=["Unity", "C#", "FPS", "Enemy AI"], platform="WIN · ITCH", color="#84cc16"),
]

TOOLS = [
    dict(slug="smart-toolkit", title="Smart Toolkit", kind="Web App", desc="Practical calculators, tools and guides for everyday game development.", tech=["Next.js", "TypeScript", "Tailwind"], button="Open smarttoolkit.app", status="Live"),
    dict(slug="debug-the-day", title="Debug the Day", kind="Gamified Life App", desc="Tasks, habits, money and notes, levelled up with XP and quests.", tech=["Next.js", "TypeScript", "Supabase"], button="Open App", status="Live"),
    dict(slug="smart-autosave", title="Smart AutoSave", kind="Unity Editor Extension", desc="Auto-save and rolling scene backups so you never lose a scene again.", tech=["Unity", "C#", "Editor", "UIElements"], button="Get on itch.io", status="Free · Open source"),
]

PREFABS = [
    dict(slug="prefab-racer", file="TopDownRacer.prefab", title="Top-Down Racer", desc="2D racing prototype exploring multiplayer networking.", tech=["Unity", "C#", "Netcode"], color="#f472b6"),
    dict(slug="prefab-pong", file="RetroPong.prefab", title="Retro Pong Rebooted", desc="Pong remake with menus, CPU AI and PvP, from scratch.", tech=["C++", "Raylib"], color="#4a9eff"),
]


if __name__ == "__main__":
    header()
    inspector()
    hierarchy(GAMES)
    for g in GAMES:
        game_card(g)
    packages_header()
    for i, t in enumerate(TOOLS):
        package_row(t, i)
    console()
    for p in PREFABS:
        prefab(p)
    section("stack", "▦", "Project", "Assets/TechStack")
    section("stats", "▥", "Profiler", "GitHub activity")
    section("snake", "≋", "Timeline", "Contributions.anim")
    status_bar()
