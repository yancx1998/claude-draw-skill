# /screenshot Skill Design

**Date:** 2026-06-15
**Repo:** claude-draw-skill

---

## Purpose

A `/screenshot` slash command for Claude Code that captures a user-selected screen region, lets the user annotate it with drawing tools, then loads the result into the conversation.

Distinct from `/draw` (blank canvas). This tool starts with real screen content.

---

## Components

### 1. `screenshot_tool.py`

Two-phase flow in a single script:

**Phase 1 — Region select:**
- Show a transparent fullscreen tkinter window with crosshair cursor
- User clicks and drags to select a rectangle
- On release: capture that region as a PIL image using `ImageGrab.grab(bbox=...)`
- On Linux without PIL screen capture: fall back to `scrot -s` CLI

**Phase 2 — Annotation:**
- Open a new tkinter window sized to the captured region
- Display the screenshot as the canvas background (PhotoImage)
- Toolbar: color picker (black, red, blue, green, orange, white), brush size slider (1–20), eraser, clear, Done
- Mirror all strokes to a PIL ImageDraw overlay for reliable PNG export
- On Done: composite overlay onto screenshot background, save to output path, close

**Output:** `/tmp/claude_screenshot.png` (Linux/macOS) or `%TEMP%\claude_screenshot.png` (Windows)

**Prerequisites:**
- Python 3 + tkinter (required)
- Pillow (required — for screen capture and PNG export)
- Linux region select: `python3-xlib` or `scrot` CLI fallback

### 2. `commands/screenshot.md`

Tells Claude to:
1. Run `python3 ~/.claude/screenshot_tool.py` (auto-sets DISPLAY on Linux)
2. Wait for exit (user clicks Done)
3. Read `/tmp/claude_screenshot.png`
4. Display it and say "Screenshot received — what would you like me to do with it?"

### 3. `install.sh` (updated)

Copies both `draw_sketch.py` and `screenshot_tool.py` to `~/.claude/` and both command files to `~/.claude/commands/`.

---

## Error Handling

| Failure | Behavior |
|---|---|
| Pillow not installed | Print clear install message and exit |
| No DISPLAY on Linux | Auto-set `DISPLAY=:0`; if still fails, print message |
| scrot not found (Linux fallback) | Print `sudo apt install scrot` and exit |
| User presses Escape during select | Exit cleanly with no file saved |

---

## Out of Scope

- Delay timer (capture after N seconds)
- Auto-describe image content (user loads it, then asks Claude manually)
- Window/app-specific capture
