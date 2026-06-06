import unittest

from pixelagent.canvas import PixelCanvas


class TestOutline(unittest.TestCase):
    def test_outline_surrounds_single_pixel_8_connected(self):
        c = PixelCanvas(5, 5)
        c.pixel(2, 2, 3)
        c.outline(1)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    self.assertEqual(c.get(2 + dx, 2 + dy), 1)
        self.assertEqual(c.get(2, 2), 3)  # original kept

    def test_outline_keeps_interior_fill(self):
        c = PixelCanvas(6, 6)
        c.rect(1, 1, 4, 4, 2, filled=True)
        c.outline(1)
        self.assertEqual(c.get(2, 2), 2)  # interior untouched
        self.assertEqual(c.get(0, 0), 1)  # diagonal corner outside -> outline
        self.assertEqual(c.get(0, 3), 1)  # left of the block -> outline

    def test_outline_orthogonal_skips_diagonals(self):
        c = PixelCanvas(5, 5)
        c.pixel(2, 2, 3)
        c.outline(1, diagonal=False)
        self.assertEqual(c.get(2, 1), 1)
        self.assertEqual(c.get(1, 2), 1)
        self.assertEqual(c.get(1, 1), 0)  # diagonal not outlined


if __name__ == "__main__":
    unittest.main()
