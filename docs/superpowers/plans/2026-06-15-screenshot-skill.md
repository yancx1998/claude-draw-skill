# /screenshot Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `/screenshot` Claude Code slash command that captures a user-selected screen region, lets the user annotate it with drawing tools, then loads the result into the conversation.

**Architecture:** A single Python script (`screenshot_tool.py`) runs in two phases — first a fullscreen tkinter overlay showing the live screen for region selection (drag to select), then an annotation window with the cropped screenshot as background and the same toolbar as `/draw`. A command file (`commands/screenshot.md`) tells Claude to run the script and read the result.

**Tech Stack:** Python 3, tkinter, Pillow (required), scrot CLI (Linux fallback for full-screen grab)

---

### Task 1: Full-screen capture utility

**Files:**
- Create: `screenshot_tool.py`

The capture approach: grab a full screenshot silently first, then show it as a fullscreen tkinter window so the user can drag to select a region — no transparency compositing needed.

- [ ] **Step 1: Create `screenshot_tool.py` with screen grab helper**

```python
#!/usr/bin/env python3
"""screenshot_tool.py — region select + annotate for Claude Code /screenshot skill."""
import os, sys, platform, tempfile

if platform.system() == "Linux" and "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0"

OUTPUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "claude_screenshot.png")

def grab_full_screen():
    """Capture full screen as PIL Image. Tries Pillow first, scrot on Linux as fallback."""
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        if img:
            return img
    except Exception:
        pass
    # Linux fallback: scrot
    import subprocess
    tmp = tempfile.mktemp(suffix=".png")
    result = subprocess.run(["scrot", tmp], capture_output=True)
    if result.returncode != 0:
        print("Error: Pillow ImageGrab failed and scrot not found.")
        print("Install scrot: sudo apt install scrot")
        sys.exit(1)
    from PIL import Image
    img = Image.open(tmp)
    os.unlink(tmp)
    return img

if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk, ImageDraw
    except ImportError:
        print("Error: Pillow is required. Install it with: pip install pillow")
        sys.exit(1)
    full_img = grab_full_screen()
    print(f"Screen captured: {full_img.size}")
```

- [ ] **Step 2: Verify it runs without error**

```bash
cd /tmp/claude-draw-skill
python3 screenshot_tool.py /tmp/test_ss.png
```
Expected output: `Screen captured: (WWWW, HHHH)` — no errors, no file saved yet (annotation window not built yet).

- [ ] **Step 3: Commit**

```bash
git add screenshot_tool.py
git commit -m "feat: screenshot_tool.py - full screen grab utility"
```

---

### Task 2: Region selection overlay

**Files:**
- Modify: `screenshot_tool.py`

Show the full screenshot as a fullscreen tkinter window. User drags to select a rectangle. On mouse release, crop the image and close the window.

- [ ] **Step 1: Add `RegionSelector` class to `screenshot_tool.py` after `grab_full_screen()`**

```python
import tkinter as tk

class RegionSelector:
    """Fullscreen overlay showing the screenshot; user drags to select a region."""

    def __init__(self, full_img):
        self.full_img = full_img
        self.region = None  # (x1, y1, x2, y2) in original image coords
        self._start = None
        self._rect_id = None

        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(cursor="crosshair")
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        # Scale image to screen size for display (may differ on HiDPI)
        display_img = full_img.resize((sw, sh))
        self._tk_img = ImageTk.PhotoImage(display_img)
        self._scale_x = full_img.width / sw
        self._scale_y = full_img.height / sh

        self.canvas = tk.Canvas(self.root, width=sw, height=sh, cursor="crosshair",
                                highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self._tk_img)

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        # Instruction label
        self.canvas.create_text(sw // 2, 30, text="Drag to select region  •  Esc to cancel",
                                fill="white", font=("Arial", 14, "bold"),
                                tags="hint")

    def _on_press(self, e):
        self._start = (e.x, e.y)
        if self._rect_id:
            self.canvas.delete(self._rect_id)

    def _on_drag(self, e):
        if self._start is None:
            return
        if self._rect_id:
            self.canvas.delete(self._rect_id)
        self._rect_id = self.canvas.create_rectangle(
            self._start[0], self._start[1], e.x, e.y,
            outline="red", width=2, dash=(4, 4)
        )

    def _on_release(self, e):
        if self._start is None:
            return
        x1 = int(min(self._start[0], e.x) * self._scale_x)
        y1 = int(min(self._start[1], e.y) * self._scale_y)
        x2 = int(max(self._start[0], e.x) * self._scale_x)
        y2 = int(max(self._start[1], e.y) * self._scale_y)
        if x2 - x1 < 10 or y2 - y1 < 10:
            return  # too small, ignore
        self.region = (x1, y1, x2, y2)
        self.root.destroy()

    def run(self):
        self.root.mainloop()
        return self.region
```

