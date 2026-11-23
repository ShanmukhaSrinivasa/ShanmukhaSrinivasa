"""Generates the animated SVG cards used in README.md.

Run from the repo root:  python scripts/build_cards.py
Screenshots are read from assets/src/*.jpg and embedded as base64, because
GitHub blocks external images inside SVGs.
"""
import base64
import html
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "src")

MONO = "'Consolas','Courier New',monospace"
SANS = "'Segoe UI','Inter','Helvetica Neue',Arial,sans-serif"
BLUE, BLUE2 = "#38BDF8", "#2F6BFF"


def esc(s):
    return html.escape(s, quote=True)


def img64(name):
    with open(os.path.join(SRC, name), "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


def defs(uid, a, b, w, h):
    return f"""<defs>
<linearGradient id="bg{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070b14"/><stop offset="1" stop-color="#0d1526"/></linearGradient>
<linearGradient id="acc{uid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>
<linearGradient id="scan{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}" stop-opacity="0"/><stop offset=".5" stop-color="{a}" stop-opacity=".09"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></linearGradient>
<linearGradient id="fade{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset=".5" stop-color="#070b14" stop-opacity="0"/><stop offset="1" stop-color="#070b14" stop-opacity=".92"/></linearGradient>
<filter id="glow{uid}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="grid{uid}" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{a}" stroke-opacity=".06"/></pattern>
</defs><rect width="{w}" height="{h}" rx="16" fill="url(#bg{uid})"/><rect width="{w}" height="{h}" rx="16" fill="url(#grid{uid})"/><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="15" fill="none" stroke="url(#acc{uid})" stroke-opacity=".5" stroke-width="2"/>"""


def scanline(uid, w, h, dur=5):
    return f'<rect x="0" y="-80" width="{w}" height="80" fill="url(#scan{uid})"><animate attributeName="y" values="-80;{h}" dur="{dur}s" repeatCount="indefinite"/></rect>'


def runner(uid, d, delay=0.0):
    """A glowing dash that runs around a path."""
    return (f'<path d="{d}" fill="none" stroke="url(#acc{uid})" stroke-width="2.5" pathLength="100" '
            f'stroke-dasharray="14 86" filter="url(#glow{uid})"><animate attributeName="stroke-dashoffset" '
            f'values="100;0" dur="4s" begin="{delay:.2f}s" repeatCount="indefinite"/></path>')


def chips(items, x, y, color, max_x):
    out = []
    for t in items:
        w = int(len(t) * 6.9 + 18)
        if x + w > max_x:
            break
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="{color}" fill-opacity=".12" stroke="{color}" stroke-opacity=".5"/>'
                   f'<text x="{x + w / 2}" y="{y + 15}" text-anchor="middle" font-family="{MONO}" font-size="11.5" fill="{color}">{esc(t)}</text>')
        x += w + 8
    return "".join(out)


def write(path, svg):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"{path}  {len(svg) // 1024} KB")


