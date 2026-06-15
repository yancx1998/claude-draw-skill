# claudecode-draw

A Claude Code plugin that opens a sketchpad canvas so you can draw, annotate, or diagram — then loads your sketch directly into the conversation.

## Install via Claude Code

```
/plugin install claudecode-draw@claude-plugins-official
```

Or browse for it in `/plugin > Discover`.

## Manual install

```bash
git clone https://github.com/yancx1998/claudecode-draw
mkdir -p ~/.claude/commands
cp claudecode-draw/commands/draw.md ~/.claude/commands/draw.md
```

The Python sketchpad script is self-bootstrapping — it will be written to `~/.claude/draw_sketch.py` automatically on first use.

## Usage

Type `/draw` in Claude Code. A canvas opens — draw freely, pick colors, adjust brush size. Click **Done** when finished; the sketch loads into the conversation automatically.

## Requirements

- Python 3 with tkinter (standard library)
- Optional: `pip install pillow` for better PNG export

## Linux

The script auto-sets `DISPLAY=:0` if running in an SSH session with a physical display available.
