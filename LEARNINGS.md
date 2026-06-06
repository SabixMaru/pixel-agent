# Everything I learned making AI-generated pixel art & animation

A field guide distilled from building **pixel-agent** — a tool that lets an AI (Claude)
generate genuinely good pixel art and pixel animations by *seeing its own output and fixing it*.
Written so the next person (or the next Claude) doesn't have to rediscover all of this.

---

## 1. The core idea that actually works: a vision-feedback loop

The naïve approach — ask an LLM to emit a 64×64 grid of 4096 color values in one shot — produces
**noise**. LLMs have poor precise 2D spatial coherence at that scale.

What works instead is an **agentic loop**:

```
plan → draw with TOOLS → render to PNG → LOOK at it (vision) → critique → edit → repeat
```

The single most important realization: **the AI must look at a rendered image of its own work after
every change.** Vision feedback is the entire unlock. Without it you're drawing blind; with it the
output converges over a handful of passes.

Two supporting tricks make the loop usable:

- **Draw through tools, not pixels.** Operate on shapes/regions (`line`, `rect`, `ellipse`,
  `flood_fill`, `mirror`, `outline`) and only touch individual pixels for final detail. This is how
  human pixel artists work too: silhouette → blocking → detail.
- **Render an *annotated* view for critique.** Upscale nearest-neighbor, overlay a grid + coordinate
  ruler, and show a numbered palette swatch. This is what lets a visual critique ("the left eye is
  one pixel too high, outline broken near x=20") map to exact `(x, y)` edits.

Expect **3–4 critique passes per sprite.** It is not one-shot. That's fine — the value is that you
can fix *exactly* what's wrong.

---

## 2. Why this beats (and loses to) diffusion

| | Diffusion (PixelLab, Retro Diffusion, SD + LoRA) | Agentic per-pixel (this) |
|---|---|---|
| First-shot quality | High | Lower |
| Real grid / clean palette | No (paints the *style*; needs "pixelization" post-process) | Yes, by construction |
| Editability | Re-roll and pray | "make the eyes bigger" → edits those exact pixels |
| Explainable / deterministic | No | Yes |
| Animation control | Limited / canned | Full frame-by-frame control |

Use diffusion when you want a one-shot *look*. Use the agentic approach when you want **control,
editability, and explainability** — which is exactly what games, tools, and iterating-with-a-human need.

---

## 3. The pixel-art craft (the quality bar)

Researched from pixel-art tutorials; these are the rules the AI critiques against:

1. **Silhouette test** — the sprite must be recognizable as a solid black shape. If you can't tell
   what it is from the outline alone, color won't save it. Simplify until it passes.
2. **Resolution discipline** — *suggest* detail through color placement; don't draw literal tiny
   features (individual whiskers everywhere) → that's noise. 32×32 is a sweet spot; 64×64 allows
   real detail (whiskers, paws, round glasses).
3. **Tight palette** — one dominant hue family; 2–3 values per region (base + shadow + highlight);
   ~6–12 colors total.
4. **Hue-shift, don't just darken** — shadows shift hue (warm→red/orange, cool→blue/purple),
   highlights toward warm/yellow. Flat lighten/darken of one hue looks muddy.
5. **Selective outlining** — break/lighten the outline where light hits; avoid pure black (use a
   dark *tinted* color). Full dark outline = cute/cartoon; colored = modern/soft.
6. **Anti-alias sparingly** — smooth staircases of ≥2px with a halftone; never AA straight or 45°
   lines; over-AA = blur. At small sizes, often skip it.
7. **One light source**, **pixel clusters not stray noise**, **avoid pure black**.
8. **Cuteness levers** — big head, big eyes, rounded soft forms, small body, blush, exaggerate the
   defining feature (glasses, etc.).

Sources: Pixel Grimoire (Medium), Pixel Parmesan, Lospec, Pixel-Editor color theory, 2D Will Never
Die, Sprixen, Pixnote, phonoforest.

---

## 4. Engine design lessons

- **Store a grid of palette *indices*, not RGB.** Palette swaps, color ramps, and "recolor this
  region" become trivial. Index 0 = transparent.
- **Clip writes silently to bounds.** Drawing a shape partly off-canvas should clip, never crash.
- **A batch DSL makes the loop efficient.** A compact text language (`rect 10 8 22 30 2 fill`,
  `pixel 14 12 3`, `mirror_h`) means one tool call applies 50 edits + re-renders. One-pixel-per-call
  is far too slow for the loop.
- **`mirror_h` for symmetry.** Author the left half of a front-facing character, mirror to the
  right. Huge time saver and guarantees clean symmetry.
- **Stacked filled disks → clean round rings.** To draw round glasses, *don't* use an ellipse
  outline (jagged at small radii). Fill a frame-color disk, then a smaller white disk, then a
  smaller pupil disk. The leftover ring is perfectly round. (Difference-of-disks beats outline algos.)
- **Auto-outline is the biggest quality lever for chunky sprites.** Fill the entire silhouette in
  one color, then run one `outline()` pass that wraps every transparent cell bordering the shape in
  the outline color. You get a crisp, consistent 1px border around body + ears + feet + tail for free.
- **Persist the canvas as JSON** so edits accumulate across the loop, and so you can reload/branch.

---

## 5. Animation lessons

- **Frames are just canvases.** The workflow is *copy the last frame, nudge a few pixels, repeat.*
- **Only edit what moves.** A blink edits the eye interior and nothing else; then `mirror_h` keeps
  both eyes in sync. Don't redraw the whole frame.
- **Review with an onion-skin + a contact sheet.** Onion-skin (previous frame ghosted under the
  current) shows motion deltas; a contact sheet (all frames in a row) lets you eyeball the whole
  cycle at once — essential because you usually can't watch the GIF inside the tool.
- **NEVER shear/rotate across a rigid part — it splits it.** The #1 animation bug: applying a
  horizontal shear to a whole sprite to make it "sway" tears the head in half (top and bottom rows
  shift opposite directions). **Fix: layer it.** Draw the rigid part (head) on top as its own layer,
  and shear/rotate only the moving part (body) about a pivot at the join (the neck). Composite body
  then head; the head hides the seam.
- **A shadow that scales with motion sells weight.** A ground-contact shadow that widens as the
  character sinks and shrinks as it rises makes a bob read as *alive*, not floating.
- **GIF gotchas:**
  - **macOS Preview won't animate GIFs** — it shows the frames as a filmstrip. Use a **browser**
    (or QuickLook with spacebar) to actually see motion. The file is fine; the viewer isn't.
  - Export needs `disposal=2`, `loop=0`; quantize frames; identical trailing frames may get deduped.
  - GIF transparency is fiddly — easiest to composite each frame onto a background color.
- **For interactive "grab & swing" (desktop-pet) feel:** a damped spring driven by the pointer's
  velocity (`targetAngle = -velocity * k`, then spring toward it with damping) gives natural lag +
  overshoot. Keep the head a separate upright layer that follows the cursor; swing the body about
  the neck. In CSS, scale sprites at integer multiples of native size with `image-rendering: pixelated`
  to stay crisp.

---

## 6. Process lessons

- **Build the engine test-first (TDD).** The entire loop rests on the drawing primitives being
  correct — if `line`/`ellipse`/`flood_fill`/`mirror`/`outline` are even slightly wrong, the AI
  wastes passes fighting bugs instead of making art. Tested primitives = trustworthy canvas.
- **Reference without copying.** To match a style/pose, capture the *pose and vibe* (chunky sitting
  cat, simple face, blush, curled tail) and redraw it as original art — don't trace.
- **Recolors are nearly free.** Because the palette is indices + hex, a whole "litter" of color
  variants is a few hex swaps and a re-render.

---

## 7. Minimal architecture that delivers all of the above

```
canvas.py      grid of palette indices + ops: pixel/line/rect/ellipse/flood_fill/mirror_h/outline/copy
render.py      grid → PNG (clean), annotated PNG (grid + coord ruler), palette swatch
dsl.py         compact text drawing language (batch many edits per call)
animation.py   GIF / spritesheet / contact-sheet / onion-skin export
studio.py      driver/CLI: apply a DSL program to a persistent canvas, re-render all views
```

That's the whole thing. Small, testable, and it's enough for an AI to make good pixel art and
animations entirely by sight.
