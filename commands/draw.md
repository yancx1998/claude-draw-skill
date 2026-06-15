Launch the sketchpad and load the result into the conversation.

Steps:
1. Run the sketchpad using the Bash tool. Detect OS and pick the right command:
   - Linux/macOS: `python3 ~/.claude/draw_sketch.py`
   - Windows: `python %USERPROFILE%\.claude\draw_sketch.py`
   The script auto-sets DISPLAY on Linux if needed. Wait for it to exit (user clicks Done).
2. Read the saved image using the Read tool:
   - Linux/macOS: `/tmp/claude_sketch.png`
   - Windows: `%TEMP%\claude_sketch.png`
   Display it so the user can see it was captured.
3. Say "Sketch received — what would you like me to do with it?"
