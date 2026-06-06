"""Render a PixelCanvas to viewable PNGs.

- render_png:       clean upscaled sprite (what the art actually looks like)
- render_annotated: upscaled + grid + coordinate ruler (what the AGENT reads to locate pixels)
- render_swatch:    numbered palette legend (so the agent knows index -> color)
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

from .canvas import Palette, PixelCanvas

_FONT = ImageFont.load_default()
_CHECK_A = (90, 90, 90, 255)
_CHECK_B = (60, 60, 60, 255)
_BG = (28, 28, 30, 255)


def render_png(canvas: PixelCanvas, scale: int = 16, grid: bool = False,
               grid_color=(0, 0, 0, 40), checker: bool = False) -> Image.Image:
    w, h = canvas.width * scale, canvas.height * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for cy in range(canvas.height):
        for cx in range(canvas.width):
            rgba = canvas.palette.rgba(canvas.get(cx, cy))
            if rgba[3] == 0:
                if checker:
                    rgba = _CHECK_A if (cx + cy) % 2 == 0 else _CHECK_B
                else:
                    continue
            draw.rectangle([cx * scale, cy * scale, (cx + 1) * scale - 1, (cy + 1) * scale - 1], fill=rgba)
    if grid:
        for cx in range(canvas.width + 1):
            draw.line([(cx * scale, 0), (cx * scale, h)], fill=grid_color)
        for cy in range(canvas.height + 1):
            draw.line([(0, cy * scale), (w, cy * scale)], fill=grid_color)
    return img


def render_annotated(canvas: PixelCanvas, scale: int = 16, margin: int = 24,
                     every: int = 4) -> Image.Image:
    base = render_png(canvas, scale=scale, grid=True, checker=True)
    w, h = base.size
    img = Image.new("RGBA", (w + margin, h + margin), _BG)
    img.paste(base, (margin, margin), base)
    draw = ImageDraw.Draw(img)
    for cx in range(0, canvas.width, every):
        draw.text((margin + cx * scale + 1, 2), str(cx), fill=(225, 225, 225, 255), font=_FONT)
    for cy in range(0, canvas.height, every):
        draw.text((2, margin + cy * scale + 1), str(cy), fill=(225, 225, 225, 255), font=_FONT)
    return img


def render_swatch(palette: Palette, cell: int = 24) -> Image.Image:
    n = len(palette)
    img = Image.new("RGBA", (cell * 9, cell * n), _BG)
    draw = ImageDraw.Draw(img)
    for i in range(n):
        rgba = palette.rgba(i)
        y = i * cell
        if rgba[3] == 0:
            for k in range(0, cell, max(1, cell // 3)):
                fill = _CHECK_A if (k // max(1, cell // 3)) % 2 == 0 else _CHECK_B
                draw.rectangle([k, y, k + cell // 3 - 1, y + cell - 1], fill=fill)
        else:
            draw.rectangle([0, y, cell - 1, y + cell - 1], fill=rgba)
        label = f"{i}: {palette.name(i) or palette.hex(i) or 'transparent'}"
        draw.text((cell + 4, y + cell // 3), label, fill=(232, 232, 232, 255), font=_FONT)
    return img
