"""
Compose the Stagehand hero image as a diagonal split between Mac and Windows.

The canvas is divided by a diagonal from the top-right corner to the
bottom-left corner. Mac fills the upper-left triangle, Windows fills the
lower-right triangle. A thin flame-colored accent traces the seam, and the
transparent logo is overlaid in the top-left.

Usage:
    py tools/compose_hero.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "tools" / "sources"
MAC_SRC = SOURCES / "stagehand-mac.png"
WIN_SRC = SOURCES / "stagehand-windows.png"
LOGO_SRC = ROOT / "assets" / "logo-mark.png"
OUT_PATH = ROOT / "assets" / "hero-platforms.png"

# Canvas
CANVAS_W, CANVAS_H = 2100, 1300

# Each screenshot is "cover" resized to fill the canvas, then cropped using an
# anchor that keeps the most important UI content in its triangle.
#   Mac (upper-left triangle)   → anchor on its top-left so the STAGEHAND
#                                 header + library top stay visible.
#   Windows (lower-right tri.)  → anchor on its bottom-right so the orange
#                                 Load-to-Resolume + Tag-management panels
#                                 + status bar stay visible.
MAC_ANCHOR = "topleft"
WIN_ANCHOR = "bottomright"

# Diagonal seam: gap between the two triangles, in pixels measured
# perpendicular to the diagonal.
SEAM_GAP = 6

# Accent line drawn on top of the diagonal seam
ACCENT_RGB = (255, 106, 26)   # flame-500
ACCENT_WIDTH = 3
ACCENT_GLOW_BLUR = 18
ACCENT_GLOW_ALPHA = 110

# Logo (off by default — Mac's own STAGEHAND header is already visible top-left)
ENABLE_LOGO = False
LOGO_WIDTH = 200
LOGO_POS = (60, 60)
LOGO_ALPHA = 235  # 0-255


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def cover_resize(img, target_w, target_h, anchor="center"):
    """Scale `img` so it fully covers (target_w, target_h), then crop to that
    box from the given anchor corner."""
    sw, sh = img.size
    ratio = max(target_w / sw, target_h / sh)
    new_w = int(round(sw * ratio))
    new_h = int(round(sh * ratio))
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    if anchor == "center":
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
    elif anchor == "topleft":
        left, top = 0, 0
    elif anchor == "topright":
        left, top = new_w - target_w, 0
    elif anchor == "bottomright":
        left, top = new_w - target_w, new_h - target_h
    elif anchor == "bottomleft":
        left, top = 0, new_h - target_h
    else:
        raise ValueError(f"unknown anchor: {anchor}")

    return img.crop((left, top, left + target_w, top + target_h))


def diagonal_endpoints_offset(w, h, gap):
    """Return the two pairs of endpoints for the diagonal from (w, 0) to
    (0, h), shifted perpendicular to itself by +gap and -gap.

    +gap shifts toward the upper-left, -gap shifts toward the lower-right.
    """
    import math
    L = math.hypot(w, h)
    # Unit vector along diagonal (from TR to BL): (-w, h) / L
    # Perpendicular pointing upper-left: (-h, -w) / L
    nx, ny = -h / L, -w / L
    p_tr = (w, 0)
    p_bl = (0, h)
    # Upper-left side (shift toward upper-left)
    ul_tr = (p_tr[0] + nx * gap, p_tr[1] + ny * gap)
    ul_bl = (p_bl[0] + nx * gap, p_bl[1] + ny * gap)
    # Lower-right side (shift toward lower-right)
    lr_tr = (p_tr[0] - nx * gap, p_tr[1] - ny * gap)
    lr_bl = (p_bl[0] - nx * gap, p_bl[1] - ny * gap)
    return (ul_tr, ul_bl), (lr_tr, lr_bl)


def triangle_mask_upper_left(w, h, gap):
    """Mask covering the upper-left triangle, leaving a gap along the
    diagonal."""
    (ul_tr, ul_bl), _ = diagonal_endpoints_offset(w, h, gap)
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon([(0, 0), ul_tr, ul_bl], fill=255)
    return mask


def triangle_mask_lower_right(w, h, gap):
    """Mask covering the lower-right triangle, leaving a gap along the
    diagonal."""
    _, (lr_tr, lr_bl) = diagonal_endpoints_offset(w, h, gap)
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon([lr_tr, (w, h), lr_bl], fill=255)
    return mask


def draw_accent_line(canvas, w, h, color, width, glow_blur, glow_alpha):
    """Draw a soft-glowing accent line along the diagonal, on top of the
    canvas. Mutates `canvas` and returns it."""
    # Glow layer
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).line(
        [(w, 0), (0, h)],
        fill=(*color, glow_alpha),
        width=width * 4,
    )
    glow = glow.filter(ImageFilter.GaussianBlur(glow_blur))
    canvas.alpha_composite(glow)

    # Sharp line on top
    sharp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sharp).line(
        [(w, 0), (0, h)],
        fill=(*color, 230),
        width=width,
    )
    canvas.alpha_composite(sharp)
    return canvas


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    mac = Image.open(MAC_SRC).convert("RGBA")
    win = Image.open(WIN_SRC).convert("RGBA")
    logo = Image.open(LOGO_SRC).convert("RGBA")

    mac_fit = cover_resize(mac, CANVAS_W, CANVAS_H, anchor=MAC_ANCHOR)
    win_fit = cover_resize(win, CANVAS_W, CANVAS_H, anchor=WIN_ANCHOR)

    mac_mask = triangle_mask_upper_left(CANVAS_W, CANVAS_H, SEAM_GAP)
    win_mask = triangle_mask_lower_right(CANVAS_W, CANVAS_H, SEAM_GAP)

    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    canvas.paste(mac_fit, (0, 0), mac_mask)
    canvas.paste(win_fit, (0, 0), win_mask)

    draw_accent_line(
        canvas, CANVAS_W, CANVAS_H,
        ACCENT_RGB, ACCENT_WIDTH, ACCENT_GLOW_BLUR, ACCENT_GLOW_ALPHA,
    )

    if ENABLE_LOGO:
        # Logo overlay (transparent watermark, top-left)
        ratio = LOGO_WIDTH / logo.width
        new_h = int(round(logo.height * ratio))
        logo = logo.resize((LOGO_WIDTH, new_h), Image.Resampling.LANCZOS)
        r, g, b, a = logo.split()
        a = a.point(lambda v: int(v * (LOGO_ALPHA / 255)))
        logo = Image.merge("RGBA", (r, g, b, a))
        canvas.alpha_composite(logo, LOGO_POS)

    canvas.save(OUT_PATH, "PNG", optimize=True)
    print(f"Wrote {OUT_PATH} — {canvas.size}, {OUT_PATH.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
