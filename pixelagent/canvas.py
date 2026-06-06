"""Pixel canvas + palette — the data model the agent draws on.

A canvas is a grid of palette *indices*. Index 0 is always transparent.
All write ops clip silently to the canvas bounds (drawing partly off-canvas is fine).
"""
from __future__ import annotations

import json
from typing import List, Optional, Tuple

RGBA = Tuple[int, int, int, int]


def hex_to_rgba(hex_color: str) -> RGBA:
    h = hex_color.lstrip("#")
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    if len(h) == 8:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
    raise ValueError(f"bad hex color: {hex_color!r}")


class Palette:
    """Ordered colors. Index 0 is always transparent."""

    def __init__(self):
        self.entries: List[Tuple[str, Optional[str]]] = [("transparent", None)]

    def add(self, hex_color: str, name: str = "") -> int:
        self.entries.append((name, hex_color))
        return len(self.entries) - 1

    def rgba(self, idx: int) -> RGBA:
        _name, hexc = self.entries[idx]
        return (0, 0, 0, 0) if hexc is None else hex_to_rgba(hexc)

    def name(self, idx: int) -> str:
        return self.entries[idx][0]

    def hex(self, idx: int) -> Optional[str]:
        return self.entries[idx][1]

    def __len__(self) -> int:
        return len(self.entries)

    def to_dict(self) -> dict:
        return {"entries": [[n, h] for (n, h) in self.entries]}

    @classmethod
    def from_dict(cls, d: dict) -> "Palette":
        p = cls()
        p.entries = [(n, h) for (n, h) in d["entries"]]
        return p


class PixelCanvas:
    def __init__(self, width: int, height: int, palette: Optional[Palette] = None):
        self.width = width
        self.height = height
        self.palette = palette if palette is not None else Palette()
        self._grid: List[List[int]] = [[0] * width for _ in range(height)]

    # --- access ---
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get(self, x: int, y: int) -> int:
        return self._grid[y][x]

    def pixel(self, x: int, y: int, idx: int) -> "PixelCanvas":
        if self.in_bounds(x, y):
            self._grid[y][x] = idx
        return self

    def clear(self, idx: int = 0) -> "PixelCanvas":
        self._grid = [[idx] * self.width for _ in range(self.height)]
        return self

    # --- shapes ---
    def line(self, x0: int, y0: int, x1: int, y1: int, idx: int) -> "PixelCanvas":
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.pixel(x, y, idx)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy
        return self

    def rect(self, x0: int, y0: int, x1: int, y1: int, idx: int, filled: bool = False) -> "PixelCanvas":
        xa, xb = sorted((x0, x1))
        ya, yb = sorted((y0, y1))
        if filled:
            for y in range(ya, yb + 1):
                for x in range(xa, xb + 1):
                    self.pixel(x, y, idx)
        else:
            for x in range(xa, xb + 1):
                self.pixel(x, ya, idx)
                self.pixel(x, yb, idx)
            for y in range(ya, yb + 1):
                self.pixel(xa, y, idx)
                self.pixel(xb, y, idx)
        return self

    def ellipse(self, x0: int, y0: int, x1: int, y1: int, idx: int, filled: bool = False) -> "PixelCanvas":
        xa, xb = sorted((x0, x1))
        ya, yb = sorted((y0, y1))
        cx, cy = (xa + xb) / 2.0, (ya + yb) / 2.0
        rx, ry = (xb - xa) / 2.0, (yb - ya) / 2.0
        if rx <= 0 or ry <= 0:
            return self
        inside = set()
        for y in range(ya, yb + 1):
            for x in range(xa, xb + 1):
                nx, ny = (x - cx) / rx, (y - cy) / ry
                if nx * nx + ny * ny <= 1.0:
                    inside.add((x, y))
        if filled:
            for (x, y) in inside:
                self.pixel(x, y, idx)
        else:
            for (x, y) in inside:
                if any((x + dx, y + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    self.pixel(x, y, idx)
        return self

    def flood_fill(self, x: int, y: int, idx: int) -> "PixelCanvas":
        if not self.in_bounds(x, y):
            return self
        target = self.get(x, y)
        if target == idx:
            return self
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if not self.in_bounds(cx, cy) or self._grid[cy][cx] != target:
                continue
            self._grid[cy][cx] = idx
            stack += [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]
        return self

    def mirror_h(self) -> "PixelCanvas":
        for y in range(self.height):
            for x in range(self.width // 2):
                self._grid[y][self.width - 1 - x] = self._grid[y][x]
        return self

    def outline(self, idx: int, diagonal: bool = True) -> "PixelCanvas":
        """Wrap the whole non-empty shape in a 1px border of `idx` (drawn outward
        into transparent cells). Fill all your shapes, then call this once."""
        if diagonal:
            neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        else:
            neigh = [(0, -1), (-1, 0), (1, 0), (0, 1)]
        border = []
        for y in range(self.height):
            for x in range(self.width):
                if self._grid[y][x] != 0:
                    continue
                for dx, dy in neigh:
                    nx, ny = x + dx, y + dy
                    if self.in_bounds(nx, ny) and self._grid[ny][nx] != 0:
                        border.append((x, y))
                        break
        for x, y in border:
            self._grid[y][x] = idx
        return self

    def copy_region(self, sx: int, sy: int, w: int, h: int, dx: int, dy: int) -> "PixelCanvas":
        block = [[self.get(sx + i, sy + j) if self.in_bounds(sx + i, sy + j) else 0
                  for i in range(w)] for j in range(h)]
        for j in range(h):
            for i in range(w):
                self.pixel(dx + i, dy + j, block[j][i])
        return self

    # --- persistence ---
    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "palette": self.palette.to_dict(),
            "grid": self._grid,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PixelCanvas":
        c = cls(d["width"], d["height"], Palette.from_dict(d["palette"]))
        c._grid = [list(row) for row in d["grid"]]
        return c

    def save_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f)

    @classmethod
    def load_json(cls, path: str) -> "PixelCanvas":
        with open(path) as f:
            return cls.from_dict(json.load(f))

    def copy(self) -> "PixelCanvas":
        return PixelCanvas.from_dict(self.to_dict())
