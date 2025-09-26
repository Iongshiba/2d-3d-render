import os
import sys
import glfw
import ctypes

import numpy as np
from OpenGL import GL


class App:
    def __init__(self, width, height):
        if not glfw.init():
            raise RuntimeError("GLFW failed to initialize")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.width = width
        self.height = height
        self.window = glfw.create_window(self.width, self.height, "App", None, None)

        if not self.window:
            raise RuntimeError("Window failed to create")

        glfw.make_context_current(self.window)

        glfw.set_key_callback(self.window, self._on_press)

        self.shapes = []

    def _on_press(self, window, key, scancode, action, mods):
        # window   -> the window where the event occurred
        # key      -> which key was pressed (GLFW_KEY_* constants)
        # scancode -> system-specific scancode
        # action   -> GLFW_PRESS, GLFW_RELEASE, or GLFW_REPEAT
        # mods     -> modifier bits (GLFW_MOD_SHIFT, CTRL, ALT, SUPER)
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(window, True)

    def add_shape(self, shape):
        self.shapes.append(shape)

    def get_aspect_ratio(self):
        return self.width / self.height

    def run(self):
        while not glfw.window_should_close(self.window):
            # Clear once per frame
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            for shape in self.shapes:
                # Check if shape.draw accepts app parameter
                try:
                    shape.draw(self)
                except TypeError:
                    # Fallback for shapes that don't accept app parameter
                    shape.draw()

            glfw.poll_events()
            glfw.swap_buffers(self.window)

        glfw.terminate()