# ─────────────────────────────── PLAYER CARD ───────────────────────────────
def player_card():
    W, H, u = 900, 420, "p"
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">', defs(u, BLUE, BLUE2, W, H)]
    s.append(f'<path d="M24 22 h10 M24 22 v10" stroke="{BLUE}" stroke-width="3"/><path d="M876 22 h-10 M876 22 v10" stroke="{BLUE2}" stroke-width="3"/>')
    s.append(f'<text x="450" y="44" text-anchor="middle" font-family="{MONO}" font-size="20" font-weight="700" letter-spacing="6" fill="url(#acc{u})" filter="url(#glow{u})">// PLAYER PROFILE</text>')
    s.append(f'<rect x="360" y="56" width="180" height="2" fill="url(#acc{u})"><animate attributeName="width" values="40;180;40" dur="4s" repeatCount="indefinite"/><animate attributeName="x" values="430;360;430" dur="4s" repeatCount="indefinite"/></rect>')
    s.append(scanline(u, W, H))
    panel = "M38,80 H274 V386 L260,400 H24 V94 Z"
    s.append(f'<path d="{panel}" fill="#0b1324" fill-opacity=".9" stroke="{BLUE}" stroke-opacity=".35" stroke-width="1.5"/>')
    s.append(runner(u, panel))
    # avatar
    s.append(f'<clipPath id="av{u}"><circle cx="149" cy="170" r="54"/></clipPath>')
    s.append(f'<image href="{img64("avatar.jpg")}" x="95" y="116" width="108" height="108" clip-path="url(#av{u})" preserveAspectRatio="xMidYMid slice"/>')
    s.append(f'<circle cx="149" cy="170" r="54" fill="none" stroke="url(#acc{u})" stroke-width="3" filter="url(#glow{u})"/>')
    s.append(f'<circle cx="149" cy="170" r="64" fill="none" stroke="{BLUE}" stroke-opacity=".4" stroke-dasharray="6 8"><animateTransform attributeName="transform" type="rotate" from="0 149 170" to="360 149 170" dur="14s" repeatCount="indefinite"/></circle>')
    s.append(f'<text x="149" y="262" text-anchor="middle" font-family="{SANS}" font-size="19" font-weight="900" fill="#fff" letter-spacing="1">SHANMUKHA</text>')
    s.append(f'<text x="149" y="282" text-anchor="middle" font-family="{SANS}" font-size="14" font-weight="700" fill="#cfe3ff" letter-spacing="3">SRINIVASA</text>')
    s.append(f'<text x="149" y="304" text-anchor="middle" font-family="{MONO}" font-size="11.5" fill="{BLUE}" letter-spacing="2">GAMEPLAY PROGRAMMER</text>')
    s.append(f'<text x="44" y="330" font-family="{MONO}" font-size="11.5" fill="#9fb3d1">XP: ALWAYS LEVELING UP</text>')
    s.append(f'<rect x="44" y="338" width="210" height="10" rx="5" fill="#16213d"/>')
    s.append(f'<rect x="44" y="338" width="0" height="10" rx="5" fill="url(#acc{u})" filter="url(#glow{u})"><animate attributeName="width" values="0;176" dur="2s" fill="freeze"/></rect>')
    s.append(f'<text x="44" y="372" font-family="{MONO}" font-size="11" fill="#4ade80">● ONLINE — BUILDING GAMES<animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></text>')
    rows = [
        ("CLASS", "Game Developer · Gameplay Programmer"),
        ("MAIN WEAPON", "Unity + C#"),
        ("SIDE ENGINES", "Unreal Engine · Godot"),
        ("LOW-LEVEL", "C++ with Raylib & SFML"),
        ("BACKGROUND", "Game Design & Animation"),
        ("RELEASES", "itch.io · Playgama · Web, Windows, Android"),
        ("HOME BASE", "Bengaluru, India"),
    ]
    y = 80
    for i, (k, v) in enumerate(rows):
        s.append(f'<path d="M306,{y} H876 V{y+24} L868,{y+32} H298 V{y+8} Z" fill="#0b1324" stroke="{BLUE}" stroke-opacity=".25"/>')
        s.append(f'<rect x="298" y="{y}" width="4" height="32" fill="url(#acc{u})"/>')
        s.append(f'<text x="316" y="{y+21}" font-family="{MONO}" font-size="12.5" fill="{BLUE}" letter-spacing="2">{k}</text>')
        s.append(f'<text x="470" y="{y+21}" font-family="{SANS}" font-size="15" font-weight="700" fill="#fff" opacity="0">{esc(v)}'
                 f'<animate attributeName="opacity" values="0;1" dur=".4s" begin="{0.15 * i:.2f}s" fill="freeze"/></text>')
        y += 40
    s.append(f'<text x="298" y="378" font-family="{MONO}" font-size="12" fill="#9fb3d1">CURRENT QUEST &gt; <tspan fill="#fff">shipping polished web games &amp; Unity editor tools</tspan></text>')
    s.append(f'<rect x="298" y="388" width="578" height="2" fill="url(#acc{u})" opacity=".35"/>')
    s.append("</svg>")
    write("assets/player-card.svg", "".join(s))


