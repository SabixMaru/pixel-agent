import os
import tempfile
import unittest

from PIL import Image

from pixelagent.animation import contact_sheet, export_gif, export_spritesheet, onion_skin
from pixelagent.canvas import PixelCanvas


class TestAnimation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def _frame(self, i):
        c = PixelCanvas(4, 4)
        col = c.palette.add("#ffffff", "w")
        c.pixel(i % 4, 0, col)
        return c

    def test_export_gif_has_correct_frame_count(self):
        frames = [self._frame(i) for i in range(4)]
        path = os.path.join(self.tmp, "a.gif")
        export_gif(frames, path, scale=4, fps=8)
        with Image.open(path) as im:
            self.assertEqual(getattr(im, "n_frames", 1), 4)

    def test_spritesheet_lays_frames_in_a_row(self):
        frames = [self._frame(i) for i in range(3)]
        path = os.path.join(self.tmp, "sheet.png")
        export_spritesheet(frames, path, scale=4)
        with Image.open(path) as im:
            self.assertEqual(im.size, (3 * 16, 16))  # 3 frames, each 4px * scale4

    def test_contact_sheet_dimensions(self):
        frames = [self._frame(i) for i in range(2)]
        img = contact_sheet(frames, scale=4, pad=2)
        self.assertEqual(img.mode, "RGBA")
        self.assertEqual(img.size, (2 * 16 + 3 * 2, 16 + 2 * 2))

    def test_onion_skin_size_matches_current_frame(self):
        img = onion_skin(self._frame(0), self._frame(1), scale=4)
        self.assertEqual(img.size, (16, 16))
        self.assertEqual(img.mode, "RGBA")


if __name__ == "__main__":
    unittest.main()
