"""Conway's Game of Life on a torus. State persists in the repo and evolves every rebuild."""
import json, random, hashlib, pathlib
W, H, GENS = 60, 14, 30

def step(g):
    n = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            c = sum(g[(y + dy) % H][(x + dx) % W] for dy in (-1, 0, 1) for dx in (-1, 0, 1)) - g[y][x]
            n[y][x] = 1 if c == 3 or (g[y][x] and c == 2) else 0
    return n

def seeded(seed):
    r = random.Random(seed)
    return [[1 if r.random() < 0.27 else 0 for _ in range(W)] for _ in range(H)]

def advance(path, seed):
    p = pathlib.Path(path)
    st = json.loads(p.read_text()) if p.exists() else {"gen": 0, "reseeds": 0, "cells": seeded(seed), "hist": []}
    g, hist = st["cells"], st["hist"]
    for _ in range(GENS):
        g = step(g); st["gen"] += 1
        key = hashlib.md5(str(g).encode()).hexdigest()[:8]
        if not any(map(any, g)) or key in hist:              # extinct or stuck in a cycle -> new universe
            st["reseeds"] += 1; g = seeded(f"{seed}:{st['gen']}"); hist = []
        hist = (hist + [key])[-12:]
    st["cells"], st["hist"] = g, hist
    p.write_text(json.dumps(st))
    art = "\n".join("".join("█" if c else "·" for c in row) for row in g)
    return art, st["gen"], sum(map(sum, g)), st["reseeds"]
