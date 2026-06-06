# 🐾 pixel-agent

Make **pixel art and pixel animations by sight.** Instead of a diffusion model hallucinating a
pixel-art-*styled* image, an AI (Claude) drives a tiny Python engine in a loop:

> **plan → draw with tools → render → LOOK at it → critique → fix → repeat**

It draws on a real grid with a real palette, sees its own rendered output with vision, and corrects
exactly what's wrong — so you get **control, editability, and explainability** that diffusion can't give.
Want bigger eyes? Change two numbers and re-render. Want it orange instead of yellow? Swap one hex.

> Built live with Claude Code. See [`LEARNINGS.md`](LEARNINGS.md) for the full write-up of what makes
> AI-driven pixel art and animation actually work.

## What's in here

| | |
|---|---|
| `pixelagent/` | the engine — canvas, renderer, drawing DSL, animation export (Python + Pillow) |
| `skills/pixel-agent/` | the Claude Code **Skill** (the workflow Claude follows) |
| `.claude-plugin/` | plugin + marketplace manifests so Claude Code users can install it |
| `out/` | worked examples — a glasses cat (32 & 64px), a chunky yellow cat, blink + drag animations, an interactive grab-and-swing toy |
| `tests/` | the engine's test suite (39 tests) |

## Use it in Claude Code (one command)

```text
/plugin marketplace add github:SabixMaru/pixel-agent
/plugin install pixel-agent@pixel-agent
```

Then just ask: *"make me a cute 32×32 robot"* — Claude will write a drawing program, render it, look
at it, critique it against a pixel-art quality bar, and iterate until it's good. (Exact `/plugin`
syntax can vary by Claude Code version; run `/plugin` to browse if needed.)

## Use it standalone (any Python)

```bash
git clone https://github.com/SabixMaru/pixel-agent
cd pixel-agent
pip install -r requirements.txt

# apply a drawing program to a canvas and render it
PYTHONPATH=. python3 -m pixelagent.studio out/demo out/chonk_prog.txt \
  --w 64 --h 64 --scale 8 --reset

python3 -m unittest discover -s tests -t .   # run the tests
```

## The DSL (one command per line)

```text
color #RRGGBB name        # index 0 is always transparent
pixel X Y IDX
line X0 Y0 X1 Y1 IDX
rect X0 Y0 X1 Y1 IDX [fill]
ellipse X0 Y0 X1 Y1 IDX [fill]
fill X Y IDX              # flood fill
mirror_h                  # mirror left half -> right (symmetry)
outline IDX               # wrap the filled shape in a 1px border
copy SX SY W H DX DY
```

Tricks that matter: author the left half + `mirror_h` for symmetry; **stack filled disks** for clean
round glasses/eyes; **fill everything then `outline 1`** for a crisp silhouette; hue-shift your shading.

## License

MIT © 2026 SabixMaru
