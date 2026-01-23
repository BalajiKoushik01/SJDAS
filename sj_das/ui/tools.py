from PyQt6.QtCore import QPoint, Qt


# --- BASE TOOL ---
class Tool:
    def __init__(self, editor):
        self.editor = editor

    def mouse_press(self, pos, buttons): pass
    def mouse_move(self, pos, buttons): pass
    def mouse_release(self, pos, buttons): pass

# --- BRUSH TOOL (Bresenham + Thickness) ---


class BrushTool(Tool):
    def __init__(self, editor, is_eraser=False):
        super().__init__(editor)
        self.is_eraser = is_eraser
        self.last_pos = None

    def mouse_press(self, pos, buttons):
        self.editor._start_stroke()
        self.last_pos = pos
        self.draw(pos)

    def mouse_move(self, pos, buttons):
        self.draw_line(self.last_pos, pos)
        self.last_pos = pos

    def mouse_release(self, pos, buttons):
        self.editor._end_stroke("Eraser" if self.is_eraser else "Brush")
        self.last_pos = None

    def draw(self, pos):
        # Draw single point (circle/square based on brush size)
        self.editor._draw_pixel_circle(
            pos, self.editor.brush_size, self.is_eraser)

    def draw_line(self, p0, p1):
        # Bresenham / Interpolation
        x0, y0 = int(p0.x()), int(p0.y())
        x1, y1 = int(p1.x()), int(p1.y())

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = abs(y1 - y0)
        error = dx / 2
        ystep = 1 if y0 < y1 else -1
        y = y0

        for x in range(x0, x1 + 1):
            coord = QPoint(y, x) if steep else QPoint(x, y)
            self.draw(coord)
            error -= dy
            if error < 0:
                y += ystep
                error += dx

# --- FILL TOOL (Scanline) ---


class FillTool(Tool):
    def mouse_press(self, pos, buttons):
        self.editor._start_stroke()
        # Delegate to editor's robust fill for now, or move logic here
        self.editor._fill(pos, buttons & Qt.MouseButton.RightButton)
        self.editor._end_stroke("Fill")

# --- RECTANGLE TOOL ---


class RectTool(Tool):
    def __init__(self, editor):
        super().__init__(editor)
        self.start_pos = None
        self.preview_item = None

    def mouse_press(self, pos, buttons):
        self.start_pos = pos
        self.editor._start_stroke()

    def mouse_move(self, pos, buttons):
        # Show specific preview if needed
        pass

    def mouse_release(self, pos, buttons):
        # Commit Shape
        is_eraser = buttons & Qt.MouseButton.RightButton
        self.editor._draw_rect_shape(self.start_pos, pos, is_eraser)
        self.editor._end_stroke("Rectangle")