- [ ] **Step 2: Wire `RegionSelector` into `__main__` block**

Replace the `print` line at the end of `__main__` with:

```python
    selector = RegionSelector(full_img)
    region = selector.run()

    if region is None:
        print("Selection cancelled.")
        sys.exit(0)

    screenshot = full_img.crop(region)
    print(f"Region selected: {region}, size: {screenshot.size}")
```

- [ ] **Step 3: Test region selection**

```bash
python3 screenshot_tool.py /tmp/test_ss.png
```
Expected: fullscreen overlay appears showing your desktop, drag selects a region with red dashed rectangle, window closes, terminal prints `Region selected: (x1, y1, x2, y2), size: (W, H)`.

- [ ] **Step 4: Commit**

```bash
git add screenshot_tool.py
git commit -m "feat: region selection overlay with drag-to-select"
```

---

### Task 3: Annotation window

**Files:**
- Modify: `screenshot_tool.py`

Open a tkinter window with the cropped screenshot as background. Same toolbar as `draw_sketch.py`. Mirror strokes to a PIL overlay. On Done: composite overlay onto screenshot, save PNG.

- [ ] **Step 1: Add `Annotator` class after `RegionSelector`**

```python
class Annotator:
    """Annotation window — screenshot as background, draw tools on top."""

    def __init__(self, screenshot):
        self.screenshot = screenshot.copy()
        self.last = None
        self.eraser = False
        self.color = "red"
        self.size = 3

        # PIL overlay for reliable PNG export (transparent background)
        from PIL import ImageDraw
        self._overlay = Image.new("RGBA", screenshot.size, (0, 0, 0, 0))
        self._draw = ImageDraw.Draw(self._overlay)

        w, h = screenshot.size
        self.root = tk.Tk()
        self.root.title("Annotate — click Done when finished")
        self.root.resizable(True, True)

        # --- toolbar ---
        bar = tk.Frame(self.root, bg="#f0f0f0", pady=4)
        bar.pack(fill=tk.X)

        colors = ["black", "red", "blue", "green", "orange", "white"]
        for c in colors:
            tk.Button(bar, bg=c, width=2, relief=tk.RAISED,
                      command=lambda c=c: self.set_color(c)).pack(side=tk.LEFT, padx=2)

        tk.Label(bar, text="  Size:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.size_var = tk.IntVar(value=3)
        tk.Scale(bar, from_=1, to=20, orient=tk.HORIZONTAL,
                 variable=self.size_var, length=100, bg="#f0f0f0",
                 command=lambda v: setattr(self, "size", int(v))).pack(side=tk.LEFT)

        tk.Button(bar, text="Eraser", command=self.toggle_eraser,
                  relief=tk.RAISED).pack(side=tk.LEFT, padx=6)
        tk.Button(bar, text="Clear", command=self.clear,
                  bg="#ffdddd").pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="  Done  ", command=self.done,
                  bg="#4CAF50", fg="white", font=("Arial", 11, "bold")).pack(side=tk.RIGHT, padx=8)

        # --- canvas with screenshot background ---
        self._tk_bg = ImageTk.PhotoImage(screenshot)
        self.canvas = tk.Canvas(self.root, width=w, height=h, cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self._tk_bg)

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda e: setattr(self, "last", None))

    def set_color(self, c):
        self.color = c
        self.eraser = False

    def toggle_eraser(self):
        self.eraser = not self.eraser

    def clear(self):
        self.canvas.delete("drawings")
        from PIL import ImageDraw
        self._overlay = Image.new("RGBA", self.screenshot.size, (0, 0, 0, 0))
        self._draw = ImageDraw.Draw(self._overlay)

    def _on_press(self, e):
        self.last = (e.x, e.y)

    def _on_drag(self, e):
        if self.last is None:
            return
        c = "white" if self.eraser else self.color
        s = self.size_var.get() * (4 if self.eraser else 1)
        self.canvas.create_line(self.last[0], self.last[1], e.x, e.y,
                                fill=c, width=s, capstyle=tk.ROUND,
                                smooth=True, tags="drawings")
        if not self.eraser:
            self._draw.line([self.last, (e.x, e.y)], fill=c, width=s)
        else:
            # erase by painting white on overlay
            self._draw.line([self.last, (e.x, e.y)], fill=(255, 255, 255, 255), width=s)
        self.last = (e.x, e.y)

    def done(self):
        # Composite: screenshot (RGB) + overlay (RGBA)
        base = self.screenshot.convert("RGBA")
        composite = Image.alpha_composite(base, self._overlay)
        composite.convert("RGB").save(OUTPUT)
        self.root.destroy()

    def run(self):
        self.root.mainloop()
```

