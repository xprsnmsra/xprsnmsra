"""Physics and geometry, stdlib only. Every function is deterministic.

Simulations run offline at build time; the scenes bake the results into SMIL
keyframes, so GitHub's static image proxy plays real physics with zero JS.
"""
from __future__ import annotations

import math
import random

_SIM_HZ = 960  # integrator rate for the ballistic sims; divisible by 20/24/30/40/60 fps


def _stride(fps: int) -> int:
    return max(1, _SIM_HZ // fps)


# ── 1. Ballistic motion with inelastic floor collisions ─────────────────────


def drop(t0: float, h: float, g: float, e: float, fps: int, total: float) -> list[float]:
    """Vertical offset (px, negative = above the floor) of a body released at t0.

    Starts `h` px above the floor, falls under gravity `g` (px/s²), loses energy
    with restitution `e` at each floor hit, stops when the next apex < 0.4 px.
    Semi-implicit Euler at 960 Hz, sampled at `fps`.
    """
    dt = 1.0 / _SIM_HZ
    n = int(round(total * fps)) + 1
    stride = _stride(fps)
    v_rest = math.sqrt(2.0 * g * 0.4)
    y, v = -h, 0.0
    released = resting = False
    out: list[float] = []
    for i in range(n * stride):
        if i % stride == 0:
            out.append(y)
        if not released and i * dt >= t0:
            released = True
        if released and not resting:
            v += g * dt
            y += v * dt
            if y >= 0.0:
                y, v = 0.0, -v * e
                if abs(v) < v_rest:
                    v, resting = 0.0, True
    return out


def persistent_ball(g: float, h: float, e: float, fps: int, total: float,
                    give_up_below: float = 3.0) -> list[float]:
    """A ball that refuses to settle: whenever its next apex would fall below
    `give_up_below` px it is relaunched to height `h`. Offsets are ≤ 0 (up)."""
    dt = 1.0 / _SIM_HZ
    n = int(round(total * fps)) + 1
    stride = _stride(fps)
    v_launch = -math.sqrt(2.0 * g * h)
    y, v = 0.0, v_launch
    out: list[float] = []
    for i in range(n * stride):
        if i % stride == 0:
            out.append(y)
        v += g * dt
        y += v * dt
        if y >= 0.0:
            y, v = 0.0, -v * e
            if v * v / (2.0 * g) < give_up_below:
                v = v_launch
    return out


# ── 2. Double pendulum, RK4 ─────────────────────────────────────────────────

State = tuple[float, float, float, float]


def _deriv(s: State, k: float) -> State:
    """Equal masses and lengths, k = g/L. Standard Lagrangian derivation."""
    t1, w1, t2, w2 = s
    d = t1 - t2
    den = 3.0 - math.cos(2.0 * d)
    a1 = (-3.0 * k * math.sin(t1) - k * math.sin(t1 - 2.0 * t2)
          - 2.0 * math.sin(d) * (w2 * w2 + w1 * w1 * math.cos(d))) / den
    a2 = (2.0 * math.sin(d) * (2.0 * w1 * w1 + 2.0 * k * math.cos(t1)
                               + w2 * w2 * math.cos(d))) / den
    return (w1, a1, w2, a2)


def _axpy(s: State, d: State, h: float) -> State:
    return (s[0] + h * d[0], s[1] + h * d[1], s[2] + h * d[2], s[3] + h * d[3])


def pendulum_energy(s: State, k: float) -> float:
    """Total energy / (m·L²) for the equal-mass double pendulum."""
    t1, w1, t2, w2 = s
    kin = w1 * w1 + 0.5 * w2 * w2 + w1 * w2 * math.cos(t1 - t2)
    pot = -2.0 * k * math.cos(t1) - k * math.cos(t2)
    return kin + pot


def double_pendulum(th1: float, th2: float, k: float, total: float, fps: int,
                    dt: float = 0.002) -> tuple[list[tuple[float, float, float, float]], float]:
    """Integrate with classic RK4. Returns (frames, max relative energy drift).

    A frame is (x1, y1, x2, y2) in unit-length coordinates, y pointing down.
    """
    s: State = (th1, 0.0, th2, 0.0)
    e0 = pendulum_energy(s, k)
    steps = int(round(total / dt))
    stride = max(1, int(round(1.0 / (fps * dt))))
    frames: list[tuple[float, float, float, float]] = []
    drift = 0.0
    for i in range(steps + 1):
        if i % stride == 0:
            x1, y1 = math.sin(s[0]), math.cos(s[0])
            frames.append((x1, y1, x1 + math.sin(s[2]), y1 + math.cos(s[2])))
        k1 = _deriv(s, k)
        k2 = _deriv(_axpy(s, k1, dt / 2), k)
        k3 = _deriv(_axpy(s, k2, dt / 2), k)
        k4 = _deriv(_axpy(s, k3, dt), k)
        s = (s[0] + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]),
             s[1] + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]),
             s[2] + dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]),
             s[3] + dt / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3]))
        if i % 25 == 0:
            drift = max(drift, abs(pendulum_energy(s, k) - e0) / abs(e0))
    return frames, drift


