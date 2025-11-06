from __future__ import annotations

import gc
import sys
from dataclasses import dataclass
from typing import List, Sequence

import glfw
import imgui  # type: ignore
from imgui.integrations.glfw import GlfwRenderer  # type: ignore

from OpenGL import GL

from config import ShapeConfig, ShapeType, ShadingModel
from config import GradientMode
from config.palette import COLOR_PRESETS, ColorPreset
from rendering.camera import CameraMovement
from shape.factory import ShapeFactory
from template import SceneController, create_controller
from template.shape_gallery import build_shape_scene, is_2d_shape


class App:
    def __init__(self, width, height, use_trackball):
        # Ensure GLFW is properly terminated before initializing
        try:
            glfw.terminate()
        except Exception:
            pass

        if not glfw.init():
            raise RuntimeError("GLFW failed to initialize")

        self.width = width
        self.height = height
        self.winsize = (width, height)
        self.window = None
        self.gl_version = None

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.width = width
        self.height = height
        self.winsize = (width, height)
        self.window = glfw.create_window(self.width, self.height, "App", None, None)

        if not self.window:
            glfw.terminate()
            raise RuntimeError("Window failed to create")

        glfw.make_context_current(self.window)
        fb_width, fb_height = glfw.get_framebuffer_size(self.window)
        if fb_width and fb_height:
            self.width, self.height = fb_width, fb_height
        self.winsize = (self.width, self.height)

        # glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        glfw.set_key_callback(self.window, self._on_press)
        glfw.set_cursor_pos_callback(self.window, self._on_mouse)
        glfw.set_scroll_callback(self.window, self._on_scroll)
        glfw.set_mouse_button_callback(self.window, self._on_mouse_press)
        glfw.set_framebuffer_size_callback(self.window, self._on_resize)

        self.renderer = None
        self.ui = None
        self._key_handlers = []
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

    def _on_resize(self, window, width, height):
        width = max(int(width), 1)
        height = max(int(height), 1)
        self.width = width
        self.height = height
        self.winsize = (width, height)
        GL.glViewport(0, 0, width, height)

    def _on_mouse_press(self, window, button, action, mods):
        if self.ui and self.ui.wants_mouse_capture():
            return
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
        if self.ui and self.ui.wants_mouse_capture():
            return
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

        if (
            self.ui
            and self.ui.wants_keyboard_capture()
            and key not in (glfw.KEY_ESCAPE, glfw.KEY_Q)
        ):
            return

        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(window, True)
            if key == glfw.KEY_F and self.renderer:
                self.renderer.toggle_wireframe()
            if key in self.pressed_keys:
                self.pressed_keys[key] = True
        elif action == glfw.RELEASE and key in self.pressed_keys:
            self.pressed_keys[key] = False

        for handler in self._key_handlers:
            handler(key, action, mods)

    def _on_scroll(self, window, delta_x, delta_y):
        if self.ui and self.ui.wants_mouse_capture():
            return
        if self.renderer:
            self.renderer.zoom_trackball(delta_y, self.winsize[1])

    def add_renderer(self, renderer):
        renderer.use_trackball = self.use_arcball
        renderer.app = self
        self.renderer = renderer

    def add_ui(self, ui):
        self.ui = ui

    def register_key_handler(self, handler):
        self._key_handlers.append(handler)

    def set_window_title(self, title: str) -> None:
        if self.window:
            glfw.set_window_title(self.window, title)

    def get_aspect_ratio(self):
        return self.width / self.height

    def run(self):
        while not glfw.window_should_close(self.window):
            current_time = glfw.get_time()
            delta_time = min(current_time - self._last_time, 0.05)
            self._last_time = current_time

            glfw.poll_events()

            if self.ui:
                self.ui.process_inputs()
                self.ui.new_frame(delta_time, self.winsize)

            # Clear once per frame
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            if self.renderer:
                if not (self.ui and self.ui.wants_keyboard_capture()):
                    self._update_camera(delta_time)
                self.renderer.render(delta_time)

            if self.ui:
                self.ui.render()

            glfw.swap_buffers(self.window)

        # Cleanup before terminating
        self.cleanup()

    def cleanup(self):
        """Cleanup all resources before terminating."""
        try:
            # Cleanup renderer resources
            if self.renderer and hasattr(self.renderer, "cleanup"):
                self.renderer.cleanup()

            # Cleanup UI
            if self.ui:
                self.ui.shutdown()

            # Terminate GLFW
            if self.window:
                glfw.destroy_window(self.window)
                self.window = None

            glfw.terminate()
        except Exception as e:
            # If cleanup fails, at least try to terminate GLFW
            try:
                glfw.terminate()
            except Exception:
                pass

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


