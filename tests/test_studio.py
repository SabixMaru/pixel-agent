import os
import tempfile
import unittest

from pixelagent.studio import Studio


class TestStudio(unittest.TestCase):
    def test_apply_then_render_writes_outputs_and_persists_canvas(self):
        wd = os.path.join(tempfile.mkdtemp(), "cat")
        s = Studio(wd, width=8, height=8, scale=8)
        s.apply("color #ff0000 red\nrect 1 1 6 6 1 fill")
        paths = s.render(every=2)
        for p in paths.values():
            self.assertTrue(os.path.exists(p), f"missing {p}")
        # a fresh Studio on the same dir reloads the persisted canvas
        reloaded = Studio(wd, width=8, height=8, scale=8)
        self.assertEqual(reloaded.canvas.get(3, 3), 1)


if __name__ == "__main__":
    unittest.main()
