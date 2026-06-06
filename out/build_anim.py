"""Build a cute idle animation: breathing bob + blink + ground shadow.

The cat is drawn on a taller (32x36) frame so it has vertical room. Each frame
places the base cat at a vertical offset `oy` (small = high on the rise) and draws
a ground-contact shadow whose width grows as the cat settles down.
Blink frames only edit the left eye interior; mirror_h keeps both eyes in sync.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pixelagent.animation import contact_sheet, export_gif, export_spritesheet
from pixelagent.canvas import PixelCanvas
from pixelagent.dsl import apply_commands

PROG = open(os.path.join(ROOT, "out", "cat_prog.txt")).read()
FUR, WHITE, PUPIL, SHADOW = 2, 6, 7, 10
FRAME_H = 36


def base(modifier=None):
    c = PixelCanvas(32, 32)
    apply_commands(c, PROG)  # ends with mirror_h -> symmetric
    if modifier:
        modifier(c)
        c.mirror_h()
    return c


def clear_eye(c):  # repaint left lens interior as fur (glasses ring untouched)
    c.line(8, 14, 10, 14, FUR)
    for y in (15, 16, 17):
        c.line(7, y, 11, y, FUR)
    c.line(8, 18, 10, 18, FUR)


def eye_half(c):
    clear_eye(c)
    c.line(7, 16, 11, 16, WHITE)
    c.line(8, 17, 10, 17, PUPIL)


def eye_closed(c):
    clear_eye(c)
    for x, y in [(7, 16), (8, 17), (9, 17), (10, 17), (11, 16)]:
        c.pixel(x, y, PUPIL)


def placed(src, oy):
    """Drop the 32x32 `src` onto a 32x36 frame at vertical offset oy, with shadow."""
    c = PixelCanvas(32, FRAME_H, src.palette)
    rx = 6 + oy  # shadow widens as the cat sinks
    c.ellipse(16 - rx, 33, 16 + rx, 35, SHADOW, filled=True)
    for y in range(32):
        for x in range(32):
            v = src.get(x, y)
            if v:
                c.pixel(x, y + oy, v)
    return c


open_, half, closed = base(), base(eye_half), base(eye_closed)

# (vertical offset, eye state) — rise, blink at the top, sink, settle
SEQ = [
    (3, open_), (2, open_), (1, open_), (0, open_),
    (0, half), (0, closed), (0, half), (0, open_),
    (1, open_), (2, open_), (3, open_), (3, open_),
]
frames = [placed(src, oy) for oy, src in SEQ]

OUT = os.path.join(ROOT, "out", "cat")
export_gif(frames, os.path.join(OUT, "idle.gif"), scale=10, fps=10, background=(246, 244, 240, 255))
export_spritesheet(frames, os.path.join(OUT, "idle_sheet.png"), scale=8)
contact_sheet(frames, scale=5, cols=12, pad=3).save(os.path.join(OUT, "idle_contact.png"))
print(f"built {len(frames)} frames -> idle.gif ({frames[0].width}x{frames[0].height})")
