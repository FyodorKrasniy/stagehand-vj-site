"""
Convert hero PNG and feature GIFs to WebP for faster page loads.

- Hero PNG -> lossless WebP (transparency preserved, sharp UI edges)
- Feature GIFs -> animated WebP (per-frame timing preserved, loops forever)

All modern browsers (Chrome 32+, Firefox 65+, Safari 14+, Edge 18+) support
both static and animated WebP, so the site can reference .webp directly
without a <picture> fallback. The originals stay on disk for source-archive
purposes.

Usage:
    py tools/optimize_assets.py
"""

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Static PNGs -> lossless WebP
STATIC_PNGS = [
    "hero-platforms.png",
]

# Animated GIFs -> animated WebP
ANIMATED_GIFS = [
    "stagehand-library-picker-large.gif",
    "stagehand-controls-options-large.gif",
    "stagehand-preview-switching-large.gif",
    "stagehand-set-workflow-large.gif",
    "stagehand-resolume-handoff-large.gif",
]


def convert_png_lossless(src_name):
    src = ASSETS / src_name
    dst = src.with_suffix(".webp")
    img = Image.open(src)
    img.save(dst, "WEBP", lossless=True, quality=100, method=6)
    return src, dst


def convert_gif_animated(src_name):
    src = ASSETS / src_name
    dst = src.with_suffix(".webp")

    img = Image.open(src)
    frames = []
    durations = []
    try:
        while True:
            # Convert each frame to RGBA so transparency carries across
            frames.append(img.convert("RGBA").copy())
            durations.append(img.info.get("duration", 100))
            img.seek(img.tell() + 1)
    except EOFError:
        pass

    frames[0].save(
        dst,
        "WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,            # loop forever
        quality=82,
        method=6,
        minimize_size=True,
    )
    return src, dst


def report(src, dst):
    before = src.stat().st_size
    after = dst.stat().st_size
    pct = 100 * (1 - after / before)
    print(
        f"  {src.name:50s} {before // 1024:>5} KB  ->  "
        f"{dst.name:50s} {after // 1024:>5} KB  ({pct:+.0f}%)"
    )


def main():
    print("Static PNGs -> lossless WebP")
    for name in STATIC_PNGS:
        report(*convert_png_lossless(name))

    print("\nAnimated GIFs -> animated WebP")
    for name in ANIMATED_GIFS:
        report(*convert_gif_animated(name))


if __name__ == "__main__":
    main()
