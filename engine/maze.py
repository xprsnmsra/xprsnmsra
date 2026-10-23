"""A persistence agent: a daily maze, an explorer that hits dead ends and retries, BFS as the benchmark."""
import random
from collections import deque
CW, CH = 24, 9

def run(seed):
    r = random.Random(seed)
    W, H = 2 * CW + 1, 2 * CH + 1
    m = [["#"] * W for _ in range(H)]
    st = [(1, 1)]; m[1][1] = " "
    while st:                                                # randomized DFS carve
        x, y = st[-1]
        nb = [(x + dx, y + dy, dx, dy) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))
              if 0 < x + dx < W - 1 and 0 < y + dy < H - 1 and m[y + dy][x + dx] == "#"]
        if not nb: st.pop(); continue
        nx, ny, dx, dy = r.choice(nb)
        m[y + dy // 2][x + dx // 2] = m[ny][nx] = " "; st.append((nx, ny))
    goal = (W - 2, H - 2)
    seen, path, dead, steps, back = {(1, 1)}, [(1, 1)], set(), 0, 0
    while path[-1] != goal:                                  # the agent: explore, fail, backtrack, retry
        x, y = path[-1]; steps += 1
        nxt = [(x + dx, y + dy) for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1))
               if m[y + dy][x + dx] == " " and (x + dx, y + dy) not in seen]
        if nxt:
            c = r.choice(nxt); seen.add(c); path.append(c)
        else:
            dead.add(path.pop()); back += 1
    q, par = deque([(1, 1)]), {(1, 1): None}                  # BFS = optimal benchmark
    while q:
        c = q.popleft()
        if c == goal: break
        for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if m[n[1]][n[0]] == " " and n not in par: par[n] = c; q.append(n)
    opt, c = 0, goal
    while par[c]: opt += 1; c = par[c]
    route = set(path)
    rows = []
    for y in range(H):
        rows.append("".join("S" if (x, y) == (1, 1) else "E" if (x, y) == goal else
                            "█" if m[y][x] == "#" else "•" if (x, y) in route else "·" if (x, y) in dead else " "
                            for x in range(W)))
    return "\n".join(rows), dict(steps=steps, back=back, route=len(path) - 1, opt=opt)
