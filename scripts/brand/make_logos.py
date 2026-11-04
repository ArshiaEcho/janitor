"""Writes the Janitor mark and the nine README tile logos. Every glyph carries the same slanted cut.

The cut and the tile frame follow the Altocue brand system, so the Stratos House repos read as one family.
Each tile owns one hue on the same pearl spectrum.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "assets" / "logos"

TOOLS = {
    "diagnose": ("#b5f4d9", "#7fdcbd"),
    "villains": ("#f8c6d6", "#ee96b4"),
    "disk": ("#abdffa", "#74b8ea"),
    "memory": ("#cfc0f9", "#a690ee"),
    "settings": ("#b8cbfb", "#8aa2f0"),
    "clutter": ("#fad5b1", "#f2b27c"),
    "trash": ("#a8efe9", "#6fd3d6"),
    "password": ("#f3e4a4", "#ddc26a"),
    "verify": ("#d7f1a9", "#a9d873"),
}


def slash(x: float, w: float = 5.5, y: float = -12, h: float = 124) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#000" transform="rotate(10 {x + w / 2} 50)"/>'


def broom() -> str:
    """The Janitor mark: a broom, handle up, with the slanted cut running through the bristles."""
    return (
        '<rect x="44" y="5" width="12" height="44" rx="6" fill="#fff"/>'
        '<path d="M30 56 H70 L82 90 H18 Z" fill="#fff" stroke="#fff" stroke-width="10" stroke-linejoin="round"/>'
        + slash(34.5, 5, 66, 50) + slash(47.5, 5, 66, 50) + slash(60.5, 5, 66, 50)
    )


GLYPHS = {
    "diagnose": (
        '<path d="M12 70 A38 38 0 0 1 88 70" fill="none" stroke="#fff" stroke-width="13" stroke-linecap="round"/>'
        '<path d="M50 70 L70 34" stroke="#fff" stroke-width="9" stroke-linecap="round"/>'
        '<circle cx="50" cy="70" r="10" fill="#fff"/>' + slash(30, 4.5, 20, 36)
    ),
    "villains": (
        '<circle cx="50" cy="50" r="40" fill="#fff"/><circle cx="50" cy="50" r="26" fill="#000"/>'
        '<circle cx="50" cy="50" r="13" fill="#fff"/>' + slash(47.5, 5)
    ),
    "disk": "".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="18" rx="7" fill="#fff" fill-opacity="{o}"/>'
        for x, y, w, o in ((10, 18, 80, ".42"), (10, 41, 80, ".7"), (10, 64, 80, "1"))
    )
    + slash(60, 5),
    "memory": (
        '<rect x="18" y="8" width="64" height="84" rx="12" fill="#fff"/>'
        + "".join(f'<rect x="30" y="{y}" width="{w}" height="7" rx="3.5" fill="#000"/>' for y, w in ((24, 40), (38, 40), (52, 28), (66, 34)))
        + slash(66, 4.5, 50, 60)
    ),
    "settings": "".join(
        f'<rect x="10" y="{y - 4}" width="80" height="8" rx="4" fill="#fff" fill-opacity=".46"/><circle cx="{c}" cy="{y}" r="11" fill="#fff"/>'
        for y, c in ((22, 66), (50, 32), (78, 58))
    ),
    "clutter": (
        '<path d="M42 8 Q46 38 74 44 Q46 50 42 82 Q38 50 10 44 Q38 38 42 8 Z" fill="#fff"/>'
        '<path d="M78 58 Q80 72 92 75 Q80 78 78 92 Q76 78 64 75 Q76 72 78 58 Z" fill="#fff" fill-opacity=".62"/>'
    ),
    "trash": (
        '<rect x="14" y="14" width="72" height="12" rx="6" fill="#fff"/><rect x="38" y="6" width="24" height="10" rx="5" fill="#fff"/>'
        '<path d="M22 32 H78 L72 88 Q71 94 65 94 H35 Q29 94 28 88 Z" fill="#fff"/>'
        + slash(38, 4.5, 42, 44) + slash(55, 4.5, 42, 44)
    ),
    "password": (
        '<circle cx="32" cy="50" r="22" fill="#fff"/><circle cx="32" cy="50" r="9" fill="#000"/>'
        '<rect x="48" y="44" width="42" height="12" rx="6" fill="#fff"/>'
        '<rect x="70" y="50" width="9" height="20" rx="4" fill="#fff"/><rect x="82" y="50" width="8" height="15" rx="4" fill="#fff"/>'
    ),
    "verify": (
        '<circle cx="50" cy="50" r="42" fill="#fff"/>'
        '<path d="M30 51 L44 65 L71 36" fill="none" stroke="#000" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
}


def glyph_svg(name: str, top: str, bottom: str, size: int = 100) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 100 100">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>'
        f'<mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100"><rect width="100" height="100" fill="#000"/>{GLYPHS[name]}</mask></defs>'
        f'<rect width="100" height="100" fill="url(#g)" mask="url(#m)"/></svg>'
    )


def tile_svg(name: str, top: str, bottom: str) -> str:
    inner = glyph_svg(name, top, bottom)
    body = inner[inner.index("<defs>") : inner.rindex("</svg>")]
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160">'
        '<defs><linearGradient id="t" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#1b2c35"/><stop offset=".62" stop-color="#101b24"/></linearGradient></defs>'
        '<rect x="1" y="1" width="158" height="158" rx="42" fill="url(#t)" stroke="#d3eefc" stroke-opacity=".16" stroke-width="2"/>'
        f'<svg x="38" y="38" width="84" height="84" viewBox="0 0 100 100">{body}</svg></svg>'
    )


def mark_svg(size: int = 100) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 100 100">'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#eafff5"/><stop offset=".38" stop-color="#b5f4d9"/>'
        '<stop offset=".72" stop-color="#a5e7d1"/><stop offset="1" stop-color="#8fd4e0"/></linearGradient>'
        '<mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100"><rect width="100" height="100" fill="#000"/>'
        f"{broom()}</mask></defs>"
        '<rect width="100" height="100" fill="url(#g)" mask="url(#m)"/></svg>'
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "janitor.svg").write_text(mark_svg())
    for name, (top, bottom) in TOOLS.items():
        (OUT / f"{name}.svg").write_text(glyph_svg(name, top, bottom))
        (OUT / f"{name}-tile.svg").write_text(tile_svg(name, top, bottom))


if __name__ == "__main__":
    main()
