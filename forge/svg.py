"""Tiny SVG helpers shared by every scene."""
from __future__ import annotations

from xml.sax.saxutils import escape

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

C = {
    "bg": "#0b0f14", "panel": "#111823", "line": "#1f2a37", "ink": "#e6edf3",
    "muted": "#7d8a99", "accent": "#39ff88", "a2": "#4cc9f0", "violet": "#9d7bff",
    "pink": "#ff5d8f", "warm": "#ffb454", "teal": "#2dd4bf",
}


def n(x: float) -> str:
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def kt(vals: list[float]) -> str:
    return ";".join(f"{v:.4f}".rstrip("0").rstrip(".") or "0" for v in vals)


def esc(s: str) -> str:
    return escape(s, {'"': "&quot;"})


def col(name: str) -> str:
    return C.get(name, name)


def document(w: int, h: int, title: str, desc: str, body: str, defs: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(title)}" '
        f'font-family="{MONO}">\n<title>{esc(title)}</title>\n<desc>{esc(desc)}</desc>\n'
        f'<defs>{defs}</defs>\n{body}\n</svg>\n'
    )


def frame(w: int, h: int, grid: bool = True) -> str:
    """Rounded dark panel with an optional faint grid, so every scene is theme-proof."""
    g = (f'<rect width="{w}" height="{h}" rx="18" fill="url(#grid)"/>' if grid else "")
    return (f'<rect width="{w}" height="{h}" rx="18" fill="{C["bg"]}"/>{g}'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="18" fill="none" stroke="{C["line"]}"/>')


GRID_DEFS = (
    f'<pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">'
    f'<path d="M30 0H0V30" fill="none" stroke="#ffffff" stroke-opacity=".035"/></pattern>'
)

GLOW_DEFS = (
    '<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">'
    '<feGaussianBlur stdDeviation="3" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    '<filter id="glow2" x="-60%" y="-60%" width="220%" height="220%">'
    '<feGaussianBlur stdDeviation="6" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
)
