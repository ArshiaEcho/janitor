"""Draws assets/terminal.gif: one janitor-claude pass over a demo folder with planted clutter.

Every finding below came from the skill's own read-only commands, run on that folder.
Typed lines appear a few characters at a time, output lines appear whole, and the last frame holds.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONT = ROOT / "scripts" / "brand" / "fonts" / "GeistMono-Variable.ttf"
OUT = ROOT / "assets" / "terminal.gif"
W, H, SCALE = 900, 600, 2
BG, TYPED, MUTED, MINT, AMBER = "#080d13", "#f3f7fa", "#8fa3b3", "#b5f4d9", "#fad5b1"

SCRIPT = [
    ("type", "> clean up this folder", TYPED),
    ("say", "Janitor here. Looking around, touching nothing yet.", MUTED),
    ("say", "  4 .DS_Store files, 2 __pycache__ folders, 2 tool caches", MINT),
    ("say", "  1 dead symlink: deploy.sh", MINT),
    ("say", "  CLAUDE.md imports docs/old-setup.md, which is gone", AMBER),
    ("say", "  a hook calls .claude/hooks/format.sh, which is missing", AMBER),
    ("say", "  skill \"release\" has no frontmatter, so no description", AMBER),
    ("say", "  .mcp.json server \"tickets\" points at a missing command", AMBER),
    ("say", "  .env is tracked by git (contents not shown, rotate keys)", AMBER),
    ("say", "Plan: move the 8 cache items to the Trash. Report the rest.", MUTED),
    ("type", "> yes", TYPED),
    ("say", "Moved 8 items to the Trash. Before 8, after 0.", MUTED),
    ("bold", "Clean. Come back any time.", TYPED),
]


def main() -> None:
    font = ImageFont.truetype(str(FONT), 15 * SCALE)
    font.set_variation_by_axes([400])
    bold = ImageFont.truetype(str(FONT), 15 * SCALE)
    bold.set_variation_by_axes([650])
    shown: list[tuple[str, str, ImageFont.FreeTypeFont]] = []
    frames: list[tuple[Image.Image, int]] = []

    def backdrop() -> Image.Image:
        image = Image.new("RGB", (W * SCALE, H * SCALE), BG)
        top, bottom = (16, 27, 36), (8, 13, 19)
        draw = ImageDraw.Draw(image)
        for y in range(H * SCALE):
            t = y / (H * SCALE)
            draw.line([(0, y), (W * SCALE, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))
        x0, y0, x1, y1 = (v * SCALE for v in (40, 36, W - 40, H - 36))
        draw.rounded_rectangle((x0, y0, x1, y1), radius=18 * SCALE, fill="#0b131a", outline="#22323d", width=2 * SCALE)
        draw.line([(x0, y0 + 40 * SCALE), (x1, y0 + 40 * SCALE)], fill="#1a2730", width=2 * SCALE)
        for index, dot in enumerate(("#f8c6d6", "#fad5b1", "#b5f4d9")):
            cx, cy = x0 + (24 + index * 20) * SCALE, y0 + 20 * SCALE
            draw.ellipse((cx - 6 * SCALE, cy - 6 * SCALE, cx + 6 * SCALE, cy + 6 * SCALE), fill=dot)
        title = "janitor-claude  ~/demo-repo"
        width = draw.textlength(title, font=small)
        draw.text(((W * SCALE - width) / 2, y0 + 11 * SCALE), title, fill=MUTED, font=small)
        return image

    small = ImageFont.truetype(str(FONT), 13 * SCALE)
    small.set_variation_by_axes([450])
    base = backdrop()

    def snap(ms: int, partial: tuple[str, str] | None = None, cursor: bool = False) -> None:
        image = base.copy()
        draw = ImageDraw.Draw(image)
        y = 98 * SCALE
        lines = shown + ([(partial[0], partial[1], font)] if partial else [])
        for text, colour, face in lines:
            draw.text((68 * SCALE, y), text, fill=colour, font=face)
            y += 31 * SCALE
        if cursor and lines:
            text, _, face = lines[-1]
            x = 68 * SCALE + draw.textlength(text, font=face) + 3 * SCALE
            draw.rectangle((x, y - 31 * SCALE + 2 * SCALE, x + 9 * SCALE, y - 31 * SCALE + 21 * SCALE), fill=MINT)
        frames.append((image.resize((W, H), Image.LANCZOS), ms))

    snap(700, (">", TYPED), cursor=True)
    for kind, text, colour in SCRIPT:
        if kind == "type":
            for end in range(2, len(text) + 1, 3):
                snap(45, (text[:end], colour), cursor=True)
            shown.append((text, colour, font))
            snap(350)
        else:
            shown.append((text, colour, bold if kind == "bold" else font))
            snap(260)
    shown.append((">", TYPED, font))
    snap(3200, cursor=True)

    # One palette for every frame, taken from the finished screen, so the window dots keep their colour throughout.
    palette = frames[-1][0].quantize(colors=96, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    first, *rest = (frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame, _ in frames)
    first.save(OUT, save_all=True, append_images=rest, duration=[ms for _, ms in frames], loop=0, optimize=True)


if __name__ == "__main__":
    main()
