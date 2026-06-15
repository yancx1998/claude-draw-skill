#!/usr/bin/env bash
# Install /draw and /screenshot skills for Claude Code
set -e

DEST="$HOME/.claude"
mkdir -p "$DEST/commands"

cp draw_sketch.py "$DEST/draw_sketch.py"
cp screenshot_tool.py "$DEST/screenshot_tool.py"
cp commands/draw.md "$DEST/commands/draw.md"
cp commands/screenshot.md "$DEST/commands/screenshot.md"

echo "Installed!"
echo "  /draw       -> $DEST/draw_sketch.py"
echo "  /screenshot -> $DEST/screenshot_tool.py"
echo ""
echo "Required for /screenshot: pip install pillow"
echo "Linux only (fallback): sudo apt install scrot"
echo ""
echo "Optional for /draw: pip install pillow"
echo ""
echo "Use /draw or /screenshot in Claude Code."
