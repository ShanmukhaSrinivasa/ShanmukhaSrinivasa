"""Generates the dark-fantasy RPG style SVG cards used in README.md.

Run from the repo root:  python scripts/build_cards.py
Screenshots are read from assets/src/*.jpg and embedded as base64, because
GitHub blocks external images inside SVGs.
"""
import base64
import html
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "src")
OUT = "assets/rpg"

SERIF = "'Palatino Linotype','Book Antiqua',Palatino,Georgia,serif"
SANS = "'Segoe UI','Helvetica Neue',Arial,sans-serif"

BG1, BG2 = "#0b0b0d", "#18181d"
STEEL = "#5c626c"
SILVER = "#c9ced6"
BRIGHT = "#eef1f5"
MUTED = "#8d939c"
CRIMSON = "#2f7fd8"  # accent blue (name kept from the original red theme)
EMBER = "#5cb8ff"


def esc(s):
    return html.escape(s, quote=True)


def img64(name):
    with open(os.path.join(SRC, name), "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


def tw(s, size, k=0.58):
    return len(s) * size * k


def write(name, svg):
    path = f"{OUT}/{name}"
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"{path}  {len(svg) // 1024} KB")


def defs(w, h, accent=CRIMSON):
    return f"""<defs>
<radialGradient id="bg" cx="50%" cy="40%" r="75%"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG1}"/></radialGradient>
<linearGradient id="silver" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="{SILVER}"/><stop offset="1" stop-color="#7d838c"/></linearGradient>
<linearGradient id="steelline" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{SILVER}" stop-opacity="0"/><stop offset=".5" stop-color="{SILVER}" stop-opacity=".8"/><stop offset="1" stop-color="{SILVER}" stop-opacity="0"/></linearGradient>
<linearGradient id="blood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="#0b2547"/></linearGradient>
<linearGradient id="vig" x1="0" y1="0" x2="0" y2="1"><stop offset=".55" stop-color="{BG1}" stop-opacity="0"/><stop offset="1" stop-color="{BG1}" stop-opacity=".95"/></linearGradient>
<filter id="glow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="2.5" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.2"/></filter>
<pattern id="noise" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0 6L6 0" stroke="{SILVER}" stroke-opacity=".025"/></pattern>
</defs><rect width="{w}" height="{h}" rx="10" fill="url(#bg)"/><rect width="{w}" height="{h}" rx="10" fill="url(#noise)"/>"""


def diamond(x, y, r, fill=SILVER, extra=""):
    return f'<path d="M{x},{y - r} L{x + r},{y} L{x},{y + r} L{x - r},{y} Z" fill="{fill}" {extra}/>'


def frame(w, h, accent=CRIMSON):
    """Double steel border with corner ornaments."""
    s = [f'<rect x="3" y="3" width="{w - 6}" height="{h - 6}" rx="8" fill="none" stroke="{STEEL}" stroke-width="1.5"/>',
         f'<rect x="9" y="9" width="{w - 18}" height="{h - 18}" rx="5" fill="none" stroke="{SILVER}" stroke-opacity=".22"/>']
    for cx, cy, dx, dy in [(9, 9, 1, 1), (w - 9, 9, -1, 1), (9, h - 9, 1, -1), (w - 9, h - 9, -1, -1)]:
        s.append(f'<path d="M{cx},{cy + dy * 22} V{cy} H{cx + dx * 22}" fill="none" stroke="{SILVER}" stroke-width="2"/>')
        s.append(diamond(cx + dx * 6, cy + dy * 6, 3.5, accent, 'filter="url(#glow)"'))
    return "".join(s)


def divider(cx, y, half, accent=CRIMSON):
    return (f'<rect x="{cx - half}" y="{y - .5}" width="{half * 2}" height="1" fill="url(#steelline)"/>'
            + diamond(cx, y, 5, "none", f'stroke="{SILVER}" stroke-width="1.2"') + diamond(cx, y, 2.2, accent, 'filter="url(#glow)"')
            + diamond(cx - 16, y, 2, SILVER, 'opacity=".6"') + diamond(cx + 16, y, 2, SILVER, 'opacity=".6"'))


