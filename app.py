import os
import sys
import glfw
import ctypes

import numpy as np

from OpenGL import GL


# # Set platform hint before importing OpenGL
# if sys.platform.startswith("linux"):
#     os.environ.setdefault("PYOPENGL_PLATFORM", "glx")
