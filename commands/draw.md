---
description: Launch a sketchpad and load your drawing into the conversation.
allowed-tools: [Bash, Read, Write]
---
Launch the sketchpad and load the result into the conversation.

Steps:

1. Check if the sketchpad script exists:
   Run via Bash: `test -f ~/.claude/draw_sketch.py && echo EXISTS || echo MISSING`

   If MISSING, write `~/.claude/draw_sketch.py` using the Write tool with this exact content:

```python
#!/usr/bin/env python3
"""Sketchpad for Claude Code /draw skill.
Saves canvas as PNG when user clicks Done.
Works on Linux, macOS, and Windows.
"""
import os
import sys
import platform
import tempfile

# Auto-set DISPLAY on Linux if not already set (e.g. SSH session with physical display)
if platform.system() == "Linux" and "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0"

import tkinter as tk

OUTPUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "claude_sketch.png")


class Sketchpad:
    def __init__(self, root):
        self.root = root
        root.title("Sketch for Claude  —  click Done when finished")
        root.resizable(True, True)

        self.color = "black"
        self.size = 3
        self.last = None
        self.eraser = False

        self._pil_image = None
        self._pil_draw = None
        self._init_pil(800, 600)

        bar = tk.Frame(root, bg="#f0f0f0", pady=4)
        bar.pack(fill=tk.X)

        colors = ["black", "red", "blue", "green", "orange", "purple", "white"]
        for c in colors:
            b = tk.Button(bar, bg=c, width=2, relief=tk.RAISED,
                          command=lambda c=c: self.set_color(c))
            b.pack(side=tk.LEFT, padx=2)

        tk.Label(bar, text="  Size:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.size_var = tk.IntVar(value=3)
        tk.Scale(bar, from_=1, to=20, orient=tk.HORIZONTAL,
                 variable=self.size_var, length=100, bg="#f0f0f0",
                 command=lambda v: setattr(self, "size", int(v))
                 ).pack(side=tk.LEFT)

        tk.Button(bar, text="Eraser", command=self.toggle_eraser,
                  relief=tk.RAISED).pack(side=tk.LEFT, padx=6)
        tk.Button(bar, text="Clear", command=self.clear,
                  bg="#ffdddd").pack(side=tk.LEFT, padx=2)

        tk.Button(bar, text="  Done  ", command=self.done,
                  bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                  relief=tk.RAISED).pack(side=tk.RIGHT, padx=8)

        self.canvas = tk.Canvas(root, width=800, height=600, bg="white",
                                cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda e: setattr(self, "last", None))
        self.canvas.bind("<Configure>", self._on_resize)

    def _init_pil(self, w, h):
        try:
            from PIL import Image, ImageDraw
            self._pil_image = Image.new("RGB", (w, h), "white")
            self._pil_draw = ImageDraw.Draw(self._pil_image)
        except ImportError:
            self._pil_image = None
            self._pil_draw = None

    def _on_resize(self, event):
        if self._pil_image is None:
            return
        w, h = event.width, event.height
        if w != self._pil_image.width or h != self._pil_image.height:
            from PIL import Image
            new_img = Image.new("RGB", (w, h), "white")
            new_img.paste(self._pil_image, (0, 0))
            from PIL import ImageDraw
            self._pil_image = new_img
            self._pil_draw = ImageDraw.Draw(self._pil_image)

    def set_color(self, c):
        self.color = c
        self.eraser = False

    def toggle_eraser(self):
        self.eraser = not self.eraser

    def clear(self):
        self.canvas.delete("all")
        if self._pil_draw:
            w = self._pil_image.width
            h = self._pil_image.height
            self._pil_draw.rectangle([0, 0, w, h], fill="white")

    def on_press(self, e):
        self.last = (e.x, e.y)

    def on_drag(self, e):
        if self.last is None:
            return
        c = "white" if self.eraser else self.color
        s = self.size_var.get() * (4 if self.eraser else 1)

        self.canvas.create_line(self.last[0], self.last[1], e.x, e.y,
                                fill=c, width=s, capstyle=tk.ROUND, smooth=True)

        if self._pil_draw:
            self._pil_draw.line([self.last, (e.x, e.y)], fill=c, width=s)

        self.last = (e.x, e.y)

    def done(self):
        saved = False

        if self._pil_image:
            try:
                self._pil_image.save(OUTPUT)
                saved = True
            except Exception:
                pass

        if not saved:
            try:
                import tempfile, os
                from PIL import Image
                ps = tempfile.mktemp(suffix=".eps")
                self.canvas.postscript(file=ps, colormode="color")
                img = Image.open(ps)
                img.save(OUTPUT)
                os.unlink(ps)
                saved = True
            except Exception:
                pass

        if not saved:
            try:
                import tempfile, os, subprocess
                ps = tempfile.mktemp(suffix=".eps")
                self.canvas.postscript(file=ps, colormode="color")
                result = subprocess.run(["convert", ps, OUTPUT], capture_output=True)
                if result.returncode != 0:
                    subprocess.run(
                        ["gs", "-dNOPAUSE", "-dBATCH", "-sDEVICE=png16m",
                         f"-sOutputFile={OUTPUT}", ps],
                        capture_output=True
                    )
                os.unlink(ps)
                saved = True
            except Exception:
                pass

        if not saved:
            print(f"Warning: could not save PNG. Install Pillow: pip install pillow", file=sys.stderr)

        self.root.destroy()


root = tk.Tk()
app = Sketchpad(root)
root.mainloop()
```

2. Run the sketchpad:
   - Linux/macOS: `python3 ~/.claude/draw_sketch.py`
   - Windows: `python %USERPROFILE%\.claude\draw_sketch.py`
   Wait for it to exit (user clicks Done).

3. Read the saved image using the Read tool:
   - Linux/macOS: `/tmp/claude_sketch.png`
   - Windows: look for the path printed in step 2 output
   Display it so the user can see it.

4. Say "Sketch received — what would you like me to do with it?"
