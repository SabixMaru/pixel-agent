import unittest

from pixelagent.canvas import PixelCanvas, Palette


class TestPalette(unittest.TestCase):
    def test_index_zero_is_transparent(self):
        p = Palette()
        self.assertEqual(p.rgba(0), (0, 0, 0, 0))

    def test_add_returns_incrementing_indices(self):
        p = Palette()
        self.assertEqual(p.add("#ff0000", "red"), 1)
        self.assertEqual(p.add("#00ff00", "green"), 2)

    def test_rgba_parses_hex(self):
        p = Palette()
        idx = p.add("#ff8800", "orange")
        self.assertEqual(p.rgba(idx), (255, 136, 0, 255))

    def test_rgba_parses_hex_without_hash(self):
        p = Palette()
        idx = p.add("2b2b2b")
        self.assertEqual(p.rgba(idx), (43, 43, 43, 255))


class TestPixelCanvasBasics(unittest.TestCase):
    def test_new_canvas_is_all_transparent(self):
        c = PixelCanvas(4, 4)
        self.assertEqual((c.width, c.height), (4, 4))
        self.assertTrue(all(c.get(x, y) == 0 for x in range(4) for y in range(4)))

    def test_set_and_get_pixel(self):
        c = PixelCanvas(4, 4)
        c.pixel(1, 2, 5)
        self.assertEqual(c.get(1, 2), 5)

    def test_out_of_bounds_pixel_is_clipped_silently(self):
        c = PixelCanvas(4, 4)
        c.pixel(-1, 0, 3)
        c.pixel(0, 99, 3)
        self.assertEqual(c.get(0, 0), 0)


class TestShapes(unittest.TestCase):
    def test_horizontal_line(self):
        c = PixelCanvas(8, 8)
        c.line(1, 3, 5, 3, 2)
        for x in range(1, 6):
            self.assertEqual(c.get(x, 3), 2)
        self.assertEqual(c.get(0, 3), 0)
        self.assertEqual(c.get(6, 3), 0)

    def test_diagonal_line_endpoints_and_midpoints(self):
        c = PixelCanvas(8, 8)
        c.line(0, 0, 3, 3, 1)
        for i in range(4):
            self.assertEqual(c.get(i, i), 1)

    def test_rect_outline_only(self):
        c = PixelCanvas(6, 6)
        c.rect(1, 1, 4, 4, 3)
        self.assertEqual(c.get(1, 1), 3)
        self.assertEqual(c.get(4, 4), 3)
        self.assertEqual(c.get(2, 1), 3)
        self.assertEqual(c.get(2, 2), 0)

    def test_rect_filled(self):
        c = PixelCanvas(6, 6)
        c.rect(1, 1, 4, 4, 3, filled=True)
        self.assertEqual(c.get(2, 2), 3)
        self.assertEqual(c.get(4, 4), 3)
        self.assertEqual(c.get(0, 0), 0)

    def test_filled_ellipse_center_set_corners_clear(self):
        c = PixelCanvas(9, 9)
        c.ellipse(0, 0, 8, 8, 4, filled=True)
        self.assertEqual(c.get(4, 4), 4)
        self.assertEqual(c.get(0, 0), 0)
        self.assertEqual(c.get(8, 8), 0)

    def test_flood_fill_respects_borders(self):
        c = PixelCanvas(5, 5)
        c.rect(0, 0, 4, 4, 1)
        c.flood_fill(2, 2, 7)
        self.assertEqual(c.get(2, 2), 7)
        self.assertEqual(c.get(1, 1), 7)
        self.assertEqual(c.get(0, 0), 1)

    def test_mirror_h_copies_left_half_to_right(self):
        c = PixelCanvas(4, 2)
        c.pixel(0, 0, 5)
        c.pixel(1, 1, 6)
        c.mirror_h()
        self.assertEqual(c.get(3, 0), 5)
        self.assertEqual(c.get(2, 1), 6)


class TestPersistence(unittest.TestCase):
    def test_json_round_trip(self):
        c = PixelCanvas(3, 3)
        c.palette.add("#ff0000", "red")
        c.pixel(1, 1, 1)
        c2 = PixelCanvas.from_dict(c.to_dict())
        self.assertEqual((c2.width, c2.height), (3, 3))
        self.assertEqual(c2.get(1, 1), 1)
        self.assertEqual(c2.palette.rgba(1), (255, 0, 0, 255))


if __name__ == "__main__":
    unittest.main()
