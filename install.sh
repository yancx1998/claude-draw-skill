#!/usr/bin/env bash
# Install the /draw skill for Claude Code
set -e

DEST="$HOME/.claude"
mkdir -p "$DEST/commands"

cp draw_sketch.py "$DEST/draw_sketch.py"
cp commands/draw.md "$DEST/commands/draw.md"

echo "Installed!"
echo "  Script : $DEST/draw_sketch.py"
echo "  Command: $DEST/commands/draw.md"
echo ""
echo "Optional: install Pillow for best PNG quality:"
echo "  pip install pillow"
echo ""
echo "Use /draw in Claude Code to open the sketchpad."
