"""A tiny line-based drawing language so the agent applies many edits per call.

One command per line. Full-line comments start with '#'. Example program:

    color #2b2b2b outline
    color #f4a259 fur
    ellipse 8 6 23 21 2 fill
    mirror_h
    pixel 12 14 1

Commands:
    color HEX [name]
    pixel X Y IDX
    line X0 Y0 X1 Y1 IDX
    rect X0 Y0 X1 Y1 IDX [fill]
    ellipse X0 Y0 X1 Y1 IDX [fill]
    fill X Y IDX            (flood fill)
    mirror_h
    clear [IDX]
    copy SX SY W H DX DY
"""
from __future__ import annotations

from .canvas import PixelCanvas


def apply_commands(canvas: PixelCanvas, text: str) -> PixelCanvas:
    for lineno, raw in enumerate(text.splitlines(), 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        cmd, args = parts[0], parts[1:]
        try:
            _dispatch(canvas, cmd, args)
        except ValueError:
            raise
        except Exception as e:  # arity / parse errors -> actionable message
            raise ValueError(f"line {lineno}: {stripped!r}: {e}")
    return canvas


def _dispatch(canvas: PixelCanvas, cmd: str, args: list) -> None:
    if cmd == "color":
        canvas.palette.add(args[0], args[1] if len(args) > 1 else "")
    elif cmd == "pixel":
        x, y, i = map(int, args)
        canvas.pixel(x, y, i)
    elif cmd == "line":
        x0, y0, x1, y1, i = map(int, args)
        canvas.line(x0, y0, x1, y1, i)
    elif cmd == "rect":
        filled = bool(args) and args[-1] == "fill"
        x0, y0, x1, y1, i = map(int, args[:-1] if filled else args)
        canvas.rect(x0, y0, x1, y1, i, filled=filled)
    elif cmd == "ellipse":
        filled = bool(args) and args[-1] == "fill"
        x0, y0, x1, y1, i = map(int, args[:-1] if filled else args)
        canvas.ellipse(x0, y0, x1, y1, i, filled=filled)
    elif cmd == "fill":
        x, y, i = map(int, args)
        canvas.flood_fill(x, y, i)
    elif cmd == "mirror_h":
        canvas.mirror_h()
    elif cmd == "outline":
        canvas.outline(int(args[0]), diagonal=(len(args) < 2 or args[1] != "ortho"))
    elif cmd == "clear":
        canvas.clear(int(args[0]) if args else 0)
    elif cmd == "copy":
        sx, sy, w, h, dx, dy = map(int, args)
        canvas.copy_region(sx, sy, w, h, dx, dy)
    else:
        raise ValueError(f"unknown command: {cmd!r}")
