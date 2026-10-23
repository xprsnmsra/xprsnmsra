#!/usr/bin/env python3
"""Fills README.tpl.md with computed modules. Run after generate.py."""
import sys, json, hashlib, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import lorenz, life, maze, vm, knot, diagrams

USER = "iprsnmsra"
now = datetime.datetime.now(datetime.timezone.utc)
seed = f"{USER}:{now:%Y-%m-%d}"
state = ROOT / "engine" / "state"; state.mkdir(exist_ok=True)

meta_p = state / "meta.json"
meta = json.loads(meta_p.read_text()) if meta_p.exists() else {"born": f"{now:%Y-%m-%d}", "builds": 0}
meta["builds"] += 1; meta_p.write_text(json.dumps(meta))
age = (now.date() - datetime.date.fromisoformat(meta["born"])).days

art, lam, T = lorenz.run(seed)
lf, gen, pop, rs = life.advance(state / "life.json", USER)
mz, ms = maze.run(seed)
code = vm.run(seed)
stl, tris = knot.stl()
(ROOT / "assets" / "trefoil.stl").write_text(stl)

mods = [("lorenz", "Lorenz · RK4 chaos"), ("life", "Game of Life · persistent"), ("maze", "Maze agent · retries"),
        ("vm", "Compiler + VM"), ("knot", "STL 3D mesh")]
fill = {
  "STATUS": f"build {hashlib.sha256(seed.encode()).hexdigest()[:7]} · rebuilt {meta['builds']}× · alive {age} days · {now:%Y-%m-%d %H:%M} UTC",
  "LORENZ": art, "LAMBDA": f"{lam:.2f}", "TSPAN": f"{T:.0f}", "SEED": seed,
  "LIFE": lf, "GEN": str(gen), "POP": str(pop), "RESEEDS": str(rs),
  "MAZE": mz, "STEPS": str(ms["steps"]), "BACK": str(ms["back"]), "OPT": str(ms["opt"]), "WASTE": str(ms["steps"] - ms["opt"]),
  "VM": code, "KNOT": stl, "TRIS": str(tris),
  "PIPELINE": diagrams.pipeline(mods), "NGU": diagrams.never_give_up(), "SKILLS": diagrams.skills(),
}
tpl = (ROOT / "README.tpl.md").read_text(encoding="utf-8")
for k, v in fill.items(): tpl = tpl.replace("{{" + k + "}}", v)
(ROOT / "README.md").write_text(tpl, encoding="utf-8")
print(f"README.md {len(tpl.encode())/1024:.0f} KiB (GitHub limit 500 KiB) · life gen {gen} pop {pop} · λ={lam:.3f}")
