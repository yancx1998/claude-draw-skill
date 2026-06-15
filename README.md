# claude-draw-skill

A `/draw` slash command for [Claude Code](https://claude.ai/code) that opens a sketchpad window, lets you draw, and loads the result directly into the conversation.

![demo](demo.png)

## Features

- Color picker, adjustable brush size, eraser, clear button
- Cross-platform: Linux, macOS, Windows
- Three PNG export methods (Pillow → PostScript+PIL → CLI fallback)
- No external dependencies required (Pillow optional but recommended)

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3 + tkinter | Usually bundled with Python. On Ubuntu: `sudo apt install python3-tk` |
| Pillow (recommended) | `pip install pillow` — best PNG quality, no screen capture needed |
| Display / GUI | Needed to show the window. Works on desktop Linux, macOS, Windows. On headless Linux: requires X11 forwarding (`ssh -X`) or a running display. |

## Install

```bash
git clone https://github.com/yancx1998/claude-draw-skill
cd claude-draw-skill
bash install.sh
```

That copies two files:
- `~/.claude/draw_sketch.py` — the sketchpad app
- `~/.claude/commands/draw.md` — the Claude Code slash command

## Usage

In Claude Code, type:

```
/draw
```

A sketchpad window opens. Draw, then click **Done**. Claude sees the image and asks what to do with it.

## How it works

The skill (`commands/draw.md`) tells Claude to run `draw_sketch.py`, wait for it to exit, then read and display the saved PNG. PNG export priority:

1. **Pillow ImageDraw** — draws to both tkinter canvas and a PIL image in parallel; saves directly (no screen capture, works everywhere)
2. **PostScript + PIL** — exports canvas as EPS, converts via PIL + Ghostscript
3. **CLI fallback** — uses `convert` (ImageMagick) or `gs` (Ghostscript)

## License

MIT
