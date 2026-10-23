"""Scene renderers. Each returns an SVG string; none use scripts or external resources."""
from __future__ import annotations

import hashlib
import math
from datetime import datetime

from . import astro, physics
from .svg import C, GLOW_DEFS, GRID_DEFS, col, document, esc, frame, kt, n


# ═══ 1. HERO ═════════════════════════════════════════════════════════════════

def hero(p: dict, sig: bytes) -> str:
    W, H, T, FPS = 900, 360, 10.0, 30
    name = p["person"]["name"].upper()
    size = 66
    cw = size * 0.6
    x0 = W / 2 - len(name) * cw / 2 + cw / 2
    out = [frame(W, H)]

    # twinkling starfield (seeded)
    rng = physics.seeded(7)
    for _ in range(34):
        x, y, r = rng.uniform(20, W - 20), rng.uniform(20, H - 20), rng.choice([0.8, 1, 1.4])
        d = rng.uniform(2.5, 6)
        out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{r}" fill="#fff" opacity=".5">'
                   f'<animate attributeName="opacity" values=".1;.8;.1" dur="{n(d)}s" repeatCount="indefinite"/></circle>')

    out.append(f'<rect width="{W}" height="2" fill="{C["accent"]}" opacity=".07">'
               f'<animate attributeName="y" values="0;{H}" dur="6s" repeatCount="indefinite"/></rect>')

    out.append(f'<text x="40" y="52" font-size="13" fill="{C["accent"]}" letter-spacing="2">'
               f'{esc(p["person"]["kicker"])}</text>')
    # status pill
    st = p["person"]["status"]
    pw = len(st) * 6.7 + 44
    px = W - 40 - pw
    out.append(f'<rect x="{n(px)}" y="34" width="{n(pw)}" height="26" rx="13" fill="{C["accent"]}" fill-opacity=".08" '
               f'stroke="{C["accent"]}" stroke-opacity=".5"/>'
               f'<circle cx="{n(px + 16)}" cy="47" r="4" fill="{C["accent"]}">'
               f'<animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle>'
               f'<text x="{n(px + 28)}" y="51" font-size="11" fill="{C["accent"]}" textLength="{n(len(st) * 6.7)}" '
               f'lengthAdjust="spacing">{esc(st)}</text>')

    # name letters: real ballistic drops
    out.append(f'<linearGradient id="ng" gradientUnits="userSpaceOnUse" x1="{n(x0 - cw)}" y1="0" x2="{n(x0 + len(name) * cw)}" y2="0">'
               f'<stop offset="0" stop-color="{C["accent"]}"/><stop offset=".55" stop-color="{C["a2"]}"/>'
               f'<stop offset="1" stop-color="{C["violet"]}"/></linearGradient>')
    out.append('<g filter="url(#glow)" font-size="66" font-weight="800" text-anchor="middle" fill="url(#ng)">')
    t_sim = 3.4
    nf = int(t_sim * FPS) + 1
    for i, ch in enumerate(name):
        if ch == " ":
            continue
        t0 = 0.3 + i * 0.075
        ys = physics.drop(t0, 240, 2600, 0.38, FPS, t_sim)
        vals = ";".join(f"0 {n(y)}" for y in ys) + ";0 0"
        keys = kt([k / (FPS * T) for k in range(nf)] + [1.0])
        ts = t0 / T
        out.append(
            f'<text x="{n(x0 + i * cw)}" y="170" opacity="0">{esc(ch)}'
            f'<animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="{keys}" dur="{n(T)}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{ts:.4f};{ts + 0.004:.4f};{(T - 0.8) / T:.4f};{(T - 0.3) / T:.4f};1" '
            f'dur="{n(T)}s" repeatCount="indefinite"/></text>')
    out.append("</g>")

    roles = " · ".join(p["person"]["roles"])
    out.append(f'<text x="{W / 2}" y="210" font-size="15" fill="{C["a2"]}" text-anchor="middle" '
               f'textLength="{n(len(roles) * 9.4)}" lengthAdjust="spacing">{esc(roles)}</text>')

    # tagline + the ball that never stops
    tag = p["person"]["tagline"]
    tw = 340
    tx0 = W / 2 - tw / 2
    out.append(f'<text x="{n(tx0)}" y="262" font-size="26" font-weight="700" fill="{C["ink"]}" '
               f'textLength="{tw}" lengthAdjust="spacing">{esc(tag)}</text>')
    gy = 318
    out.append(f'<line x1="{n(tx0 - 20)}" y1="{gy + 6}" x2="{n(tx0 + tw + 20)}" y2="{gy + 6}" stroke="{C["line"]}"/>')
    tb = 7.0
    ys = physics.persistent_ball(900, 44, 0.78, 30, tb)
    out.append(
        f'<circle r="6" fill="{C["accent"]}" filter="url(#glow)">'
        f'<animate attributeName="cx" values="{n(tx0)};{n(tx0 + tw)}" dur="{n(tb)}s" repeatCount="indefinite"/>'
        f'<animate attributeName="cy" values="{";".join(n(gy + y) for y in ys)}" dur="{n(tb)}s" repeatCount="indefinite"/></circle>')

    # sigil: lissajous derived from sha256(profile.toml)
    a, b = 2 + sig[0] % 5, 3 + sig[1] % 6
    if a == b:
        b += 1
    pts = physics.lissajous(a, b, sig[2] / 255 * math.pi, 46)
    d = "M" + " L".join(f"{n(790 + x)} {n(262 + y)}" for x, y in pts)
    out.append(
        f'<path d="{d}" pathLength="1" fill="none" stroke="{C["accent"]}" stroke-width="1.4" stroke-linecap="round" '
        f'stroke-dasharray="1" stroke-dashoffset="1" filter="url(#glow)">'
        f'<animate attributeName="stroke-dashoffset" values="1;0;0;1" keyTimes="0;0.4;0.9;1" dur="{n(T)}s" repeatCount="indefinite"/></path>'
        f'<text x="790" y="332" font-size="9" fill="{C["muted"]}" text-anchor="middle">sigil {a}:{b} · {sig.hex()[:8]}</text>')

    out.append(f'<text x="40" y="338" font-size="12" fill="{C["muted"]}">“{esc(p["person"]["motto"])}”</text>')
    return document(W, H, f'{p["person"]["name"]} — {tag}',
                    "Name letters fall under simulated gravity with energy-losing bounces; a ball that relaunches "
                    "whenever it is about to settle runs beneath the tagline.",
                    "\n".join(out), GRID_DEFS + GLOW_DEFS)


