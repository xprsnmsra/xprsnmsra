"""Pull live repo stats from the GitHub API into data/cache.json.

Runs inside GitHub Actions with GITHUB_TOKEN. If the network or token is missing it
leaves the existing cache untouched, so builds never fail because of the API.
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


def fetch(repo: str, token: str | None) -> dict | None:
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "forge"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.load(r)
        return {"stars": d["stargazers_count"], "forks": d["forks_count"],
                "language": d.get("language"), "pushed": (d.get("pushed_at") or "")[:10]}
    except Exception as exc:  # noqa: BLE001 - any failure means "keep the old cache"
        print(f"sync: {repo}: {exc}")
        return None


def run(profile: dict, cache_path: Path) -> dict:
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    token = os.environ.get("GITHUB_TOKEN")
    for pr in profile["project"]:
        if pr.get("repo"):
            got = fetch(pr["repo"], token)
            if got:
                cache[pr["repo"]] = got
    cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")
    return cache