# ─────────────────────────────── GAME CARDS ───────────────────────────────
def game_card(slug, title, genre, tagline, tech, platform, button, a, b, folder="shipped"):
    W, H, u = 440, 400, "g"
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">', defs(u, a, b, W, H)]
    clip = "M30,12 H428 V228 L410,246 H12 V30 Z"
    s.append(f'<clipPath id="clip{u}"><path d="{clip}"/></clipPath><g clip-path="url(#clip{u})">')
    s.append(f'<image href="{img64(slug + ".jpg")}" x="12" y="12" width="416" height="234" preserveAspectRatio="xMidYMid slice"/>')
    s.append(f'<rect x="12" y="12" width="416" height="234" fill="url(#fade{u})"/></g>')
    s.append(f'<path d="{clip}" fill="none" stroke="{a}" stroke-opacity=".45" stroke-width="1.5"/>')
    s.append(runner(u, clip))
    gw = int(len(genre) * 7.2 + 22)
    s.append(f'<rect x="26" y="210" width="{gw}" height="24" rx="4" fill="#070b14" fill-opacity=".85" stroke="{a}"/>'
             f'<text x="{26 + gw / 2}" y="226" text-anchor="middle" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{a}" letter-spacing="1">{esc(genre.upper())}</text>')
    s.append(f'<text x="20" y="276" font-family="{SANS}" font-size="23" font-weight="900" fill="#fff" letter-spacing=".5">{esc(title)}</text>')
    s.append(f'<text x="20" y="298" font-family="{SANS}" font-size="13" font-style="italic" fill="#9fb3d1">{esc(tagline)}</text>')
    s.append(chips(tech, 20, 312, a, 420))
    s.append(f'<rect x="20" y="350" width="400" height="1" fill="{a}" opacity=".25"/>')
    s.append(f'<text x="20" y="378" font-family="{MONO}" font-size="11" fill="#7f93b5">{esc(platform)}</text>')
    bw = int(len(button) * 8 + 34)
    bx = 420 - bw
    s.append(f'<rect x="{bx}" y="360" width="{bw}" height="28" rx="6" fill="url(#acc{u})" filter="url(#glow{u})"><animate attributeName="opacity" values="1;.7;1" dur="1.8s" repeatCount="indefinite"/></rect>')
    s.append(f'<text x="{bx + bw / 2}" y="379" text-anchor="middle" font-family="{MONO}" font-size="12.5" font-weight="700" fill="#070b14" letter-spacing="1">{esc(button)}</text>')
    s.append(scanline(u, W, H, 6))
    s.append("</svg>")
    write(f"assets/{folder}/{slug}.svg", "".join(s))


GAMES = [
    ("haunted-hotel", "Haunted Hotel Empire", "3D Idle Tycoon", "Check in. Never check out.", ["Unity", "C#", "Idle Economy", "WebGL"], "WEB · PLAYGAMA", "▶ PLAY FREE", "#A78BFA", "#38BDF8"),
    ("last-bunker", "Last Bunker", "Idle Zombie Defense", "Hold the line. Survive the night.", ["Unity", "C#", "Wave Spawning", "Pooling"], "WEB · PLAYGAMA", "▶ PLAY FREE", "#F87171", "#FB923C"),
    ("arcane-ascent", "Arcane Ascent", "Puzzle Platformer", "The Void Tower awaits. The only way out is UP.", ["Unity", "C#", "HLSL", "2D Physics"], "WEB · WINDOWS · ITCH.IO", "▶ PLAY FREE", "#C084FC", "#818CF8"),
    ("orbit-rogue", "Orbit Rogue", "Boss Rush · Bullet Hell", "Stuck in orbit. Destined for glory.", ["Unity", "C#", "Roguelite", "AI FSM"], "WEB · WINDOWS · ITCH.IO", "▶ PLAY FREE", "#22D3EE", "#3B82F6"),
    ("last-service", "Last Service", "Psychological Horror", "The station is closed. One final task remains.", ["Unity", "C#", "3D", "Narrative"], "WINDOWS · ITCH.IO", "▶ DOWNLOAD", "#94A3B8", "#EF4444"),
    ("zombie-rush", "Zombie Rush", "FPS · Wave Survival", "Survive the horde. Adapt or be overrun.", ["Unity", "C#", "FPS", "Enemy AI"], "WINDOWS · ITCH.IO", "▶ DOWNLOAD", "#84CC16", "#22C55E"),
    ("word-hunter", "Word Hunter", "Word Puzzle", "The ultimate test of vocabulary and speed.", ["Unity", "C#", "UI Toolkit", "Algorithms"], "WEB · WINDOWS · ITCH.IO", "▶ PLAY FREE", "#34D399", "#38BDF8"),
    ("tic-tac-toe", "Tic-Tac-Toe Online", "Online Multiplayer", "A classic rebuilt around real-time netcode.", ["Unity", "C#", "Photon PUN 2"], "WEB · WINDOWS · ITCH.IO", "▶ PLAY FREE", "#F472B6", "#A78BFA"),
]

