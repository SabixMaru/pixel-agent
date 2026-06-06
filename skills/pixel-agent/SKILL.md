---
name: pixel-agent
description: Use when the user wants to CREATE pixel art or pixel animations (sprites, game art, icons, a cute character, an animated GIF). Drives the bundled pixel-agent Python engine in a draw → render → LOOK → critique → fix loop so Claude makes the art by sight, with full per-pixel control.
---

# Making pixel art & animation by sight

You generate pixel art by **looking at your own output and fixing it**, not by emitting pixels blind.
Run the loop below. Expect 3–4 critique passes per sprite — that's normal.

## The loop

1. **Plan** the subject, canvas size (32×32 is a sweet spot, 64×64 for detail), and a tight palette.
2. **Write a DSL program** (`*.txt`) using the commands below. Author the LEFT half of symmetric
   characters and end with `mirror_h`.
3. **Render** it and **read the annotated PNG** (it has a grid + coordinate ruler so you can locate
   every pixel) AND the clean sprite.
4. **Critique against the quality bar** (below). State concrete fixes ("left eye 1px high, outline
   broken at x=20").
5. **Edit the program, re-render, look again.** Repeat until it's good. Show the user the clean sprite.

## Running the engine

The engine is bundled with this skill (a Python package `pixelagent`, needs Pillow). From the plugin
root (the folder containing `pixelagent/`):

```bash
pip install pillow            # once, if missing
PYTHONPATH=<plugin_root> python3 -m pixelagent.studio <workdir> <program.txt> \
  --w 32 --h 32 --scale 16 --every 4 --reset
```

This writes `<workdir>/sprite.png` (clean), `annotated.png` (grid+coords — read THIS to critique),
and `palette.png`. Re-run after each edit (drop `--reset` to keep accumulating onto the canvas).

## DSL commands (one per line; `#` = full-line comment)

```
color #RRGGBB name        define a palette color (index 0 is always transparent)
pixel X Y IDX
line X0 Y0 X1 Y1 IDX
rect X0 Y0 X1 Y1 IDX [fill]
ellipse X0 Y0 X1 Y1 IDX [fill]
fill X Y IDX              flood fill
mirror_h                  mirror left half onto right (symmetry)
outline IDX               wrap the whole filled shape in a 1px border of IDX
clear [IDX]
copy SX SY W H DX DY
```

## High-leverage techniques

- **Symmetry:** author the left half, end with `mirror_h`. For an asymmetric part (a tail), draw it
  AFTER `mirror_h`.
- **Clean round rings (glasses/eyes):** stack filled disks — frame disk, then smaller white disk,
  then smaller pupil disk. Do NOT use `ellipse` outline (jagged).
- **Clean silhouette:** fill ALL fur/body/ear/feet/tail shapes in the base color, then call
  `outline 1` once for a crisp border around everything.
- **Shading:** hue-shift (warm base → orange/red shadow, pale-warm highlight), one light source,
  follow the form's curve (don't lay flat horizontal bands — that reads as a headband).

## Quality bar (critique against this every pass)

1. Silhouette reads as a solid black shape. 2. Suggest detail via color, don't over-detail (noise).
3. Tight palette, 2–3 values/region, ~6–12 colors. 4. Hue-shift shadows, don't just darken.
5. Selective/tinted outline, not pure black. 6. AA sparingly. 7. One light source, clusters not noise.
8. Cuteness: big head/eyes, rounded forms, blush, exaggerate the defining feature.

## Animation

Frames are just canvases — copy the last, nudge what moves, re-render. Build a small Python script
(see `out/build_anim.py`, `out/build_dragged.py` for worked examples) that:
- derives frames by editing only the moving part (e.g. eye interior for a blink) + `mirror_h`;
- exports `export_gif`, `export_spritesheet`, and a `contact_sheet` to review.

**Critical rule:** never shear/rotate across a rigid part — it SPLITS it (e.g. a sway that tears the
head). Layer it: rigid part on top, moving part sheared/rotated about the join, composited.

**GIF viewing:** macOS Preview won't animate GIFs (shows frames). Open in a browser or QuickLook.

See `LEARNINGS.md` in the repo for the full write-up of why all of this works.
