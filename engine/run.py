import os
import sys

if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

from app import App
from shape import Triangle, Cube, Cylinder
from OpenGL import GL

# fmt: off
def main():
    width = 1000
    height = 1000

    app = App(width, height) # App must init before init shapes

    # OpenGL settings - moved after app initialization
    GL.glViewport(0, 0, width, height)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_CULL_FACE)
    GL.glCullFace(GL.GL_BACK)
    # This heavily depends on setting the w for homogeneous
    # If w is positive
    GL.glFrontFace(GL.GL_CCW)
    GL.glClearColor(0.1, 0.1, 0.12, 1.0)


    shape_dir = "./shape"
    triangle = Triangle("./shape/triangle/triangle.vert", "./shape/triangle/triangle.frag")
    cube = Cube("./shape/cube/cube.vert", "./shape/cube/cube.frag")
    cylinder = Cylinder("./shape/cylinder/cylinder.vert", "./shape/cylinder/cylinder.frag", 1, 0.5, 20)

    app.add_shape(cylinder)

    app.run()


if __name__ == "__main__":
    main()