TOOLS = [
    ("smart-toolkit", "Smart Toolkit", "Web App", "Calculators, tools & guides for game devs.", ["Next.js", "TypeScript", "Tailwind"], "SMARTTOOLKIT.APP", "▶ OPEN", "#38BDF8", "#2F6BFF"),
    ("debug-the-day", "Debug the Day", "Gamified Life App", "Tasks, habits & money, with XP and quests.", ["Next.js", "TypeScript", "Supabase"], "WEB · PWA", "▶ OPEN", "#4ADE80", "#22D3EE"),
    ("smart-autosave", "Smart AutoSave", "Unity Editor Tool", "Never lose a scene again. Free & open source.", ["Unity", "C#", "Editor", "UIElements"], "UNITY 2021.3+ · ITCH.IO", "★ GET IT", "#FBBF24", "#38BDF8"),
]


# ─────────────────────────────── MINI CARDS (no screenshot) ───────────────────────────────
def mini_card(slug, glyph, title, desc, tags, a, b):
    W, H, u = 290, 210, "m"
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">', defs(u, a, b, W, H)]
    s.append(f'<circle cx="48" cy="52" r="26" fill="{a}" fill-opacity=".1" stroke="url(#acc{u})" stroke-width="2" filter="url(#glow{u})"/>')
    s.append(f'<circle cx="48" cy="52" r="33" fill="none" stroke="{a}" stroke-opacity=".35" stroke-dasharray="4 6"><animateTransform attributeName="transform" type="rotate" from="0 48 52" to="360 48 52" dur="12s" repeatCount="indefinite"/></circle>')
    s.append(f'<text x="48" y="59" text-anchor="middle" font-family="{MONO}" font-size="18" font-weight="700" fill="{a}">{esc(glyph)}</text>')
    s.append(f'<text x="92" y="48" font-family="{SANS}" font-size="17" font-weight="900" fill="#fff">{esc(title)}</text>')
    s.append(f'<rect x="92" y="56" width="60" height="2" fill="url(#acc{u})"><animate attributeName="width" values="20;80;20" dur="4s" repeatCount="indefinite"/></rect>')
    y = 104
    for line in desc:
        s.append(f'<text x="22" y="{y}" font-family="{SANS}" font-size="13" fill="#b6c6e0">{esc(line)}</text>')
        y += 20
    s.append(chips(tags, 22, 168, a, 272))
    s.append(scanline(u, W, H, 5))
    s.append("</svg>")
    write(f"assets/projects/{slug}.svg", "".join(s))


MINIS = [
    ("multiplayer-racer", "P2", "Top-Down Racer", ["2D racing prototype exploring", "multiplayer networking."], ["Unity", "Netcode"], "#F472B6", "#A78BFA"),
    ("retro-pong", "C++", "Retro Pong Rebooted", ["Pong remake with menus, CPU AI", "and PvP, written from scratch."], ["C++", "Raylib"], "#38BDF8", "#2F6BFF"),
]