- [ ] **Step 2: Wire `Annotator` into `__main__` block**

After the `screenshot = full_img.crop(region)` line, add:

```python
    annotator = Annotator(screenshot)
    annotator.run()

    if os.path.exists(OUTPUT):
        print(f"Saved to {OUTPUT}")
    else:
        print("Cancelled — no file saved.")
```

- [ ] **Step 3: Test the full flow end-to-end**

```bash
python3 screenshot_tool.py /tmp/test_ss.png
```
Expected:
1. Fullscreen overlay → drag to select a region → window closes
2. Annotation window opens showing the cropped screenshot
3. Draw some red marks → click Done
4. Terminal prints `Saved to /tmp/test_ss.png`
5. Open `/tmp/test_ss.png` — should show annotated screenshot

```bash
eog /tmp/test_ss.png   # or: xdg-open /tmp/test_ss.png
```

- [ ] **Step 4: Commit**

```bash
git add screenshot_tool.py
git commit -m "feat: annotation window with screenshot background and draw tools"
```

---

### Task 4: Command file

**Files:**
- Create: `commands/screenshot.md`

- [ ] **Step 1: Create `commands/screenshot.md`**

```markdown
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
```

- [ ] **Step 2: Install and test the command**

```bash
cp screenshot_tool.py ~/.claude/screenshot_tool.py
cp commands/screenshot.md ~/.claude/commands/screenshot.md
```

Then open Claude Code and type `/screenshot` — verify the full flow works.

- [ ] **Step 3: Commit**

```bash
git add commands/screenshot.md
git commit -m "feat: /screenshot command file"
```

---

### Task 5: Update install.sh and README

**Files:**
- Modify: `install.sh`
- Modify: `README.md`

- [ ] **Step 1: Update `install.sh` to include screenshot files**

Replace the content of `install.sh` with:

```bash
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
echo "  /draw      → $DEST/draw_sketch.py"
echo "  /screenshot → $DEST/screenshot_tool.py"
echo ""
echo "Required: pip install pillow"
echo "Linux only: sudo apt install scrot  (fallback if Pillow ImageGrab fails)"
echo ""
echo "Use /draw or /screenshot in Claude Code."
```

- [ ] **Step 2: Update README.md**

Add a `/screenshot` section after the `/draw` usage section:

```markdown
## /screenshot

Capture a region of your screen, annotate it, and send it to Claude.

```
/screenshot
```

1. A fullscreen overlay shows your desktop — drag to select a region
2. The selected region opens in an annotation window (same tools as /draw)
3. Click **Done** — Claude sees the annotated screenshot

**Extra requirement on Linux:** `sudo apt install scrot` (only needed if Pillow's ImageGrab fails on your system)
```

- [ ] **Step 3: Commit and push**

```bash
git add install.sh README.md
git commit -m "feat: update install.sh and README for /screenshot"
git push
```

---

## Self-Review

**Spec coverage:**
- ✅ Region select via fullscreen drag overlay — Task 2
- ✅ Annotation with colors, size, eraser — Task 3
- ✅ Pillow required, scrot fallback on Linux — Task 1
- ✅ Output to `/tmp/claude_screenshot.png` — Task 1 (`OUTPUT` var)
- ✅ Command file loads result into conversation — Task 4
- ✅ Escape to cancel — Task 2 (`<Escape>` binding)
- ✅ Install script updated — Task 5

**No placeholders found.**

**Type consistency:** `Image`, `ImageTk`, `ImageDraw` all imported from `PIL` consistently. `OUTPUT` global used in both `Annotator.done()` and `__main__`. `self._overlay` and `self._draw` stay in sync via `clear()`.
