"""CLI: python -m forge [build|verify|sync] [--now ISO8601] [--sync]"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from . import readme, scenes, sync

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "profile.toml"
CACHE = ROOT / "data" / "cache.json"
ASSETS = ROOT / "assets"


def load() -> tuple[dict, bytes]:
    raw = DATA.read_bytes()
    return tomllib.loads(raw.decode()), hashlib.sha256(raw).digest()


def build(now: datetime, out_root: Path = ROOT, do_sync: bool = False) -> dict[str, str]:
    p, sig = load()
    if do_sync:
        sync.run(p, CACHE)
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    chaos_svg, drift = scenes.chaos(p)
    files = {
        "hero.svg": scenes.hero(p, sig),
        "terminal.svg": scenes.terminal(p),
        "orbit.svg": scenes.orbit(p),
        "graph.svg": scenes.graph(p),
        "signals.svg": scenes.signals(p),
        "chaos.svg": chaos_svg,
    }
    stats = {"scenes": len(files) + 1, "bytes": sum(len(v.encode()) for v in files.values())}
    files["telemetry.svg"] = scenes.telemetry(p, now, sig, drift, stats)
    (out_root / "assets").mkdir(exist_ok=True)
    for name, text in files.items():
        (out_root / "assets" / name).write_text(text, encoding="utf-8")
    (out_root / "README.md").write_text(readme.render(p, cache, sig.hex()), encoding="utf-8")
    return files


def lint(files: dict[str, str]) -> list[str]:
    problems = []
    for name, text in files.items():
        try:
            root = ET.fromstring(text)
        except ET.ParseError as e:
            problems.append(f"{name}: invalid XML ({e})")
            continue
        if len(text.encode()) > 900_000:
            problems.append(f"{name}: over 900 KB")
        for el in root.iter():
            tag = el.tag.split("}")[-1]
            if tag in ("script", "foreignObject", "image"):
                problems.append(f"{name}: forbidden <{tag}>")
            for k, v in el.attrib.items():
                if k.endswith("href") and not v.startswith("#"):
                    problems.append(f"{name}: external reference {v}")
                if k.startswith("on"):
                    problems.append(f"{name}: event handler {k}")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="forge")
    ap.add_argument("cmd", choices=["build", "verify", "sync"], nargs="?", default="build")
    ap.add_argument("--now", help="ISO-8601 timestamp (default: current UTC)")
    ap.add_argument("--sync", action="store_true", help="fetch live repo stats first")
    a = ap.parse_args(argv)
    now = datetime.fromisoformat(a.now) if a.now else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    if a.cmd == "sync":
        sync.run(load()[0], CACHE)
        return 0
    files = build(now, do_sync=a.sync)
    if a.cmd == "build":
        print(f"built {len(files)} scenes, {sum(len(v) for v in files.values()) // 1024} KB")
        return 0
    problems = lint(files)
    again = {k: v for k, v in build(now).items()}
    if again != files:
        problems.append("build is not deterministic")
    for pr in problems:
        print("FAIL", pr)
    print("verify:", "ok" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
