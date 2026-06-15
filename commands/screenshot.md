Capture a screen region, annotate it, and load the result into the conversation.

Steps:
1. Run the screenshot tool using the Bash tool:
   - Linux/macOS: `python3 ~/.claude/screenshot_tool.py`
   - Windows: `python %USERPROFILE%\.claude\screenshot_tool.py`
   The script auto-sets DISPLAY on Linux if needed. A fullscreen overlay appears — drag to select a region, then annotate in the window that opens. Click Done when finished.
2. Read the saved image using the Read tool:
   - Linux/macOS: `/tmp/claude_screenshot.png`
   - Windows: look for the path printed in step 1 output
   Display it so the user can see it was captured.
3. Say "Screenshot received — what would you like me to do with it?"
