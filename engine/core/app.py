import os
import sys
import glfw
import ctypes

from OpenGL import GL

from rendering.camera import CameraMovement


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
        self.renderer = None
        self.pressed_keys = {
            glfw.KEY_W: False,
            glfw.KEY_S: False,
            glfw.KEY_A: False,
            glfw.KEY_D: False,
        }
        self._last_time = glfw.get_time()

    def _on_press(self, window, key, scancode, action, mods):
        # window   -> the window where the event occurred
        # key      -> which key was pressed (GLFW_KEY_* constants)
        # scancode -> system-specific scancode
        # action   -> GLFW_PRESS, GLFW_RELEASE, or GLFW_REPEAT
        # mods     -> modifier bits (GLFW_MOD_SHIFT, CTRL, ALT, SUPER)
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(window, True)
            if key in self.pressed_keys:
                self.pressed_keys[key] = True
        elif action == glfw.RELEASE and key in self.pressed_keys:
            self.pressed_keys[key] = False

    def add_shape(self, shape):
        self.shapes.append(shape)

    def add_renderer(self, renderer):
        self.renderer = renderer

    def get_aspect_ratio(self):
        return self.width / self.height

    def run(self):
        while not glfw.window_should_close(self.window):
            current_time = glfw.get_time()
            delta_time = current_time - self._last_time
            self._last_time = current_time

            # Clear once per frame
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            if self.renderer is not None:
                self._update_camera_movement(delta_time)

            if self.shapes:
                for shape in self.shapes:
                    try:
                        shape.draw(self)
                    except TypeError:
                        shape.draw()
            elif self.renderer:
                try:
                    self.renderer.draw(self)
                except TypeError:
                    self.renderer.draw()

            glfw.poll_events()
            glfw.swap_buffers(self.window)

        glfw.terminate()

    def _update_camera_movement(self, delta_time: float) -> None:
        if delta_time <= 0.0 or self.renderer is None:
            return

        step_scale = float(delta_time)
        if self.pressed_keys.get(glfw.KEY_W):
            self.renderer.move_camera(CameraMovement.FORWARD, step_scale)
        if self.pressed_keys.get(glfw.KEY_S):
            self.renderer.move_camera(CameraMovement.BACKWARD, step_scale)
        if self.pressed_keys.get(glfw.KEY_A):
            self.renderer.move_camera(CameraMovement.LEFT, step_scale)
        if self.pressed_keys.get(glfw.KEY_D):
            self.renderer.move_camera(CameraMovement.RIGHT, step_scale)