def embers(w, h, n, seed, color=EMBER):
    rnd = random.Random(seed)
    s = []
    for _ in range(n):
        x = rnd.uniform(20, w - 20)
        r = rnd.uniform(.8, 2.0)
        dur = rnd.uniform(5, 10)
        delay = rnd.uniform(0, 8)
        drift = rnd.uniform(-30, 30)
        s.append(f'<circle cx="{x:.0f}" cy="{h}" r="{r:.1f}" fill="{color}" opacity="0" filter="url(#glow)">'
                 f'<animate attributeName="cy" values="{h};{h * .25:.0f}" dur="{dur:.1f}s" begin="{delay:.1f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="cx" values="{x:.0f};{x + drift:.0f}" dur="{dur:.1f}s" begin="{delay:.1f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;.9;0" dur="{dur:.1f}s" begin="{delay:.1f}s" repeatCount="indefinite"/></circle>')
    return "".join(s)


def plaque(cx, y, text, size=17, accent=CRIMSON):
    """Centered title in silver serif caps flanked by ornaments."""
    half = tw(text, size, .86) / 2 + 30
    return (f'<text x="{cx}" y="{y}" text-anchor="middle" font-family="{SERIF}" font-size="{size}" font-weight="700" letter-spacing="5" fill="url(#silver)">{esc(text)}</text>'
            f'<rect x="{cx - half - 90}" y="{y - size * .35:.0f}" width="90" height="1" fill="url(#steelline)"/>'
            f'<rect x="{cx + half}" y="{y - size * .35:.0f}" width="90" height="1" fill="url(#steelline)"/>'
            + diamond(cx - half - 4, y - size * .35, 4, accent, 'filter="url(#glow)"')
            + diamond(cx + half + 4, y - size * .35, 4, accent, 'filter="url(#glow)"'))


def tags(items, x, y, max_x, accent):
    out = []
    for t in items:
        w = int(tw(t, 11, .6) + 20)
        if x + w > max_x:
            break
        out.append(f'<path d="M{x + 6},{y} H{x + w - 6} L{x + w},{y + 10} L{x + w - 6},{y + 20} H{x + 6} L{x},{y + 10} Z" fill="{accent}" fill-opacity=".12" stroke="{SILVER}" stroke-opacity=".35"/>'
                   f'<text x="{x + w / 2}" y="{y + 14}" text-anchor="middle" font-family="{SANS}" font-size="11" fill="{SILVER}">{esc(t)}</text>')
        x += w + 7
    return "".join(out)


def svg_open(w, h):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'