# ─────────────────────────────── SKILL TREE ───────────────────────────────
def skill_tree():
    W, H, u = 900, 400, "s"
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">', defs(u, BLUE, BLUE2, W, H)]
    s.append(f'<text x="450" y="44" text-anchor="middle" font-family="{MONO}" font-size="20" font-weight="700" letter-spacing="6" fill="url(#acc{u})" filter="url(#glow{u})">// SKILL TREE</text>')
    s.append(scanline(u, W, H, 6))
    branches = [
        (160, "GAMEPLAY", "#38BDF8", ["Gameplay Systems", "Game Feel & Juice", "Enemy AI · FSMs", "Procedural Gen"]),
        (450, "ENGINEERING", "#A78BFA", ["Object Pooling · Perf", "Shaders · HLSL", "Multiplayer · Photon", "WebGL Publishing"]),
        (740, "CRAFT", "#FBBF24", ["Game Design", "3D Art · Blender/Maya", "Animation", "Editor Tools"]),
    ]
    root_y = 82
    s.append(f'<circle cx="450" cy="{root_y}" r="16" fill="#0b1324" stroke="url(#acc{u})" stroke-width="2.5" filter="url(#glow{u})"/>'
             f'<text x="450" y="{root_y + 4}" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="700" fill="#fff">SHK</text>')
    for bi, (x, name, c, nodes) in enumerate(branches):
        path = f"M450,{root_y + 16} C450,118 {x},104 {x},128"
        s.append(f'<path d="{path}" fill="none" stroke="{c}" stroke-opacity=".35" stroke-width="2"/>')
        s.append(f'<path d="{path}" fill="none" stroke="{c}" stroke-width="3" pathLength="100" stroke-dasharray="10 90" filter="url(#glow{u})"><animate attributeName="stroke-dashoffset" values="100;0" dur="2.5s" begin="{bi * .4:.1f}s" repeatCount="indefinite"/></path>')
        s.append(f'<rect x="{x - 90}" y="128" width="180" height="30" rx="6" fill="{c}" fill-opacity=".14" stroke="{c}"/>'
                 f'<text x="{x}" y="148" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="700" fill="{c}" letter-spacing="3">{name}</text>')
        s.append(f'<line x1="{x}" y1="158" x2="{x}" y2="{176 + 52 * (len(nodes) - 1)}" stroke="{c}" stroke-opacity=".3" stroke-width="2"/>')
        s.append(f'<circle cx="{x}" cy="160" r="3" fill="{c}" filter="url(#glow{u})"><animate attributeName="cy" values="160;{176 + 52 * (len(nodes) - 1)}" dur="3s" begin="{bi * .5:.1f}s" repeatCount="indefinite"/></circle>')
        for ni, label in enumerate(nodes):
            ny = 176 + 52 * ni
            s.append(f'<path d="M{x - 104},{ny} H{x + 96} L{x + 104},{ny + 8} V{ny + 34} H{x - 96} L{x - 104},{ny + 26} Z" fill="#0b1324" stroke="{c}" stroke-opacity=".45"/>')
            s.append(f'<rect x="{x - 104}" y="{ny + 6}" width="3" height="22" fill="{c}"/>')
            s.append(f'<text x="{x - 88}" y="{ny + 22}" font-family="{SANS}" font-size="13.5" font-weight="600" fill="#e6efff" opacity="0">{esc(label)}'
                     f'<animate attributeName="opacity" values="0;1" dur=".4s" begin="{.3 + .15 * ni + .2 * bi:.2f}s" fill="freeze"/></text>')
            s.append(f'<circle cx="{x + 88}" cy="{ny + 17}" r="4" fill="{c}"><animate attributeName="opacity" values="1;.3;1" dur="2s" begin="{ni * .3:.1f}s" repeatCount="indefinite"/></circle>')
    s.append("</svg>")
    write("assets/skill-tree.svg", "".join(s))


if __name__ == "__main__":
    player_card()
    skill_tree()
    for g in GAMES:
        game_card(*g)
    for t in TOOLS:
        game_card(*t, folder="tools")
    for m in MINIS:
        mini_card(*m)
