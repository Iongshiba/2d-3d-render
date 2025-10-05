import os
import sys
import glfw
import ctypes

from OpenGL import GL

from rendering.camera import CameraMovement


class App:
    def __init__(self, width, height, use_trackball):
        if not glfw.init():
            raise RuntimeError("GLFW failed to initialize")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.width = width
        self.height = height
        self.winsize = (width, height)
        self.window = glfw.create_window(self.width, self.height, "App", None, None)

        if not self.window:
            raise RuntimeError("Window failed to create")

        glfw.make_context_current(self.window)

        # glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        glfw.set_key_callback(self.window, self._on_press)
        glfw.set_cursor_pos_callback(self.window, self._on_mouse)
        glfw.set_scroll_callback(self.window, self._on_scroll)
        glfw.set_mouse_button_callback(self.window, self._on_mouse_press)

        self.renderer = None
        self.pressed_keys = {
            glfw.KEY_W: False,
            glfw.KEY_S: False,
            glfw.KEY_A: False,
            glfw.KEY_D: False,
        }
        self.mouse_pos = (0, 0)
        self.mouse_move = False
        self._last_time = glfw.get_time()

        self.use_arcball = use_trackball

    def _on_mouse_press(self, window, button, action, mods):
        if (
            button in [glfw.MOUSE_BUTTON_LEFT, glfw.MOUSE_BUTTON_RIGHT]
            and action == glfw.PRESS
        ):
            x_pos, y_pos = glfw.get_cursor_pos(self.window)
            if self.use_arcball:
                self.mouse_pos = (x_pos, self.winsize[1] - y_pos)
            else:
                self.mouse_pos = (x_pos, y_pos)
            self.mouse_move = True
        elif action == glfw.RELEASE:
            self.mouse_move = False

    def _on_mouse(self, window, x_pos, y_pos):
        # window   -> the window where the event occured
        # xpos     -> the recorded x position of the mouse
        # ypos     -> the recorded y position of the mouse

        # fmt: off
        if self.mouse_move:
            prev_pos = self.mouse_pos
            new_pos = (x_pos, self.winsize[1] - y_pos) if self.use_arcball else (x_pos, y_pos)
            if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT):
                if self.use_arcball:
                    self.renderer.rotate_trackball(prev_pos, new_pos, self.winsize)
                else:
                    self.renderer.rotate_camera(prev_pos, new_pos)
            if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT):
                if self.use_arcball:
                    self.renderer.move_trackball(prev_pos, new_pos)
            self.mouse_pos = new_pos

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

    def _on_scroll(self, window, delta_x, delta_y):
        self.renderer.zoom_trackball(delta_y, self.winsize[1])

    def add_renderer(self, renderer):
        renderer.use_trackball = self.use_arcball
        renderer.app = self
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

            # Updating Animated Transformed
            self._update_transform(delta_time)
            # Updating WASD movement
            self._update_camera(delta_time)
            self.renderer.render()

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

        if self.pressed_keys.get(glfw.KEY_W):
            self.renderer.move_camera(CameraMovement.FORWARD, delta_time)
        if self.pressed_keys.get(glfw.KEY_S):
            self.renderer.move_camera(CameraMovement.BACKWARD, delta_time)
        if self.pressed_keys.get(glfw.KEY_A):
            self.renderer.move_camera(CameraMovement.LEFT, delta_time)
        if self.pressed_keys.get(glfw.KEY_D):
            self.renderer.move_camera(CameraMovement.RIGHT, delta_time)
