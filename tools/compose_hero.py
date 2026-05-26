"""
Compose the Stagehand hero image.

Modes:
  - "sidebyside"  Two full app-window screenshots placed next to each other,
                  vertically centred, with rounded corners and a soft drop
                  shadow under each. No cropping, no overlap. (default)
  - "vertical"    Left half = Mac, right half = Windows, vertical seam.
  - "diagonal"    Mac fills upper-left triangle, Windows fills lower-right,
                  diagonal seam from top-right to bottom-left.

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

# "sidebyside" | "vertical" | "diagonal"
SPLIT_MODE = "sidebyside"

# --- side-by-side params ---------------------------------------------------
# Each window scaled to the same height for visual parity, placed L→R with a
# gap, vertically centred, drop-shadowed.
SBS_WINDOW_HEIGHT = 900       # height each app window is scaled to
SBS_GAP = 80                  # transparent gap between the two windows
SBS_SIDE_MARGIN = 80          # transparent margin on far left/right edges
SBS_TOP_MARGIN = 60           # transparent margin above/below windows
SBS_CORNER_RADIUS = 16
SBS_SHADOW_BLUR = 60
SBS_SHADOW_OFFSET = (0, 30)
SBS_SHADOW_ALPHA = 160

# --- split-mode params (unchanged, kept for "vertical"/"diagonal") ---------
if SPLIT_MODE == "vertical":
    CANVAS_W, CANVAS_H = 2100, 1100
elif SPLIT_MODE == "diagonal":
    CANVAS_W, CANVAS_H = 2100, 1300
else:
    CANVAS_W, CANVAS_H = None, None   # set dynamically in main()

if SPLIT_MODE == "vertical":
    MAC_ANCHOR, WIN_ANCHOR = "left", "right"
elif SPLIT_MODE == "diagonal":
    MAC_ANCHOR, WIN_ANCHOR = "topleft", "bottomright"
else:
    MAC_ANCHOR, WIN_ANCHOR = None, None

# Seam params (used for split modes only)
SEAM_GAP = 6
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

def fit_height(img, target_h):
    """Resize preserving aspect ratio so the image height matches target_h."""
    ratio = target_h / img.height
    new_w = int(round(img.width * ratio))
    return img.resize((new_w, target_h), Image.Resampling.LANCZOS)


def rounded_mask(size, radius):
    w, h = size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, w - 1, h - 1), radius=radius, fill=255,
    )
    return mask


def apply_rounded_corners(img, radius):
    mask = rounded_mask(img.size, radius)
    rounded = Image.new("RGBA", img.size, (0, 0, 0, 0))
    rounded.paste(img, (0, 0), mask=mask)
    return rounded


def screenshot_with_shadow(img, radius, shadow_blur, shadow_offset, shadow_alpha):
    """Return a transparent canvas containing a soft shadow + rounded-corner
    version of `img`, padded by 2*blur on each side so it composites cleanly
    without clipping."""
    rounded = apply_rounded_corners(img, radius)
    pad = shadow_blur * 2
    w, h = img.size
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))

    # Shadow: black silhouette of the rounded mask, blurred, alpha-capped.
    mask = rounded_mask((w, h), radius)
    shadow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow_layer.putalpha(Image.eval(mask, lambda v: min(v, shadow_alpha)))
    shadow_canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    shadow_canvas.paste(shadow_layer, (pad, pad), shadow_layer)
    shadow_canvas = shadow_canvas.filter(ImageFilter.GaussianBlur(shadow_blur))

    ox, oy = shadow_offset
    out.alpha_composite(shadow_canvas, (ox, oy))
    out.alpha_composite(rounded, (pad, pad))
    return out, pad


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
    elif anchor == "left":   # horizontal-left, vertical-center
        left = 0
        top = (new_h - target_h) // 2
    elif anchor == "right":  # horizontal-right, vertical-center
        left = new_w - target_w
        top = (new_h - target_h) // 2
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


def half_mask_left(w, h, gap):
    """Mask covering the left half of the canvas, leaving a gap at the centre
    seam."""
    seam_x = w // 2
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rectangle([0, 0, seam_x - gap, h], fill=255)
    return mask


def half_mask_right(w, h, gap):
    """Mask covering the right half of the canvas, leaving a gap at the centre
    seam."""
    seam_x = w // 2
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rectangle([seam_x + gap, 0, w, h], fill=255)
    return mask


def draw_accent_line(canvas, w, h, color, width, glow_blur, glow_alpha,
                     endpoints=None):
    """Draw a soft-glowing accent line on top of the canvas.

    `endpoints` is a (start, end) pair of (x, y) tuples. If omitted, draws
    the top-right→bottom-left diagonal."""
    if endpoints is None:
        endpoints = [(w, 0), (0, h)]

    # Glow layer
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).line(
        endpoints,
        fill=(*color, glow_alpha),
        width=width * 4,
    )
    glow = glow.filter(ImageFilter.GaussianBlur(glow_blur))
    canvas.alpha_composite(glow)

    # Sharp line on top
    sharp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sharp).line(
        endpoints,
        fill=(*color, 230),
        width=width,
    )
    canvas.alpha_composite(sharp)
    return canvas


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def compose_sidebyside(mac, win):
    """Two complete app windows side-by-side, vertically centred, with
    rounded corners and a soft drop shadow under each."""
    mac = fit_height(mac, SBS_WINDOW_HEIGHT)
    win = fit_height(win, SBS_WINDOW_HEIGHT)

    mac_card, pad = screenshot_with_shadow(
        mac, SBS_CORNER_RADIUS, SBS_SHADOW_BLUR, SBS_SHADOW_OFFSET, SBS_SHADOW_ALPHA,
    )
    win_card, _ = screenshot_with_shadow(
        win, SBS_CORNER_RADIUS, SBS_SHADOW_BLUR, SBS_SHADOW_OFFSET, SBS_SHADOW_ALPHA,
    )

    # Effective widths/heights INCLUDE shadow padding (`pad` per side).
    # When placing, subtract `pad` so the window content sits where we expect.
    canvas_w = (
        SBS_SIDE_MARGIN + mac.width + SBS_GAP + win.width + SBS_SIDE_MARGIN
    )
    canvas_h = SBS_WINDOW_HEIGHT + SBS_TOP_MARGIN * 2

    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

    # Mac on the left
    mac_x = SBS_SIDE_MARGIN - pad
    mac_y = SBS_TOP_MARGIN - pad + (SBS_WINDOW_HEIGHT - mac.height) // 2
    canvas.alpha_composite(mac_card, (mac_x, mac_y))

    # Windows on the right
    win_x = SBS_SIDE_MARGIN + mac.width + SBS_GAP - pad
    win_y = SBS_TOP_MARGIN - pad + (SBS_WINDOW_HEIGHT - win.height) // 2
    canvas.alpha_composite(win_card, (win_x, win_y))

    return canvas


def compose_split(mac, win):
    """Diagonal or vertical split-screen mode."""
    mac_fit = cover_resize(mac, CANVAS_W, CANVAS_H, anchor=MAC_ANCHOR)
    win_fit = cover_resize(win, CANVAS_W, CANVAS_H, anchor=WIN_ANCHOR)

    if SPLIT_MODE == "vertical":
        mac_mask = half_mask_left(CANVAS_W, CANVAS_H, SEAM_GAP)
        win_mask = half_mask_right(CANVAS_W, CANVAS_H, SEAM_GAP)
        seam_endpoints = [(CANVAS_W // 2, 0), (CANVAS_W // 2, CANVAS_H)]
    else:
        mac_mask = triangle_mask_upper_left(CANVAS_W, CANVAS_H, SEAM_GAP)
        win_mask = triangle_mask_lower_right(CANVAS_W, CANVAS_H, SEAM_GAP)
        seam_endpoints = [(CANVAS_W, 0), (0, CANVAS_H)]

    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    canvas.paste(mac_fit, (0, 0), mac_mask)
    canvas.paste(win_fit, (0, 0), win_mask)

    draw_accent_line(
        canvas, CANVAS_W, CANVAS_H,
        ACCENT_RGB, ACCENT_WIDTH, ACCENT_GLOW_BLUR, ACCENT_GLOW_ALPHA,
        endpoints=seam_endpoints,
    )
    return canvas


def main():
    mac = Image.open(MAC_SRC).convert("RGBA")
    win = Image.open(WIN_SRC).convert("RGBA")
    logo = Image.open(LOGO_SRC).convert("RGBA")

    if SPLIT_MODE == "sidebyside":
        canvas = compose_sidebyside(mac, win)
    else:
        canvas = compose_split(mac, win)

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
