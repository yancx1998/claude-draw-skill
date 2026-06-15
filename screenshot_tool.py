#!/usr/bin/env python3
"""screenshot_tool.py — region select + annotate for Claude Code /screenshot skill."""
import os
import sys
import platform
import tempfile

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


import tkinter as tk


class RegionSelector:
    """Fullscreen overlay showing the screenshot; user drags to select a region."""

    def __init__(self, full_img):
        from PIL import ImageTk
        self.full_img = full_img
        self.region = None
        self._start = None
        self._rect_id = None

        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(cursor="crosshair")
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        display_img = full_img.resize((sw, sh))
        self._tk_img = ImageTk.PhotoImage(display_img)
        self._scale_x = full_img.width / sw
        self._scale_y = full_img.height / sh

        self.canvas = tk.Canvas(self.root, width=sw, height=sh,
                                cursor="crosshair", highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self._tk_img)

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        self.canvas.create_text(sw // 2, 30,
                                text="Drag to select region  •  Esc to cancel",
                                fill="white", font=("Arial", 14, "bold"))

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
            return
        self.region = (x1, y1, x2, y2)
        self.root.destroy()

    def run(self):
        self.root.mainloop()
        return self.region


class Annotator:
    """Annotation window — screenshot as background, draw tools on top."""

    def __init__(self, screenshot):
        from PIL import Image, ImageTk, ImageDraw
        self.screenshot = screenshot.copy()
        self.last = None
        self.eraser = False
        self.color = "red"
        self.size = 3

        self._overlay = Image.new("RGBA", screenshot.size, (0, 0, 0, 0))
        self._draw = ImageDraw.Draw(self._overlay)

        w, h = screenshot.size
        self.root = tk.Tk()
        self.root.title("Annotate  —  click Done when finished")
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
                  bg="#4CAF50", fg="white",
                  font=("Arial", 11, "bold")).pack(side=tk.RIGHT, padx=8)

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
        from PIL import Image, ImageDraw
        self.canvas.delete("drawings")
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
            self._draw.line([self.last, (e.x, e.y)],
                            fill=(255, 255, 255, 255), width=s)
        self.last = (e.x, e.y)

    def done(self):
        from PIL import Image
        base = self.screenshot.convert("RGBA")
        composite = Image.alpha_composite(base, self._overlay)
        composite.convert("RGB").save(OUTPUT)
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk, ImageDraw
    except ImportError:
        print("Error: Pillow is required. Install it with: pip install pillow")
        sys.exit(1)

    full_img = grab_full_screen()

    selector = RegionSelector(full_img)
    region = selector.run()

    if region is None:
        print("Selection cancelled.")
        sys.exit(0)

    screenshot = full_img.crop(region)

    annotator = Annotator(screenshot)
    annotator.run()

    if os.path.exists(OUTPUT):
        print(f"Saved to {OUTPUT}")
    else:
        print("Cancelled — no file saved.")
