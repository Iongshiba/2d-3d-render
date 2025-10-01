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

        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        glfw.set_key_callback(self.window, self._on_press)
        glfw.set_cursor_pos_callback(self.window, self._on_mouse)

        self.renderer = None
        self.pressed_keys = {
            glfw.KEY_W: False,
            glfw.KEY_S: False,
            glfw.KEY_A: False,
            glfw.KEY_D: False,
        }
        self.mouse_pos = (width / 2, height / 2)
        self.mouse_offset = (0.0, 0.0)
        self.mouse_move = False
        self._last_time = glfw.get_time()

    def _on_mouse(self, window, x_pos, y_pos):
        # window   -> the window where the event occured
        # xpos     -> the recorded x position of the mouse
        # ypos     -> the recorded y position of the mouse

        x_offset = self.mouse_pos[0] - x_pos
        y_offset = self.mouse_pos[1] - y_pos
        self.mouse_pos = (x_pos, y_pos)
        self.mouse_offset = (x_offset, y_offset)
        self.mouse_move = True

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
                self._update_camera(delta_time)
                self._update_transform(delta_time)
                self.renderer.render(self)

            glfw.poll_events()
            glfw.swap_buffers(self.window)

        glfw.terminate()

    def _update_transform(self, delta_time: float) -> None:
        if delta_time <= 0.0:
            return

        self.renderer.move_world(delta_time)

    def _update_camera(self, delta_time: float) -> None:
        if delta_time <= 0.0:
            return

        if self.mouse_move:
            self.renderer.rotate_camera(self.mouse_offset)
            self.mouse_move = False

        if self.pressed_keys.get(glfw.KEY_W):
            self.renderer.move_camera(CameraMovement.FORWARD, delta_time)
        if self.pressed_keys.get(glfw.KEY_S):
            self.renderer.move_camera(CameraMovement.BACKWARD, delta_time)
        if self.pressed_keys.get(glfw.KEY_A):
            self.renderer.move_camera(CameraMovement.LEFT, delta_time)
        if self.pressed_keys.get(glfw.KEY_D):
            self.renderer.move_camera(CameraMovement.RIGHT, delta_time)