# ─────────────────────────────── CHARACTER SHEET ───────────────────────────────
def character_sheet():
    W, H = 900, 440
    s = [svg_open(W, H), defs(W, H), embers(W, H, 18, 1), frame(W, H)]
    s.append(plaque(450, 48, "CHARACTER SHEET", 19))
    # portrait in a pointed arch
    px, py, pw, ph = 46, 82, 200, 260
    arch = f"M{px},{py + 70} Q{px},{py} {px + pw / 2},{py - 6} Q{px + pw},{py} {px + pw},{py + 70} V{py + ph} H{px} Z"
    s.append(f'<clipPath id="arch"><path d="{arch}"/></clipPath>')
    s.append(f'<g clip-path="url(#arch)"><image href="{img64("portrait.jpg")}" x="{px}" y="{py - 6}" width="{pw}" height="{ph + 6}" preserveAspectRatio="xMidYMid slice"/>'
             f'<rect x="{px}" y="{py - 6}" width="{pw}" height="{ph + 6}" fill="url(#vig)"/>'
             f'<rect x="{px}" y="{py - 6}" width="{pw}" height="{ph + 6}" fill="#000" opacity=".18"/></g>')
    s.append(f'<path d="{arch}" fill="none" stroke="{SILVER}" stroke-width="2"/>')
    s.append(f'<path d="{arch}" fill="none" stroke="{CRIMSON}" stroke-width="2" pathLength="100" stroke-dasharray="12 88" filter="url(#glow)">'
             f'<animate attributeName="stroke-dashoffset" values="100;0" dur="6s" repeatCount="indefinite"/></path>')
    s.append(diamond(px + pw / 2, py - 6, 5, CRIMSON, 'filter="url(#glow)"'))
    s.append(f'<text x="{px + pw / 2}" y="{py + ph + 34}" text-anchor="middle" font-family="{SERIF}" font-size="21" font-weight="700" letter-spacing="3" fill="url(#silver)">SHANMUKHA</text>')
    s.append(f'<text x="{px + pw / 2}" y="{py + ph + 54}" text-anchor="middle" font-family="{SERIF}" font-size="13" letter-spacing="6" fill="{MUTED}">SRINIVASA</text>')
    s.append(f'<text x="{px + pw / 2}" y="{py + ph + 78}" text-anchor="middle" font-family="{SERIF}" font-size="12" font-style="italic" fill="{EMBER}" opacity=".9">Level: always rising'
             f'<animate attributeName="opacity" values=".9;.45;.9" dur="2.4s" repeatCount="indefinite"/></text>')
    rows = [
        ("CLASS", "Game Developer · Gameplay Programmer"),
        ("PRIMARY WEAPON", "Unity + C#"),
        ("SECONDARY", "Unreal Engine · Godot"),
        ("FORGED IN", "C++ with Raylib & SFML"),
        ("ORIGIN", "Game Design & Animation"),
        ("REALMS", "itch.io · Playgama · Web, Windows, Android"),
        ("HOMELAND", "Bengaluru, India"),
    ]
    x0, y = 286, 98
    for i, (k, v) in enumerate(rows):
        s.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".5s" begin="{.2 + i * .15:.2f}s" fill="freeze"/>'
                 + diamond(x0 + 4, y - 5, 3, CRIMSON) +
                 f'<text x="{x0 + 18}" y="{y}" font-family="{SERIF}" font-size="12" letter-spacing="2.5" fill="{MUTED}">{k}</text>'
                 f'<text x="{x0 + 190}" y="{y}" font-family="{SERIF}" font-size="16" fill="{BRIGHT}">{esc(v)}</text>'
                 f'<rect x="{x0}" y="{y + 12}" width="{W - x0 - 40}" height="1" fill="{SILVER}" opacity=".1"/></g>')
        y += 38
    s.append(divider((x0 + W - 40) / 2, y + 2, (W - 40 - x0) / 2))
    s.append(f'<text x="{x0}" y="{y + 36}" font-family="{SERIF}" font-size="12" letter-spacing="2.5" fill="{EMBER}">CURRENT QUEST</text>'
             f'<text x="{x0 + 160}" y="{y + 36}" font-family="{SERIF}" font-size="15" font-style="italic" fill="{SILVER}">Shipping polished web games &amp; Unity editor tools</text>')
    s.append("</svg>")
    write("character-sheet.svg", "".join(s))


