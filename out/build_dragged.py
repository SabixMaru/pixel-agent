"""'Being dragged' animation — RIGID head, SWAYING body.

Two layers: the head (never distorted) and the body+legs (sheared about the neck
so it swings like a pendulum). Body is drawn first, head on top hides the join.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pixelagent.animation import contact_sheet, export_gif, export_spritesheet
from pixelagent.canvas import PixelCanvas
from pixelagent.dsl import apply_commands
from pixelagent.render import render_png

HEAD_PROG = open(os.path.join(ROOT, "out", "cat_dragged_prog.txt")).read()
BODY_PROG = open(os.path.join(ROOT, "out", "cat_dragged_body.txt")).read()

FRAME_W, FRAME_H = 44, 40
OX, OY = 6, 2
BODY_PIVOT = 24 + OY   # frame row where the body attaches under the chin
DIV = 5                # smaller = bigger leg swing


def built(prog):
    c = PixelCanvas(32, 36)
    apply_commands(c, prog)
    return c


def blit(dst, src):
    for y in range(min(dst.height, src.height)):
        for x in range(min(dst.width, src.width)):
            v = src.get(x, y)
            if v:
                dst.pixel(x, y, v)


def place_wide(src):
    c = PixelCanvas(FRAME_W, FRAME_H, src.palette)
    for y in range(src.height):
        for x in range(src.width):
            v = src.get(x, y)
            if v:
                c.pixel(x + OX, y + OY, v)
    return c


def sway_body(src, amount):
    """Shear only below the pivot — the body swings, nothing above the neck moves."""
    c = PixelCanvas(src.width, src.height, src.palette)
    for y in range(src.height):
        dx = round(amount * (y - BODY_PIVOT) / DIV) if y > BODY_PIVOT else 0
        for x in range(src.width):
            v = src.get(x, y)
            if v:
                c.pixel(x + dx, y, v)
    return c


head = place_wide(built(HEAD_PROG))
body = place_wide(built(BODY_PROG))


def frame(amount):
    c = PixelCanvas(FRAME_W, FRAME_H, head.palette)
    blit(c, sway_body(body, amount))  # swinging body underneath
    blit(c, head)                     # rigid head on top, hides the join
    return c


AMOUNTS = [-2, -1, 0, 1, 2, 1, 0, -1]
frames = [frame(a) for a in AMOUNTS]

OUT = os.path.join(ROOT, "out", "cat")
export_gif(frames, os.path.join(OUT, "dragged.gif"), scale=10, fps=12, background=(246, 244, 240, 255))
export_spritesheet(frames, os.path.join(OUT, "dragged_sheet.png"), scale=8)
contact_sheet(frames, scale=5, cols=8, pad=3).save(os.path.join(OUT, "dragged_contact.png"))

# separate still layers for the interactive toy (aligned 44x40 frames)
render_png(head, scale=10).save(os.path.join(OUT, "head_still.png"))
render_png(body, scale=10).save(os.path.join(OUT, "body_still.png"))
print(f"built {len(frames)} frames -> dragged.gif + head_still.png + body_still.png")
