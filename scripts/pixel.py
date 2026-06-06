#!/usr/bin/env python3
"""Path-based launcher for the pixel-agent studio.

Lets the skill run the engine from a plugin install with no PYTHONPATH setup:

    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pixel.py" <workdir> <program.txt> \
        --w 32 --h 32 --scale 16 --every 4 --reset

It puts the plugin root (this file's grandparent) on sys.path, then runs the studio CLI.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pixelagent.studio import _main  # noqa: E402

if __name__ == "__main__":
    _main()