# ── 3. Kepler's third law ───────────────────────────────────────────────────


def kepler_period(a: float, a0: float, t0: float) -> float:
    """Orbital period at semi-major axis `a`, given period `t0` at `a0` (T ∝ a^1.5)."""
    return t0 * (a / a0) ** 1.5


# ── 4. Fruchterman–Reingold force-directed layout ───────────────────────────


def force_layout(pos: list[list[float]], edges: list[tuple[int, int]], w: float, h: float,
                 iters: int = 600, min_dist: float = 70.0) -> list[list[float]]:
    """Spring-embedder layout in [0,w]×[0,h] with a collision shell. Mutates `pos`."""
    n = len(pos)
    k = 0.85 * math.sqrt(w * h / max(n, 1))
    temp = w / 6.0
    cx, cy = w / 2.0, h / 2.0
    for it in range(iters):
        disp = [[0.0, 0.0] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                dx, dy = pos[i][0] - pos[j][0], pos[i][1] - pos[j][1]
                d = max(math.hypot(dx, dy), 0.01)
                f = k * k / d
                if d < min_dist:
                    f += (min_dist - d) * 6.0
                ux, uy = dx / d, dy / d
                disp[i][0] += ux * f
                disp[i][1] += uy * f
                disp[j][0] -= ux * f
                disp[j][1] -= uy * f
        for u, v in edges:
            dx, dy = pos[u][0] - pos[v][0], pos[u][1] - pos[v][1]
            d = max(math.hypot(dx, dy), 0.01)
            f = d * d / k
            ux, uy = dx / d, dy / d
            disp[u][0] -= ux * f
            disp[u][1] -= uy * f
            disp[v][0] += ux * f
            disp[v][1] += uy * f
        for i in range(n):
            disp[i][0] += (cx - pos[i][0]) * 0.9
            disp[i][1] += (cy - pos[i][1]) * 0.9
            mag = max(math.hypot(*disp[i]), 0.01)
            step = min(mag, temp)
            pos[i][0] = min(w, max(0.0, pos[i][0] + disp[i][0] / mag * step))
            pos[i][1] = min(h, max(0.0, pos[i][1] + disp[i][1] / mag * step))
        temp *= 0.985 if it > iters * 0.3 else 0.998
    return pos


def seeded(seed: int) -> random.Random:
    return random.Random(seed)


# ── 5. Lissajous sigil ──────────────────────────────────────────────────────


def lissajous(a: int, b: int, phase: float, r: float, samples: int = 600) -> list[tuple[float, float]]:
    return [(r * math.sin(a * t + phase), r * math.sin(b * t))
            for t in (2.0 * math.pi * i / samples for i in range(samples + 1))]
