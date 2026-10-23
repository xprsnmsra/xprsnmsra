"""Mermaid diagrams (rendered natively by GitHub), generated from live data."""
def pipeline(modules):
    L = ["flowchart LR", "  cron([\"⏰ cron · 04:00 UTC\"]) --> gen[\"generate.py<br/>SVG physics\"]",
         "  cron --> eng[\"engine/build.py\"]"]
    for m, label in modules: L.append(f"  eng --> {m}[\"{label}\"]")
    L += ["  gen --> out", "  " + " & ".join(m for m, _ in modules) + " --> out[(README.md)]",
          "  out --> git[\"git commit\"] --> web([\"github.com/you\"])", "  web -. visitor .-> out"]
    return "\n".join(L)

def never_give_up():
    return """stateDiagram-v2
  direction LR
  [*] --> Idea
  Idea --> Build
  Build --> Bug: it breaks
  Bug --> Learn
  Learn --> Build: retry
  Build --> Ship: it works
  Ship --> Idea: next obsession"""

def skills():
    t = {"Systems & AI": ["System design", "Agentic AI", "LLMs & API keys", "AI solutions"],
         "Languages": ["C++", "Java", "Python", "C#"],
         "Web": ["React", "Next.js", "Node.js", "Express", "Frontend", "Full-stack"],
         "Cloud & Data": ["AWS", "DevOps", "SQL & DBMS"],
         "CS Core": ["DSA", "OS", "Compiler design"],
         "Game & 3D": ["Unity", "Unreal", "Blender", "Game story"]}
    L = ["mindmap", "  root((Prasoon))"]
    for k, v in t.items():
        L.append(f"    {k}")
        L += [f"      {x}" for x in v]
    return "\n".join(L)
