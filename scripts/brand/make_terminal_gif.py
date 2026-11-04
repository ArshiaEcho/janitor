"""Draws assets/terminal.gif: one janitor-claude pass over a demo folder with planted clutter.

Every finding below came from the skill's own read-only commands, run on that folder.
Typed lines appear a few characters at a time, output lines appear whole, and the last frame holds.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONT = ROOT / "scripts" / "brand" / "fonts" / "GeistMono-Variable.ttf"
OUT = ROOT / "assets" / "terminal.gif"
W, H, SCALE = 760, 500, 2
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

    def snap(ms: int, partial: tuple[str, str] | None = None) -> None:
        image = Image.new("RGB", (W * SCALE, H * SCALE), BG)
        draw = ImageDraw.Draw(image)
        y = 26 * SCALE
        for text, colour, face in shown + ([(partial[0], partial[1], font)] if partial else []):
            draw.text((26 * SCALE, y), text, fill=colour, font=face)
            y += 33 * SCALE
        frames.append((image.resize((W, H), Image.LANCZOS), ms))

    snap(500)
    for kind, text, colour in SCRIPT:
        if kind == "type":
            for end in range(2, len(text) + 1, 3):
                snap(45, (text[:end], colour))
            shown.append((text, colour, font))
            snap(350)
        else:
            shown.append((text, colour, bold if kind == "bold" else font))
            snap(260)
    frames[-1] = (frames[-1][0], 3200)

    first, *rest = (frame.quantize(colors=48, method=Image.MEDIANCUT) for frame, _ in frames)
    first.save(OUT, save_all=True, append_images=rest, duration=[ms for _, ms in frames], loop=0, optimize=True)


if __name__ == "__main__":
    main()