# ═══ 2. TERMINAL ═════════════════════════════════════════════════════════════

def terminal(p: dict) -> str:
    W, CW, FS, LH = 900, 7.8, 13, 25
    lines = p["terminal"]
    H = 70 + len(lines) * LH + 40
    x0, y0 = 36, 88
    # timeline
    t = 0.6
    ev: list[dict] = []
    for ln in lines:
        txt = ln["text"]
        if ln["type"] == "cmd":
            full = "$ " + txt
            ev.append({"kind": "cmd", "text": full, "start": t, "step": 0.045})
            t += len(full) * 0.045 + 0.35
        else:
            ev.append({"kind": "out", "text": txt, "start": t})
            t += 0.55
    final_start = t
    T = t + 4.5
    out = [frame(W, H, grid=False)]
    out.append(f'<path d="M0 18a18 18 0 0 1 18-18H{W - 18}a18 18 0 0 1 18 18V44H0Z" fill="{C["panel"]}"/>'
               f'<circle cx="28" cy="22" r="6" fill="#ff5f56"/><circle cx="50" cy="22" r="6" fill="#ffbd2e"/><circle cx="72" cy="22" r="6" fill="#27c93f"/>'
               f'<text x="{W / 2}" y="26" font-size="12" fill="{C["muted"]}" text-anchor="middle">prasoon@forge: ~</text>')
    defs = []
    for i, e in enumerate(ev):
        y = y0 + i * LH
        if e["kind"] == "cmd":
            m = len(e["text"])
            s = e["start"]
            times = [0.0] + [(s + (k + 1) * e["step"]) / T for k in range(m)]
            times[1:] = [max(v, 0.0001 * (j + 1)) for j, v in enumerate(times[1:])]
            vals = ";".join(n(k * CW) for k in range(m + 1))
            defs.append(f'<clipPath id="c{i}"><rect x="{x0}" y="{y - 16}" height="22" width="0">'
                        f'<animate attributeName="width" calcMode="discrete" values="{vals}" keyTimes="{kt(times)}" dur="{n(T)}s" repeatCount="indefinite"/></rect></clipPath>')
            rest = e["text"][2:]
            out.append(f'<g clip-path="url(#c{i})"><text x="{x0}" y="{y}" font-size="{FS}" textLength="{n(2 * CW)}" lengthAdjust="spacing" fill="{C["accent"]}">$</text>'
                       f'<text x="{x0 + 2 * CW}" y="{y}" font-size="{FS}" textLength="{n(len(rest) * CW)}" lengthAdjust="spacing" fill="{C["ink"]}">{esc(rest)}</text></g>')
        else:
            ts = e["start"] / T
            out.append(f'<text x="{x0}" y="{y}" font-size="{FS}" fill="{C["a2"]}" opacity="0" textLength="{n(len(e["text"]) * CW)}" lengthAdjust="spacing">{esc(e["text"])}'
                       f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{ts:.4f};{ts + 0.012:.4f};1" dur="{n(T)}s" repeatCount="indefinite"/></text>')
    # live cursor: one block that hops to wherever typing happens
    cur_x, cur_y, cur_t = [], [], []
    for i, e in enumerate(ev):
        if e["kind"] != "cmd":
            continue
        for k in range(len(e["text"]) + 1):
            cur_t.append((e["start"] + k * e["step"]) / T)
            cur_x.append(x0 + k * CW)
            cur_y.append(y0 + i * LH - 13)
    fy = y0 + len(ev) * LH
    cur_t.append(final_start / T)
    cur_x.append(x0 + 2 * CW)
    cur_y.append(fy - 13)
    out.append(f'<text x="{x0}" y="{fy}" font-size="{FS}" fill="{C["accent"]}" opacity="0">$'
               f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{final_start / T:.4f};{final_start / T + 0.01:.4f};1" dur="{n(T)}s" repeatCount="indefinite"/></text>')
    cur_t[0] = 0.0
    seen = 0.0
    for j in range(len(cur_t)):  # enforce strictly increasing keyTimes
        cur_t[j] = max(cur_t[j], seen + 1e-5)
        seen = cur_t[j]
    cur_t[0] = 0.0
    out.append(
        f'<rect width="{CW}" height="16" fill="{C["accent"]}" opacity=".9">'
        f'<animate attributeName="x" calcMode="discrete" values="{";".join(n(v) for v in cur_x)}" keyTimes="{kt(cur_t)}" dur="{n(T)}s" repeatCount="indefinite"/>'
        f'<animate attributeName="y" calcMode="discrete" values="{";".join(n(v) for v in cur_y)}" keyTimes="{kt(cur_t)}" dur="{n(T)}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5001;1" dur="1s" repeatCount="indefinite" additive="replace"/></rect>')
    return document(W, H, "Terminal — whoami", "A terminal session that types out who Prasoon is.",
                    "\n".join(out), "".join(defs))


# ═══ 3. ORBIT (Kepler) ═══════════════════════════════════════════════════════

def orbit(p: dict) -> str:
    W, H = 900, 580
    cx, cy = 560, 290
    rings = p["ring"]
    r0, dr, t0 = 62.0, 38.0, 9.0
    out = [frame(W, H)]
    out.append(f'<text x="36" y="46" font-size="13" fill="{C["accent"]}" letter-spacing="2">// SKILL ORBIT</text>'
               f'<text x="36" y="66" font-size="10.5" fill="{C["muted"]}">period ∝ radius^1.5 (Kepler III)</text>')
    for k, ring in enumerate(rings):
        r = r0 + k * dr
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{n(r)}" fill="none" stroke="{col(ring["color"])}" stroke-opacity=".22" stroke-dasharray="2 6"/>')
        ly = 110 + k * 26
        out.append(f'<circle cx="42" cy="{ly - 4}" r="4" fill="{col(ring["color"])}"/>'
                   f'<text x="54" y="{ly}" font-size="11" fill="{C["ink"]}" letter-spacing="1.5">{esc(ring["name"])}</text>'
                   f'<text x="154" y="{ly}" font-size="10" fill="{C["muted"]}">T={n(physics.kepler_period(r, r0, t0))}s</text>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="26" fill="{C["accent"]}" fill-opacity=".1" stroke="{C["accent"]}" filter="url(#glow2)">'
               f'<animate attributeName="r" values="24;29;24" dur="3s" repeatCount="indefinite"/></circle>'
               f'<text x="{cx}" y="{cy + 5}" font-size="15" font-weight="800" fill="{C["accent"]}" text-anchor="middle">PM</text>')
    for k, ring in enumerate(rings):
        r = r0 + k * dr
        per = physics.kepler_period(r, r0, t0)
        sk = ring["skills"]
        phase = (k * 47) % 360
        for j, s in enumerate(sk):
            a0 = phase + j * 360 / len(sk)
            c = col(ring["color"])
            pr = 6.5 if s.get("primary") else 4.5
            glow = ' filter="url(#glow)"' if s.get("primary") else ""
            wt = "700" if s.get("primary") else "400"
            out.append(
                f'<g><animateTransform attributeName="transform" type="rotate" from="{n(a0)} {cx} {cy}" to="{n(a0 + 360)} {cx} {cy}" dur="{n(per)}s" repeatCount="indefinite"/>'
                f'<g transform="translate({n(cx + r)} {cy})"><circle r="{pr}" fill="{c}"{glow}/>'
                f'<g><animateTransform attributeName="transform" type="rotate" from="{n(-a0)}" to="{n(-a0 - 360)}" dur="{n(per)}s" repeatCount="indefinite"/>'
                f'<text y="{n(pr + 12)}" font-size="10.5" font-weight="{wt}" text-anchor="middle" fill="{C["ink"]}" '
                f'stroke="{C["bg"]}" stroke-width="3" paint-order="stroke">{esc(s["name"])}</text></g></g></g>')
    out.append(f'<text x="{W - 36}" y="{H - 24}" font-size="10" fill="{C["muted"]}" text-anchor="end">bold = daily drivers</text>')
    return document(W, H, "Skill orbit",
                    "Skills orbit a core. Outer rings orbit slower, following Kepler's third law.",
                    "\n".join(out), GRID_DEFS + GLOW_DEFS)


# ═══ 4. PROJECT × STACK GRAPH ════════════════════════════════════════════════

_TAG_COLOR = {"AI": "pink", "Gemini": "pink", "LightGBM": "pink", "Agentic AI": "pink",
              "Python": "a2", "JavaScript": "a2", "HTML": "a2"}


def graph(p: dict) -> str:
    W, H = 900, 470
    projs = p["project"]
    tags: list[str] = []
    for pr in projs:
        for t in pr["tags"]:
            if t not in tags:
                tags.append(t)
    names = [pr["name"] for pr in projs] + tags
    edges = [(i, len(projs) + tags.index(t)) for i, pr in enumerate(projs) for t in pr["tags"]]
    deg = [0] * len(names)
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    rng = physics.seeded(11)
    pos = [[W / 2 + 160 * math.cos(2 * math.pi * i / len(names)) + rng.uniform(-8, 8),
            H / 2 + 120 * math.sin(2 * math.pi * i / len(names)) + rng.uniform(-8, 8)] for i in range(len(names))]
    physics.force_layout(pos, edges, W, H, iters=700, min_dist=64)
    xs, ys = [q[0] for q in pos], [q[1] for q in pos]
    sx = (W - 190) / max(max(xs) - min(xs), 1)
    sy = (H - 150) / max(max(ys) - min(ys), 1)
    pos = [[95 + (q[0] - min(xs)) * sx, 90 + (q[1] - min(ys)) * sy] for q in pos]

    out = [frame(W, H)]
    out.append(f'<text x="36" y="46" font-size="13" fill="{C["accent"]}" letter-spacing="2">// PROJECT × STACK</text>'
               f'<text x="36" y="66" font-size="10.5" fill="{C["muted"]}">Fruchterman–Reingold layout, solved at build time. Shared tech pulls projects together.</text>')
    for k, (u, v) in enumerate(edges):
        out.append(f'<line x1="{n(pos[u][0])}" y1="{n(pos[u][1])}" x2="{n(pos[v][0])}" y2="{n(pos[v][1])}" stroke="{C["accent"]}" '
                   f'stroke-opacity=".35" stroke-dasharray="3 7"><animate attributeName="stroke-dashoffset" values="0;-20" '
                   f'dur="{n(1.2 + (k % 5) * 0.25)}s" repeatCount="indefinite"/></line>')
    for i, nm in enumerate(names):
        x, y = pos[i]
        if i < len(projs):
            feat = projs[i].get("featured")
            r = 24 if feat else 17
            out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{r}" fill="{C["accent"]}" fill-opacity=".12" stroke="{C["accent"]}" filter="url(#glow)">'
                       f'<animate attributeName="r" values="{r};{r + 3};{r}" dur="{n(2.6 + i * 0.4)}s" repeatCount="indefinite"/></circle>'
                       f'<text x="{n(x)}" y="{n(y + 4)}" font-size="11" font-weight="800" fill="{C["accent"]}" text-anchor="middle">{esc(nm[:2].upper())}</text>'
                       f'<text x="{n(x)}" y="{n(y + r + 16)}" font-size="12" font-weight="700" fill="{C["ink"]}" text-anchor="middle" '
                       f'stroke="{C["bg"]}" stroke-width="3" paint-order="stroke">{esc(nm)}</text>')
        else:
            c = col(_TAG_COLOR.get(nm, "warm"))
            r = 4 + deg[i] * 1.6
            out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{c}"/>'
                       f'<text x="{n(x)}" y="{n(y + r + 13)}" font-size="10.5" fill="{C["ink"]}" text-anchor="middle" '
                       f'stroke="{C["bg"]}" stroke-width="3" paint-order="stroke">{esc(nm)}</text>')
    return document(W, H, "Project × stack graph",
                    "A force-directed graph linking each project to the technologies it uses.",
                    "\n".join(out), GRID_DEFS + GLOW_DEFS)


# ═══ 5. SIGNAL TICKER ════════════════════════════════════════════════════════

def signals(p: dict) -> str:
    W, H, CWID, GAP = 900, 96, 310, 14
    sg = p["signal"]
    total = len(sg) * (CWID + GAP)
    dur = total / 55.0  # 55 px/s
    out = [frame(W, H, grid=False), '<g clip-path="url(#tk)">']
    cards = []
    for rep in range(2):
        for i, s in enumerate(sg):
            x = rep * total + i * (CWID + GAP)
            c = col(["accent", "a2", "violet", "pink", "warm", "teal", "accent"][i % 7])
            cards.append(f'<g transform="translate({x} 18)"><rect width="{CWID}" height="60" rx="10" fill="{C["panel"]}" stroke="{c}" stroke-opacity=".45"/>'
                         f'<rect x="0" y="12" width="3" height="36" rx="1.5" fill="{c}"/>'
                         f'<text x="18" y="27" font-size="12.5" font-weight="700" fill="{C["ink"]}">{esc(s["title"])}</text>'
                         f'<text x="18" y="46" font-size="10.5" fill="{C["muted"]}">{esc(s["detail"])}</text></g>')
    out.append(f'<g>{"".join(cards)}<animateTransform attributeName="transform" type="translate" from="0 0" to="{-total} 0" dur="{n(dur)}s" repeatCount="indefinite"/></g></g>')
    out.append(f'<rect width="60" height="{H}" rx="18" fill="url(#fl)"/><rect x="{W - 60}" width="60" height="{H}" rx="18" fill="url(#fr)"/>')
    defs = (f'<clipPath id="tk"><rect width="{W}" height="{H}" rx="18"/></clipPath>'
            f'<linearGradient id="fl"><stop offset="0" stop-color="{C["bg"]}"/><stop offset="1" stop-color="{C["bg"]}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="fr"><stop offset="0" stop-color="{C["bg"]}" stop-opacity="0"/><stop offset="1" stop-color="{C["bg"]}"/></linearGradient>')
    return document(W, H, "Proof ticker", "Hackathons, ambassador roles and certifications, scrolling.", "\n".join(out), defs)


# ═══ 6. TELEMETRY (sun over Lucknow · moon · build stamp) ════════════════════

def telemetry(p: dict, now: datetime, sig: bytes, drift: float, stats: dict) -> str:
    W, H = 900, 190
    lat, lon = astro.LUCKNOW
    local = now.astimezone(astro.IST)
    curve = astro.day_curve(now, lat, lon)
    el = astro.sun_elevation(now, lat, lon)
    rise, sset = astro.sun_times(curve)
    age = astro.moon_age(now)
    ill = astro.moon_illumination(age)

    out = [frame(W, H)]
    out.append(f'<text x="36" y="38" font-size="13" fill="{C["accent"]}" letter-spacing="2">// TELEMETRY</text>')
    # sun plot
    px0, px1, hy, k = 36, 470, 136, 0.9
    ptsd = "M" + " L".join(f"{n(px0 + h / 24 * (px1 - px0))} {n(hy - e * k)}" for h, e in curve)
    out.append(f'<clipPath id="sunclip"><rect x="{px0}" y="72" width="{px1 - px0}" height="{hy + 30 - 72}"/></clipPath>'
               f'<rect x="{px0}" y="{hy}" width="{px1 - px0}" height="30" fill="#000" opacity=".35"/>'
               f'<line x1="{px0}" y1="{hy}" x2="{px1}" y2="{hy}" stroke="{C["line"]}"/>'
               f'<path d="{ptsd}" fill="none" stroke="{C["warm"]}" stroke-width="1.6" stroke-opacity=".8" clip-path="url(#sunclip)"/>')
    hnow = local.hour + local.minute / 60
    sx, sy = px0 + hnow / 24 * (px1 - px0), hy - el * k
    out.append(f'<circle cx="{n(sx)}" cy="{n(min(sy, hy + 22))}" r="6" fill="{C["warm"] if el > 0 else C["muted"]}" filter="url(#glow)"/>')
    for h in (0, 6, 12, 18, 24):
        x = px0 + h / 24 * (px1 - px0)
        out.append(f'<text x="{n(x)}" y="{hy + 24}" font-size="9" fill="{C["muted"]}" text-anchor="{"start" if h == 0 else "end" if h == 24 else "middle"}">{h:02d}h</text>')
    out.append(f'<text x="{px0}" y="62" font-size="11" fill="{C["ink"]}">LUCKNOW · sun {el:+.1f}° · rise {astro.hm(rise)} · set {astro.hm(sset)} IST</text>')

    # moon
    mx, my, mr = 560, 98, 34
    r2 = mr * abs(math.cos(2 * math.pi * age))
    waxing = age < 0.5
    if waxing:
        term_sweep = 0 if age < 0.25 else 1
        lit = f"M{mx} {my - mr}A{mr} {mr} 0 0 1 {mx} {my + mr}A{n(r2)} {mr} 0 0 {term_sweep} {mx} {my - mr}Z"
    else:
        term_sweep = 1 if age > 0.75 else 0
        lit = f"M{mx} {my - mr}A{mr} {mr} 0 0 0 {mx} {my + mr}A{n(r2)} {mr} 0 0 {term_sweep} {mx} {my - mr}Z"
    out.append(f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="#1a2330" stroke="{C["line"]}"/>'
               f'<path d="{lit}" fill="#e8eef5" filter="url(#glow)"/>'
               f'<text x="{mx}" y="{my + mr + 22}" font-size="10.5" fill="{C["ink"]}" text-anchor="middle">{astro.moon_name(age)} · {ill * 100:.0f}%</text>')

    # build stamp
    bx = 650
    rows = [("build", sig.hex()[:12]), ("rk4 ΔE/E", f"{drift:.1e}"), ("scenes", str(stats.get("scenes", 0))),
            ("svg bytes", f'{stats.get("bytes", 0) / 1024:.0f} KB'), ("built", local.strftime("%d %b %H:%M IST"))]
    for i, (a, b) in enumerate(rows):
        y = 70 + i * 22
        out.append(f'<text x="{bx}" y="{y}" font-size="11" fill="{C["muted"]}">{a}</text>'
                   f'<text x="{W - 36}" y="{y}" font-size="11" fill="{C["ink"]}" text-anchor="end">{esc(b)}</text>')
    return document(W, H, "Telemetry",
                    "Solar elevation over Lucknow, moon phase, and the build stamp, all computed at build time.",
                    "\n".join(out), GRID_DEFS + GLOW_DEFS)


# ═══ 7. CHAOS (two double pendulums, Δθ₀ = 1e-3) ═════════════════════════════

def chaos(p: dict) -> tuple[str, float]:
    W, H, T, FPS = 900, 340, 18.0, 24
    px, py, L = 450, 168, 72
    kk = 9.81
    fa, da = physics.double_pendulum(2.1, 2.5, kk, T, FPS)
    fb, db = physics.double_pendulum(2.1, 2.501, kk, T, FPS)
    drift = max(da, db)
    out = [frame(W, H)]
    out.append(f'<text x="36" y="42" font-size="13" fill="{C["accent"]}" letter-spacing="2">// SMALL DELTAS COMPOUND</text>'
               f'<text x="36" y="62" font-size="10.5" fill="{C["muted"]}">Two double pendulums, RK4. Initial angles differ by 0.001 rad.</text>')
    for fr, c in ((fa, "accent"), (fb, "pink")):
        path = "M" + " L".join(f"{n(px + f[2] * L)} {n(py + f[3] * L)}" for f in fr)
        out.append(f'<path d="{path}" fill="none" stroke="{col(c)}" stroke-opacity=".16" stroke-width="1"/>')
    for fr, c in ((fa, "accent"), (fb, "pink")):
        cc = col(c)
        xs1 = ";".join(n(px + f[0] * L) for f in fr)
        ys1 = ";".join(n(py + f[1] * L) for f in fr)
        xs2 = ";".join(n(px + f[2] * L) for f in fr)
        ys2 = ";".join(n(py + f[3] * L) for f in fr)
        d = f'dur="{n(T)}s" repeatCount="indefinite"'
        for g in range(7, 0, -1):  # ghost trail: same keyframes, negative delay
            out.append(f'<circle r="{n(4.2 - g * 0.3)}" fill="{cc}" opacity="{n(0.4 - g * 0.05)}">'
                       f'<animate attributeName="cx" values="{xs2}" begin="-{n(g * 0.07)}s" {d}/>'
                       f'<animate attributeName="cy" values="{ys2}" begin="-{n(g * 0.07)}s" {d}/></circle>')
        out.append(f'<line x1="{px}" y1="{py}" stroke="{cc}" stroke-opacity=".5"><animate attributeName="x2" values="{xs1}" {d}/>'
                   f'<animate attributeName="y2" values="{ys1}" {d}/></line>'
                   f'<line stroke="{cc}" stroke-opacity=".5"><animate attributeName="x1" values="{xs1}" {d}/><animate attributeName="y1" values="{ys1}" {d}/>'
                   f'<animate attributeName="x2" values="{xs2}" {d}/><animate attributeName="y2" values="{ys2}" {d}/></line>'
                   f'<circle r="4" fill="{cc}"><animate attributeName="cx" values="{xs1}" {d}/><animate attributeName="cy" values="{ys1}" {d}/></circle>'
                   f'<circle r="6" fill="{cc}" filter="url(#glow)"><animate attributeName="cx" values="{xs2}" {d}/><animate attributeName="cy" values="{ys2}" {d}/></circle>')
    out.append(f'<circle cx="{px}" cy="{py}" r="4" fill="{C["ink"]}"/>')
    out.append(f'<text x="{W - 36}" y="{H - 22}" font-size="11" fill="{C["muted"]}" text-anchor="end">'
               f'tiny daily effort → very different futures · energy drift {drift:.1e}</text>')
    return document(W, H, "Chaos — small deltas compound",
                    "Two double pendulums with a 0.001 rad difference diverge, simulated with RK4.",
                    "\n".join(out), GRID_DEFS + GLOW_DEFS), drift


def sha(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()