# ─────────────────────────────── QUEST CARD (game / tool) ───────────────────────────────
def quest_card(g, folder):
    W, H = 440, 410
    a = g["color"]
    s = [svg_open(W, H), defs(W, H, a), frame(W, H, a)]
    ix, iy, iw, ih = 20, 20, 400, 225
    s.append(f'<clipPath id="shot"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="3"/></clipPath>'
             f'<g clip-path="url(#shot)"><image href="{img64(g["slug"] + ".jpg")}" x="{ix}" y="{iy}" width="{iw}" height="{ih}" preserveAspectRatio="xMidYMid slice"/>'
             f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" fill="url(#vig)"/></g>'
             f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="3" fill="none" stroke="{SILVER}" stroke-opacity=".45"/>')
    # genre ribbon
    gt = g["genre"].upper()
    gw = tw(gt, 10.5, .68) + 26
    s.append(f'<path d="M{ix},{iy + ih - 34} H{ix + gw} L{ix + gw - 8},{iy + ih - 23} L{ix + gw},{iy + ih - 12} H{ix} Z" fill="url(#blood)" opacity=".92"/>'
             f'<text x="{ix + 10}" y="{iy + ih - 19}" font-family="{SERIF}" font-size="10.5" font-weight="700" letter-spacing="2" fill="#fff">{esc(gt)}</text>')
    s.append(embers(W, H, 7, sum(map(ord, g["slug"])), EMBER))
    y = iy + ih + 34
    s.append(f'<text x="{W / 2}" y="{y}" text-anchor="middle" font-family="{SERIF}" font-size="22" font-weight="700" letter-spacing="2" fill="url(#silver)">{esc(g["title"].upper())}</text>')
    s.append(divider(W / 2, y + 14, 150, a))
    s.append(f'<text x="{W / 2}" y="{y + 38}" text-anchor="middle" font-family="{SERIF}" font-size="13" font-style="italic" fill="{MUTED}">“{esc(g["tagline"])}”</text>')
    s.append(tags(g["tech"], 26, y + 52, W - 26, a))
    # footer row
    fy = H - 38
    s.append(f'<text x="26" y="{fy + 15}" font-family="{SERIF}" font-size="10.5" letter-spacing="2" fill="{MUTED}">{esc(g["platform"])}</text>')
    bt = g["button"]
    bw = tw(bt, 12, .72) + 34
    bx = W - 26 - bw
    s.append(f'<path d="M{bx + 8},{fy} H{bx + bw - 8} L{bx + bw},{fy + 11} L{bx + bw - 8},{fy + 22} H{bx + 8} L{bx},{fy + 11} Z" fill="url(#blood)" stroke="{SILVER}" stroke-opacity=".5" filter="url(#glow)">'
             f'<animate attributeName="opacity" values="1;.75;1" dur="2.2s" repeatCount="indefinite"/></path>'
             f'<text x="{bx + bw / 2}" y="{fy + 15}" text-anchor="middle" font-family="{SERIF}" font-size="12" font-weight="700" letter-spacing="2" fill="#fff">{esc(bt)}</text>')
    s.append("</svg>")
    write(f"{folder}/{g['slug']}.svg", "".join(s))


# ─────────────────────────────── SIDE QUEST (no screenshot) ───────────────────────────────
def side_quest(p):
    W, H = 440, 190
    a = p["color"]
    s = [svg_open(W, H), defs(W, H, a), frame(W, H, a), embers(W, H, 5, sum(map(ord, p["slug"])))]
    cx, cy = 74, 95
    s.append(f'<circle cx="{cx}" cy="{cy}" r="38" fill="{BG1}" stroke="{SILVER}" stroke-width="1.5"/>'
             f'<circle cx="{cx}" cy="{cy}" r="46" fill="none" stroke="{a}" stroke-opacity=".6" stroke-dasharray="2 7" filter="url(#glow)">'
             f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="20s" repeatCount="indefinite"/></circle>'
             f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" font-family="{SERIF}" font-size="22" font-weight="700" fill="url(#silver)">{esc(p["glyph"])}</text>')
    s.append(f'<text x="138" y="62" font-family="{SERIF}" font-size="10.5" letter-spacing="3" fill="{EMBER}">SIDE QUEST</text>'
             f'<text x="138" y="88" font-family="{SERIF}" font-size="19" font-weight="700" letter-spacing="1" fill="url(#silver)">{esc(p["title"].upper())}</text>')
    y = 112
    for line in p["desc"]:
        s.append(f'<text x="138" y="{y}" font-family="{SERIF}" font-size="13" font-style="italic" fill="{MUTED}">{esc(line)}</text>')
        y += 18
    s.append(tags(p["tech"], 138, y + 2, W - 22, a))
    s.append("</svg>")
    write(f"side/{p['slug']}.svg", "".join(s))


# ─────────────────────────────── ABILITY TREE ───────────────────────────────
def ability_tree():
    W, H = 900, 420
    s = [svg_open(W, H), defs(W, H), embers(W, H, 14, 7), frame(W, H)]
    s.append(plaque(450, 48, "ABILITIES", 19))
    branches = [
        (160, "GAMEPLAY", ["Gameplay Systems", "Game Feel & Juice", "Enemy AI · FSMs", "Procedural Gen"]),
        (450, "ENGINEERING", ["Object Pooling · Perf", "Shaders · HLSL", "Multiplayer · Photon", "WebGL Publishing"]),
        (740, "CRAFT", ["Game Design", "3D Art · Blender/Maya", "Animation", "Editor Tools"]),
    ]
    ry = 96
    s.append(f'<circle cx="450" cy="{ry}" r="20" fill="{BG1}" stroke="{SILVER}" stroke-width="2"/>'
             f'<circle cx="450" cy="{ry}" r="26" fill="none" stroke="{CRIMSON}" stroke-opacity=".7" stroke-dasharray="3 5" filter="url(#glow)">'
             f'<animateTransform attributeName="transform" type="rotate" from="0 450 {ry}" to="360 450 {ry}" dur="16s" repeatCount="indefinite"/></circle>'
             f'<text x="450" y="{ry + 5}" text-anchor="middle" font-family="{SERIF}" font-size="13" font-weight="700" fill="url(#silver)">SHK</text>')
    for bi, (x, name, nodes) in enumerate(branches):
        path = f"M450,{ry + 22} C450,{ry + 50} {x},{ry + 30} {x},{ry + 58}"
        s.append(f'<path d="{path}" fill="none" stroke="{SILVER}" stroke-opacity=".3" stroke-width="1.5"/>'
                 f'<path d="{path}" fill="none" stroke="{EMBER}" stroke-width="2.5" pathLength="100" stroke-dasharray="10 90" filter="url(#glow)">'
                 f'<animate attributeName="stroke-dashoffset" values="100;0" dur="2.8s" begin="{bi * .5:.1f}s" repeatCount="indefinite"/></path>')
        hy = ry + 58
        s.append(f'<path d="M{x - 86},{hy + 14} L{x - 74},{hy} H{x + 74} L{x + 86},{hy + 14} L{x + 74},{hy + 28} H{x - 74} Z" fill="url(#blood)" stroke="{SILVER}" stroke-opacity=".6"/>'
                 f'<text x="{x}" y="{hy + 19}" text-anchor="middle" font-family="{SERIF}" font-size="13" font-weight="700" letter-spacing="4" fill="#fff">{name}</text>')
        last = hy + 52 + 50 * (len(nodes) - 1)
        s.append(f'<line x1="{x}" y1="{hy + 28}" x2="{x}" y2="{last}" stroke="{SILVER}" stroke-opacity=".25" stroke-width="1.5"/>')
        for ni, label in enumerate(nodes):
            ny = hy + 52 + 50 * ni
            s.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".45s" begin="{.3 + ni * .18 + bi * .25:.2f}s" fill="freeze"/>'
                     f'<rect x="{x - 108}" y="{ny - 15}" width="216" height="30" rx="4" fill="{BG1}" stroke="{SILVER}" stroke-opacity=".35"/>'
                     + diamond(x - 92, ny, 5, "none", f'stroke="{SILVER}" stroke-width="1.2"') + diamond(x - 92, ny, 2.2, EMBER, 'filter="url(#glow)"') +
                     f'<text x="{x - 78}" y="{ny + 5}" font-family="{SERIF}" font-size="13.5" fill="{BRIGHT}">{esc(label)}</text></g>')
    s.append("</svg>")
    write("ability-tree.svg", "".join(s))


# ─────────────────────────────── SECTION TITLES + FOOTER ───────────────────────────────
def section(slug, title, subtitle=""):
    W, H = 900, 74 if subtitle else 56
    s = [svg_open(W, H),
         f'<defs><linearGradient id="silver" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="{SILVER}"/><stop offset="1" stop-color="#7d838c"/></linearGradient>'
         f'<linearGradient id="steelline" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{SILVER}" stop-opacity="0"/><stop offset=".5" stop-color="{SILVER}" stop-opacity=".8"/><stop offset="1" stop-color="{SILVER}" stop-opacity="0"/></linearGradient>'
         f'<filter id="glow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="2.5" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>',
         plaque(450, 34, title, 22)]
    if subtitle:
        s.append(f'<text x="450" y="62" text-anchor="middle" font-family="{SERIF}" font-size="13" font-style="italic" fill="{MUTED}">{esc(subtitle)}</text>')
    s.append("</svg>")
    write(f"section-{slug}.svg", "".join(s))


def footer():
    W, H = 900, 120
    s = [svg_open(W, H), defs(W, H).replace(f'<rect width="{W}" height="{H}" rx="10" fill="url(#bg)"/><rect width="{W}" height="{H}" rx="10" fill="url(#noise)"/>', ''),
         embers(W, H, 16, 99)]
    s.append(divider(450, 30, 300))
    s.append(f'<text x="450" y="70" text-anchor="middle" font-family="{SERIF}" font-size="20" font-weight="700" letter-spacing="6" fill="url(#silver)">FAREWELL, TRAVELER</text>')
    s.append(f'<text x="450" y="96" text-anchor="middle" font-family="{SERIF}" font-size="13" font-style="italic" fill="{MUTED}">Always learning. Always building. Always improving.</text>')
    s.append("</svg>")
    write("footer.svg", "".join(s))


GAMES = [
    dict(slug="haunted-hotel", title="Haunted Hotel Empire", genre="3D Idle Tycoon", tagline="Check in. Never check out.", tech=["Unity", "C#", "Idle Economy", "WebGL"], platform="WEB · PLAYGAMA", button="▶ PLAY", color="#7b4bc9"),
    dict(slug="last-bunker", title="Last Bunker", genre="Idle Zombie Defense", tagline="Hold the line. Survive the night.", tech=["Unity", "C#", "Wave Spawning", "Pooling"], platform="WEB · PLAYGAMA", button="▶ PLAY", color="#1f6fc7"),
    dict(slug="arcane-ascent", title="Arcane Ascent", genre="Puzzle Platformer", tagline="The only way out is up.", tech=["Unity", "C#", "HLSL", "2D Physics"], platform="WEB · WINDOWS · ITCH.IO", button="▶ PLAY", color="#7b4bc9"),
    dict(slug="orbit-rogue", title="Orbit Rogue", genre="Boss Rush", tagline="Stuck in orbit. Destined for glory.", tech=["Unity", "C#", "Roguelite", "AI FSM"], platform="WEB · WINDOWS · ITCH.IO", button="▶ PLAY", color="#2a6f97"),
    dict(slug="word-hunter", title="Word Hunter", genre="Word Puzzle", tagline="The ultimate test of vocabulary and speed.", tech=["Unity", "C#", "UI Toolkit", "Algorithms"], platform="WEB · WINDOWS · ITCH.IO", button="▶ PLAY", color="#2f7d5b"),
    dict(slug="tic-tac-toe", title="Tic-Tac-Toe Online", genre="Online Multiplayer", tagline="A classic rebuilt around real-time netcode.", tech=["Unity", "C#", "Photon PUN 2"], platform="WEB · WINDOWS · ITCH.IO", button="▶ PLAY", color="#9c2f6b"),
    dict(slug="last-service", title="Last Service", genre="Psychological Horror", tagline="One final task remains.", tech=["Unity", "C#", "3D", "Narrative"], platform="WINDOWS · ITCH.IO", button="▶ DOWNLOAD", color="#3a5f8f"),
    dict(slug="zombie-rush", title="Zombie Rush", genre="FPS Survival", tagline="Survive the horde. Adapt or be overrun.", tech=["Unity", "C#", "FPS", "Enemy AI"], platform="WINDOWS · ITCH.IO", button="▶ DOWNLOAD", color="#5d7a1f"),
]

TOOLS = [
    dict(slug="smart-toolkit", title="Smart Toolkit", genre="Web App", tagline="Tools and guides for game developers.", tech=["Next.js", "TypeScript", "Tailwind"], platform="SMARTTOOLKIT.APP", button="OPEN", color="#2a6f97"),
    dict(slug="debug-the-day", title="Debug the Day", genre="Gamified Life App", tagline="Tasks, habits and money, with XP and quests.", tech=["Next.js", "TypeScript", "Supabase"], platform="WEB APP", button="OPEN", color="#2f7d5b"),
    dict(slug="smart-autosave", title="Smart AutoSave", genre="Unity Editor Tool", tagline="Never lose a scene again.", tech=["Unity", "C#", "Editor"], platform="FREE · OPEN SOURCE", button="GET IT", color="#1f6fc7"),
]

SIDE = [
    dict(slug="top-down-racer", glyph="II", title="Top-Down Racer", desc=["A 2D racing prototype exploring", "multiplayer networking."], tech=["Unity", "C#", "Netcode"], color="#9c2f6b"),
    dict(slug="retro-pong", glyph="C++", title="Retro Pong Rebooted", desc=["Pong remade from scratch with", "menus, CPU AI and PvP."], tech=["C++", "Raylib"], color="#2a6f97"),
]


if __name__ == "__main__":
    character_sheet()
    for g in GAMES:
        quest_card(g, "quests")
    for t in TOOLS:
        quest_card(t, "artifacts")
    ability_tree()
    for p in SIDE:
        side_quest(p)
    section("quests", "QUESTS COMPLETED", "Choose a game and play it free · most run in your browser")
    section("artifacts", "FORGED ARTIFACTS", "Tools and apps I've built")
    section("arsenal", "ARSENAL")
    section("side", "SIDE QUESTS")
    section("chronicle", "CHRONICLE", "My journey on GitHub")
    footer()
