import unittest

from pixelagent.canvas import PixelCanvas
from pixelagent.render import render_png, render_annotated, render_swatch


class TestRenderPng(unittest.TestCase):
    def _canvas(self):
        c = PixelCanvas(4, 4)
        red = c.palette.add("#ff0000", "red")
        c.pixel(1, 1, red)
        return c, red

    def test_output_size_matches_scale(self):
        c, _ = self._canvas()
        img = render_png(c, scale=10)
        self.assertEqual(img.size, (40, 40))
        self.assertEqual(img.mode, "RGBA")

    def test_set_pixel_renders_its_color(self):
        c, _ = self._canvas()
        img = render_png(c, scale=10)
        self.assertEqual(img.getpixel((15, 15)), (255, 0, 0, 255))  # center of cell (1,1)

    def test_transparent_index_is_transparent(self):
        c, _ = self._canvas()
        img = render_png(c, scale=10)
        self.assertEqual(img.getpixel((5, 5))[3], 0)  # cell (0,0) untouched

    def test_grid_overlay_does_not_change_size(self):
        c, _ = self._canvas()
        img = render_png(c, scale=10, grid=True)
        self.assertEqual(img.size, (40, 40))


class TestAnnotated(unittest.TestCase):
    def test_annotated_adds_margin_for_coordinate_labels(self):
        c = PixelCanvas(4, 4)
        img = render_annotated(c, scale=10, margin=20, every=2)
        self.assertEqual(img.size, (4 * 10 + 20, 4 * 10 + 20))


class TestSwatch(unittest.TestCase):
    def test_swatch_has_one_row_per_palette_entry(self):
        c = PixelCanvas(1, 1)
        c.palette.add("#ff0000")
        c.palette.add("#00ff00")
        img = render_swatch(c.palette, cell=12)
        self.assertEqual(img.size[1], 12 * len(c.palette))


if __name__ == "__main__":
    unittest.main()
