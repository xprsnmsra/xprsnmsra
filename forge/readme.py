"""README.md template. Prose is deliberately tiny; the scenes carry the weight."""
from __future__ import annotations


def render(p: dict, cache: dict, digest: str) -> str:
    L = p["links"]
    rows = []
    for pr in p["project"]:
        if not pr.get("featured"):
            continue
        c = cache.get(pr.get("repo", ""), {})
        meta = " · ".join(x for x in (f'★ {c["stars"]}' if "stars" in c else "", c.get("language") or "") if x)
        name = f'**[{pr["name"]}](https://github.com/{pr["repo"]})**'
        live = f' · [live]({pr["demo"]})' if pr.get("demo") else ""
        rows.append(f'| {name}{live} | {pr["blurb"]} | {meta or "—"} |')
    table = "| Project | What it does | Live |\n|:--|:--|:--|\n" + "\n".join(rows)

    return f"""<div align="center">

<img src="assets/hero.svg" alt="Prasoon Mishra: I never give up" width="100%"/>

<a href="{L["portfolio"]}">Portfolio</a> &nbsp;·&nbsp;
<a href="{L["linkedin"]}">LinkedIn</a> &nbsp;·&nbsp;
<a href="mailto:{L["email"]}">Email</a> &nbsp;·&nbsp;
<a href="{L["leetcode"]}">LeetCode</a>

<img src="assets/terminal.svg" alt="Terminal session: who Prasoon is" width="100%"/>

<img src="assets/orbit.svg" alt="Skill orbit" width="100%"/>

<img src="assets/graph.svg" alt="Project and stack graph" width="100%"/>

</div>

{table}

<div align="center">

<img src="assets/signals.svg" alt="Hackathons, ambassador roles, certifications" width="100%"/>

<img src="assets/telemetry.svg" alt="Telemetry: sun over Lucknow, moon phase, build stamp" width="100%"/>

<img src="assets/chaos.svg" alt="Two double pendulums diverging from a tiny difference" width="100%"/>

</div>

<details>
<summary><b>How this README is built</b></summary>

<br/>

Nothing here is a screenshot or an embedded widget. `data/profile.toml` is compiled by [`forge/`](forge) (Python, standard library only) into the SVG scenes above:

- **Physics is simulated at build time.** Letters fall with real ballistic bounces, the pendulums use RK4 (energy drift is printed in the telemetry strip), skill orbit periods follow Kepler's third law.
- **The project graph is solved**, not drawn: Fruchterman–Reingold force layout over project × technology edges.
- **The sigil in the hero is a Lissajous curve derived from `sha256(profile.toml)`**, so it changes when the profile changes.
- **The sun and moon are computed** (NOAA solar-position algorithm, synodic moon phase) for Lucknow at build time.
- A [GitHub Action](.github/workflows/build.yml) rebuilds every 6 hours, pulls live repo stats, validates every SVG, and commits only when something changed.

```bash
python -m forge build     # regenerate everything
python -m forge verify    # lint SVGs + check the build is deterministic
python -m unittest        # physics and astronomy tests
```

</details>

<sub>profile hash `{digest[:12]}`</sub>
"""
