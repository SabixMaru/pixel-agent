"""Studio — the thin driver the agent pilots.

Holds a persistent canvas in a workdir. Apply a DSL program, then re-render
three views: the clean sprite, the annotated (grid + coordinate) view for
critique, and the palette legend.

CLI:
    python -m pixelagent.studio <workdir> <program_file> [--w 32 --h 32 --scale 16 --every 4 --reset]
"""
from __future__ import annotations

import argparse
import os
from typing import Dict

from .canvas import PixelCanvas
from .dsl import apply_commands
from .render import render_annotated, render_png, render_swatch


class Studio:
    def __init__(self, workdir: str, width: int = 32, height: int = 32, scale: int = 16,
                 reset: bool = False):
        self.workdir = workdir
        os.makedirs(workdir, exist_ok=True)
        self.canvas_path = os.path.join(workdir, "canvas.json")
        self.scale = scale
        if os.path.exists(self.canvas_path) and not reset:
            self.canvas = PixelCanvas.load_json(self.canvas_path)
        else:
            self.canvas = PixelCanvas(width, height)
            self.save()

    def apply(self, program: str) -> "Studio":
        apply_commands(self.canvas, program)
        self.save()
        return self

    def save(self) -> None:
        self.canvas.save_json(self.canvas_path)

    def render(self, every: int = 4) -> Dict[str, str]:
        outs = {
            "clean": os.path.join(self.workdir, "sprite.png"),
            "annotated": os.path.join(self.workdir, "annotated.png"),
            "swatch": os.path.join(self.workdir, "palette.png"),
        }
        render_png(self.canvas, scale=self.scale, checker=True).save(outs["clean"])
        render_annotated(self.canvas, scale=self.scale, margin=22, every=every).save(outs["annotated"])
        render_swatch(self.canvas.palette).save(outs["swatch"])
        return outs


def _main() -> None:
    ap = argparse.ArgumentParser(description="Apply a pixel DSL program and render views.")
    ap.add_argument("workdir")
    ap.add_argument("program_file")
    ap.add_argument("--w", type=int, default=32)
    ap.add_argument("--h", type=int, default=32)
    ap.add_argument("--scale", type=int, default=16)
    ap.add_argument("--every", type=int, default=4)
    ap.add_argument("--reset", action="store_true")
    a = ap.parse_args()
    studio = Studio(a.workdir, width=a.w, height=a.h, scale=a.scale, reset=a.reset)
    with open(a.program_file) as f:
        studio.apply(f.read())
    paths = studio.render(every=a.every)
    print(f"canvas {studio.canvas.width}x{studio.canvas.height}, palette {len(studio.canvas.palette)} entries")
    for k, v in paths.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    _main()
