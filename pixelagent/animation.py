"""Frame-based animation export: GIF, spritesheet, contact sheet, onion-skin.

Frames are just PixelCanvas objects. The animation workflow is "copy the last
frame, nudge a few pixels, repeat" — then export to review/ship.
"""
from __future__ import annotations

from typing import List, Optional

from PIL import Image

from .canvas import PixelCanvas
from .render import render_png

_BG = (40, 40, 44, 255)


def _flatten(im: Image.Image, background) -> Image.Image:
    bg = Image.new("RGBA", im.size, background)
    bg.alpha_composite(im)
    return bg


def export_gif(frames: List[PixelCanvas], path: str, scale: int = 8, fps: int = 8,
               background=_BG) -> None:
    imgs = [render_png(f, scale=scale) for f in frames]
    flat = [_flatten(im, background).convert("RGB").quantize(colors=128) for im in imgs]
    duration = int(1000 / max(1, fps))
    flat[0].save(path, save_all=True, append_images=flat[1:], duration=duration,
                 loop=0, disposal=2, optimize=False)


def export_spritesheet(frames: List[PixelCanvas], path: str, scale: int = 8) -> None:
    imgs = [render_png(f, scale=scale) for f in frames]
    fw, fh = imgs[0].size
    sheet = Image.new("RGBA", (fw * len(imgs), fh), (0, 0, 0, 0))
    for i, im in enumerate(imgs):
        sheet.paste(im, (i * fw, 0))
    sheet.save(path)


def contact_sheet(frames: List[PixelCanvas], scale: int = 8, cols: Optional[int] = None,
                  pad: int = 4, bg=(28, 28, 30, 255)) -> Image.Image:
    imgs = [render_png(f, scale=scale, checker=True) for f in frames]
    n = len(imgs)
    fw, fh = imgs[0].size
    cols = cols or n
    rows = (n + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * fw + (cols + 1) * pad, rows * fh + (rows + 1) * pad), bg)
    for i, im in enumerate(imgs):
        r, c = divmod(i, cols)
        sheet.paste(im, (pad + c * (fw + pad), pad + r * (fh + pad)), im)
    return sheet


def onion_skin(prev: PixelCanvas, cur: PixelCanvas, scale: int = 8, ghost: float = 0.35) -> Image.Image:
    faded = render_png(prev, scale=scale)
    faded.putalpha(faded.getchannel("A").point(lambda a: int(a * ghost)))
    top = render_png(cur, scale=scale)
    out = Image.new("RGBA", top.size, _BG)
    out.alpha_composite(faded)
    out.alpha_composite(top)
    return out
