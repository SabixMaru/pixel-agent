# Pixel-Agent — Design Spec

**Date:** 2026-06-05
**Status:** Approved (design), building v1

## Goal

A Python pixel-art engine that an AI (Claude, live in-session for v1) drives **by sight**:
draw with artist-style tools → render to PNG → *look at the result with vision* → critique →
edit → repeat until it meets a quality bar. Supports static sprites and frame-based animation.

This is the "Tier 3" approach: deliberate, controllable, editable per-pixel — not diffusion
(which paints the *style* of pixel art, not real grid pixels). The unique value vs. PixelLab et al.
is **control + editability + explainability**, not first-shot model quality.

## v1 target

- **32×32** canvas, a **cute cat wearing glasses**, highest quality achievable via the loop.
- Then a short animation (e.g. 4-frame idle) once the static sprite passes the bar.

## Architecture (small, independently testable units)

1. **`PixelCanvas`** — grid of palette indices + a named palette (index 0 = transparent).
   Ops: `pixel`, `line`, `rect`, `ellipse`, `flood_fill`, `mirror_h` (symmetry),
   `copy_region`, `clear`. State persists as JSON between edits.
2. **Command-batch applier** — a compact text DSL (e.g. `rect 10 8 22 30 fill 2`, `pixel 14 12 3`,
   `mirror_h`). One invocation applies many edits + re-renders. Efficient for the agent.
3. **Renderer** — grid → PNG, nearest-neighbor upscaled (×N, default ×16 so 32→512). Optional
   **grid + coordinate ruler** overlay (so a visual critique maps to exact (x,y)), transparency
   checkerboard, and a numbered **palette swatch** image.
4. **Frames + animation** — frames as `frame_NN.json`; **onion-skin** render (prev frame ghosted);
   copy-frame-then-nudge workflow; **contact sheet** (all frames in a row); export **animated GIF +
   spritesheet PNG + metadata JSON**.

## The agent loop (v1: Claude in-session)

Plan (subject, palette, silhouette) → block in shapes → render → LOOK → critique vs. intent and the
quality bar → edit batch → render → LOOK → repeat to the bar. Animation: key poses → copy+nudge
in-betweens → onion-skin review → export → review contact sheet.

**Honest caveat:** the AI's spatial judgment isn't pixel-perfect first-pass; the coordinate overlay
and the iterate-on-vision loop are what make it converge.

## Quality bar (research-backed; see spec sources)

1. **Silhouette test** — recognizable as a solid black shape; simplify until it passes.
2. **Resolution discipline** — suggest detail via color placement; no literal tiny features → noise.
3. **Tight palette** — one dominant hue family; 2–3 values/region (base+shadow+highlight); ~6–12 total.
4. **Hue-shift shading** — shadows shift hue (warm→red-purple, cool→blue-purple); highlights→warm.
5. **Selective outlining** — break/lighten outline where light hits; avoid pure black (dark tinted).
6. **Anti-alias sparingly** — smooth ≥2px staircases; never AA straight/45° lines; over-AA = blur.
7. One light source; pixel clusters not stray noise; avoid pure black.
8. **Cuteness levers** — big head, big eyes, rounded soft forms, small body, exaggerated glasses.

## Out of scope (v1)

Autonomous Claude-API wrapper (the *next* step), GUI/web frontend, reference-image import,
automated dithering algorithms.

## Testing

Unit tests for engine correctness: bounds-checked `pixel`, `line`/`rect`/`ellipse` rasterization,
`flood_fill`, `mirror_h`, JSON round-trip, GIF/spritesheet export produces N frames. Built test-first.

## Stack

Python 3.14, Pillow 12.2 (rendering + GIF). Lives at `~/Developer/Others/pixel-agent`.
