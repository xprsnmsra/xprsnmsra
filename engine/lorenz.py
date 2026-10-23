"""Chaos: Lorenz attractor (RK4) drawn in braille + Benettin Lyapunov exponent. Re-seeded daily."""
import hashlib, math
S, R, B = 10.0, 28.0, 8 / 3
BIT = [[0x01, 0x02, 0x04, 0x40], [0x08, 0x10, 0x20, 0x80]]

def d(v):
    x, y, z = v
    return (S * (y - x), x * (R - z) - y, x * y - B * z)

def rk4(v, h):
    k1 = d(v)
    k2 = d([v[i] + h / 2 * k1[i] for i in range(3)])
    k3 = d([v[i] + h / 2 * k2[i] for i in range(3)])
    k4 = d([v[i] + h * k3[i] for i in range(3)])
    return [v[i] + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(3)]

def run(seed, W=70, Hc=20, steps=14000, h=0.005):
    g = hashlib.sha256(seed.encode()).digest()
    v = [1 + (g[i] - 128) / 256 for i in range(3)]
    for _ in range(1000): v = rk4(v, h)                      # burn-in onto the attractor
    d0 = 1e-9
    w = [v[0] + d0, v[1], v[2]]
    acc, n = 0.0, 0
    grid = [[0] * W for _ in range(Hc)]
    for s in range(steps):
        v, w = rk4(v, h), rk4(w, h)
        if s % 20 == 19:                                     # Benettin renormalisation
            dist = math.dist(v, w)
            acc += math.log(dist / d0); n += 1
            w = [v[i] + (w[i] - v[i]) * d0 / dist for i in range(3)]
        if s > 4200: continue                                # draw only a short stretch so the lobes stay visible
        px = int((v[0] + 22) / 44 * (W * 2 - 1)); py = int((50 - v[2]) / 50 * (Hc * 4 - 1))
        if 0 <= px < W * 2 and 0 <= py < Hc * 4:
            grid[py // 4][px // 2] |= BIT[px % 2][py % 4]
    art = "\n".join("".join(chr(0x2800 + m) for m in row) for row in grid)
    lam = acc / (n * 20 * h)
    return art, lam, steps * h
