import unittest

from pixelagent.canvas import PixelCanvas
from pixelagent.dsl import apply_commands


class TestDSL(unittest.TestCase):
    def test_pixel_command(self):
        c = PixelCanvas(8, 8)
        apply_commands(c, "pixel 2 3 5")
        self.assertEqual(c.get(2, 3), 5)

    def test_full_line_comments_and_blanks_ignored(self):
        c = PixelCanvas(8, 8)
        apply_commands(c, "# a comment\n\n   \npixel 0 0 1\n")
        self.assertEqual(c.get(0, 0), 1)

    def test_color_adds_palette_entry(self):
        c = PixelCanvas(4, 4)
        apply_commands(c, "color #ff0000 red")
        self.assertEqual(c.palette.rgba(1), (255, 0, 0, 255))

    def test_rect_fill_keyword_fills(self):
        c = PixelCanvas(8, 8)
        apply_commands(c, "rect 1 1 4 4 2 fill")
        self.assertEqual(c.get(2, 2), 2)

    def test_rect_without_fill_is_outline(self):
        c = PixelCanvas(8, 8)
        apply_commands(c, "rect 1 1 4 4 2")
        self.assertEqual(c.get(1, 1), 2)
        self.assertEqual(c.get(2, 2), 0)

    def test_ellipse_fill(self):
        c = PixelCanvas(9, 9)
        apply_commands(c, "ellipse 0 0 8 8 3 fill")
        self.assertEqual(c.get(4, 4), 3)

    def test_fill_is_flood_fill(self):
        c = PixelCanvas(5, 5)
        apply_commands(c, "rect 0 0 4 4 1\nfill 2 2 7")
        self.assertEqual(c.get(2, 2), 7)
        self.assertEqual(c.get(0, 0), 1)

    def test_mirror_h(self):
        c = PixelCanvas(4, 2)
        apply_commands(c, "pixel 0 0 5\nmirror_h")
        self.assertEqual(c.get(3, 0), 5)

    def test_outline_command_wraps_the_shape(self):
        c = PixelCanvas(5, 5)
        apply_commands(c, "pixel 2 2 3\noutline 1")
        self.assertEqual(c.get(1, 1), 1)
        self.assertEqual(c.get(2, 2), 3)

    def test_unknown_command_raises_valueerror(self):
        c = PixelCanvas(4, 4)
        with self.assertRaises(ValueError):
            apply_commands(c, "frobnicate 1 2 3")


if __name__ == "__main__":
    unittest.main()