@dataclass(slots=True)
class MenuOption:
    label: str
    kind: str  # 'template' or 'shape'
    value: str | ShapeType


class SceneControlOverlay:
    """Immediate-mode UI overlay for selecting scenes, shapes, and shading."""

    _PANEL_MIN_WIDTH = 240.0
    _PANEL_MAX_WIDTH = 340.0

    def __init__(self, app: App, renderer):
        self.app = app
        self.renderer = renderer

        # ImGui setup keeps context co-located with GLFW usage for easier lifecycle management.
        self._imgui = imgui
        self._context = imgui.create_context()
        self._impl = GlfwRenderer(app.window, attach_callbacks=False)
        self._impl.refresh_font_texture()

        self._scene_controller: SceneController = create_controller()
        self._shape_config = ShapeConfig()
        self._color_presets: Sequence[ColorPreset] = COLOR_PRESETS
        self._color_index = 0
        self._shape_config.base_color = self._color_presets[self._color_index].rgb
        (
            self._template_options,
            self._shape_options_2d,
            self._shape_options_3d,
        ) = self._build_options()
        if not (
            self._template_options or self._shape_options_2d or self._shape_options_3d
        ):
            raise RuntimeError(
                "No templates or shapes were discovered for the control overlay."
            )

        self._current_option: MenuOption | None = None

        self.shading_model = ShadingModel.PHONG
        self._shading_labels: dict[ShadingModel, str] = {
            ShadingModel.NORMAL: "Normal",
            ShadingModel.PHONG: "Phong",
        }
        self.renderer.set_shading_model(self.shading_model)

        # Gradient settings
        self._gradient_labels: dict[GradientMode, str] = {
            GradientMode.NONE: "None",
            GradientMode.LINEAR_X: "Linear X",
            GradientMode.LINEAR_Y: "Linear Y",
            GradientMode.LINEAR_Z: "Linear Z",
            GradientMode.RADIAL: "Radial",
            GradientMode.DIAGONAL: "Diagonal",
            GradientMode.RAINBOW: "Rainbow",
        }

        # Activate first available option so the renderer has a scene before the main loop.
        initial_option = (
            self._template_options[:1]
            or self._shape_options_3d[:1]
            or self._shape_options_2d[:1]
        )[0]
        self._apply_selection(initial_option)

    def process_inputs(self) -> None:
        self._impl.process_inputs()

    def new_frame(self, _delta_time: float, winsize: Sequence[int | float]) -> None:
        self._imgui.new_frame()
        self._render_panel(winsize)

    def render(self) -> None:
        self._imgui.render()
        self._impl.render(self._imgui.get_draw_data())

    def shutdown(self) -> None:
        self._impl.shutdown()
        self._imgui.destroy_context(self._context)

    def wants_keyboard_capture(self) -> bool:
        return bool(self._imgui.get_io().want_capture_keyboard)

    def wants_mouse_capture(self) -> bool:
        return bool(self._imgui.get_io().want_capture_mouse)

    def _build_options(
        self,
    ) -> tuple[List[MenuOption], List[MenuOption], List[MenuOption]]:
        template_options: List[MenuOption] = []
        shape_options_2d: List[MenuOption] = []
        shape_options_3d: List[MenuOption] = []

        for name in sorted(self._scene_controller.listscenes()):
            label = f"{self._format_name(name)}"
            template_options.append(
                MenuOption(label=label, kind="template", value=name)
            )

        for shape_type in sorted(
            ShapeFactory.list_registered_shapes(), key=lambda item: item.name
        ):
            if shape_type in {ShapeType.LIGHT_SOURCE, ShapeType.MODEL}:
                continue
            label = f"{self._format_name(shape_type.name)}"
            option = MenuOption(label=label, kind="shape", value=shape_type)
            if is_2d_shape(shape_type):
                shape_options_2d.append(option)
            else:
                shape_options_3d.append(option)

        return template_options, shape_options_2d, shape_options_3d

    def _apply_selection(self, option: MenuOption) -> None:
        if option.kind == "template":
            scene = self._scene_controller.set_current(option.value)
            root = scene.rebuild()
            self.renderer.set_scene(root)
            self.renderer.set_face_culling(True)
            self.renderer.set_shading_model(ShadingModel.PHONG)
            self.shading_model = ShadingModel.PHONG
        else:
            selected_color = self._color_presets[self._color_index].rgb
            self._shape_config.base_color = selected_color
            root = build_shape_scene(option.value, self._shape_config)
            is_shape_2d = is_2d_shape(option.value)
            self.renderer.set_scene(root)
            self.renderer.set_face_culling(not is_shape_2d)
            next_shading = ShadingModel.NORMAL if is_shape_2d else ShadingModel.PHONG
            self.renderer.set_shading_model(next_shading)
            self.shading_model = next_shading

        self._current_option = option
        self.app.set_window_title(f"App - {option.label}")

    def _render_panel(self, winsize: Sequence[int | float]) -> None:
        width = float(winsize[0]) if winsize else float(self.app.width)
        height = float(winsize[1]) if len(winsize) > 1 else float(self.app.height)

        panel_width = max(
            self._PANEL_MIN_WIDTH, min(self._PANEL_MAX_WIDTH, width * 0.32)
        )
        panel_x = max(0.0, width - panel_width)

        flags = (
            self._imgui.WINDOW_NO_RESIZE
            | self._imgui.WINDOW_NO_COLLAPSE
            | self._imgui.WINDOW_NO_MOVE
        )

        self._imgui.set_next_window_position(panel_x, 0.0, condition=self._imgui.ALWAYS)
        self._imgui.set_next_window_size(
            panel_width, height, condition=self._imgui.ALWAYS
        )

        self._imgui.begin("Scene Controls", flags=flags)

        if self._template_options:
            self._render_combo("Templates", self._template_options)
        if self._shape_options_2d:
            self._render_combo("2D Shapes", self._shape_options_2d)
        if self._shape_options_3d:
            self._render_combo("3D Shapes", self._shape_options_3d)

        self._imgui.spacing()

        shading_label = self._shading_labels[self.shading_model]
        if self._imgui.begin_combo("Shading", shading_label):
            for model, label in self._shading_labels.items():
                is_selected = model is self.shading_model
                clicked, _ = self._imgui.selectable(label, is_selected)
                if clicked and model is not self.shading_model:
                    self.shading_model = model
                    self.renderer.set_shading_model(model)
                if is_selected:
                    self._imgui.set_item_default_focus()
            self._imgui.end_combo()

        color_label = self._color_presets[self._color_index].name
        if self._imgui.begin_combo("Color Preset", color_label):
            for idx, preset in enumerate(self._color_presets):
                is_selected = idx == self._color_index
                clicked, _ = self._imgui.selectable(preset.name, is_selected)
                if clicked and idx != self._color_index:
                    self._color_index = idx
                    self._shape_config.base_color = preset.rgb
                    if self._current_option and self._current_option.kind == "shape":
                        self._apply_selection(self._current_option)
                if is_selected:
                    self._imgui.set_item_default_focus()
            self._imgui.end_combo()

        # Gradient Mode selection
        current_gradient = self._shape_config.gradient_mode or GradientMode.NONE
        gradient_label = self._gradient_labels[current_gradient]
        if self._imgui.begin_combo("Gradient", gradient_label):
            for mode, label in self._gradient_labels.items():
                is_selected = mode is current_gradient
                clicked, _ = self._imgui.selectable(label, is_selected)
                if clicked and mode is not current_gradient:
                    self._shape_config.gradient_mode = (
                        mode if mode != GradientMode.NONE else None
                    )
                    if self._current_option and self._current_option.kind == "shape":
                        self._apply_selection(self._current_option)
                if is_selected:
                    self._imgui.set_item_default_focus()
            self._imgui.end_combo()

        self._imgui.spacing()
        self._imgui.text_wrapped(
            "Templates combine multiple objects and animations, while shapes let you preview a single primitive from the library."
        )
        self._imgui.end()

    @staticmethod
    def _format_name(value: str) -> str:
        return value.replace("_", " ").title()

    def _render_combo(self, label: str, options: Sequence[MenuOption]) -> None:
        active_label = (
            self._current_option.label if self._current_option in options else "Select"
        )
        if self._imgui.begin_combo(label, active_label):
            for option in options:
                is_selected = option is self._current_option
                display_label = option.label
                clicked, _ = self._imgui.selectable(display_label, is_selected)
                if clicked:
                    self._apply_selection(option)
                if is_selected:
                    self._imgui.set_item_default_focus()
            self._imgui.end_combo()
