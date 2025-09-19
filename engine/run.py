import os
import sys

from app import App
from shape import Triangle, Cube

if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

from OpenGL import GL

# fmt: off
def main():
    app = App() # App must init before init shapes

    shape_dir = "./shape"
    triangle = Triangle("./shape/triangle/triangle.vert", "./shape/triangle/triangle.frag")
    cube = Cube("./shape/cube/cube.vert", "./shape/cube/cube.frag")

    app.add_shape(cube)

    app.run()


if __name__ == "__main__":
    main()
