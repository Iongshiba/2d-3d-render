from __future__ import annotations

import gc
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

import glfw
import imgui  # type: ignore
from imgui.integrations.glfw import GlfwRenderer  # type: ignore

from OpenGL import GL

from config import ShapeConfig, ShapeType, ShadingModel, MODEL_TEXTURE_MAP
from config import ModelVisualizationMode, SubwindowType
from config.palette import COLOR_PRESETS, ColorPreset
from rendering.camera import CameraMovement
from shape.factory import ShapeFactory
from shape.model import Model
from template import SceneController, create_controller
from template.shape_gallery import build_shape_scene, is_2d_shape
from utils.dataset_export import DatasetExporter
from ui import GradientDescentPanel, ChemistryPanel, GeometryPanel


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

        # Initialize dataset exporter
        self.dataset_exporter = DatasetExporter()

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
                else:
                    self.renderer.pan_camera(prev_pos, new_pos)
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
            if key == glfw.KEY_T and self.renderer:
                self.renderer.toggle_texture_mapping()
            if key == glfw.KEY_B and self.renderer:
                self._toggle_model_visualization(ModelVisualizationMode.BOUNDING_BOX)
            if key == glfw.KEY_N and self.renderer:
                self._toggle_model_visualization(ModelVisualizationMode.DEPTH_MAP)
            if key == glfw.KEY_M and self.renderer:
                self._toggle_model_visualization(
                    ModelVisualizationMode.SEGMENTATION_MASK
                )
            if key == glfw.KEY_V and self.renderer:
                self._export_dataset()
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

    def _toggle_model_visualization(self, mode: ModelVisualizationMode) -> None:
        """Toggle visualization mode for all Model instances in the scene."""
        if not self.renderer or not self.renderer.root:
            return

        models = self._find_models_in_scene(self.renderer.root)
        for model in models:
            # Toggle: if already in this mode, switch to NORMAL; otherwise switch to requested mode
            if model.visualization_mode == mode:
                model.set_visualization_mode(ModelVisualizationMode.NORMAL)
            else:
                model.set_visualization_mode(mode)

    def _find_models_in_scene(self, node) -> list:
        """Recursively find all Model instances in the scene tree."""
        models = []

        # Check if this node contains a Model
        if hasattr(node, "shape") and isinstance(node.shape, Model):
            models.append(node.shape)

        # Recursively check children
        if hasattr(node, "children"):
            for child in node.children:
                models.extend(self._find_models_in_scene(child))

        return models

    def _export_dataset(self) -> None:
        """Export current scene to dataset formats (COCO and YOLO)."""
        if not self.renderer or not self.renderer.root:
            print("No scene to export")
            return

        # Find all models in the scene
        models = self._find_models_in_scene(self.renderer.root)

        if not models:
            print("No models found in scene to export")
            return

        # Perform export
        try:
            status = self.dataset_exporter.export_dataset(
                width=self.width,
                height=self.height,
                models=models,
                renderer=self.renderer,
            )
            print(status)
        except Exception as e:
            print(f"Export failed: {e}")
            import traceback

            traceback.print_exc()


class SceneControlOverlay:
    """Tabbed UI overlay for 3 subwindows: Geometry, Gradient Descent, Chemistry."""

    _PANEL_MIN_WIDTH = 280.0
    _PANEL_MAX_WIDTH = 400.0

    def __init__(self, app: App, renderer):
        self.app = app
        self.renderer = renderer

        # ImGui setup
        self._imgui = imgui
        self._context = imgui.create_context()
        self._impl = GlfwRenderer(app.window, attach_callbacks=False)
        self._impl.refresh_font_texture()

        # Create subwindow panels
        self.gradient_panel = GradientDescentPanel(renderer)
        self.chemistry_panel = ChemistryPanel(renderer)
        self.chemistry_panel.set_app(app)  # Set app reference for overlays
        self.geometry_panel = GeometryPanel(renderer)

        # Current active subwindow
        self.active_subwindow = SubwindowType.GEOMETRY

        # Activate default panel
        self.geometry_panel.activate()

    def process_inputs(self) -> None:
        self._impl.process_inputs()

    def new_frame(self, _delta_time: float, winsize: Sequence[int | float]) -> None:
        self._imgui.new_frame()
        self._render_panel(winsize)
        # Render periodic table overlay if in chemistry periodic table mode
        if self.active_subwindow == SubwindowType.CHEMISTRY:
            self.chemistry_panel.render_periodic_table_overlay(self._imgui)

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

    def _render_panel(self, winsize: Sequence[int | float]) -> None:
        """Render the main tabbed control panel."""
        width = float(winsize[0]) if winsize else float(self.app.width)
        height = float(winsize[1]) if len(winsize) > 1 else float(self.app.height)

        panel_width = max(
            self._PANEL_MIN_WIDTH, min(self._PANEL_MAX_WIDTH, width * 0.35)
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

        self._imgui.begin("Controls", flags=flags)

        # Tab bar
        if self._imgui.begin_tab_bar("SubwindowTabs"):
            # Geometry tab
            if self._imgui.begin_tab_item("Geometry")[0]:
                if self.active_subwindow != SubwindowType.GEOMETRY:
                    self.active_subwindow = SubwindowType.GEOMETRY
                    self.geometry_panel.activate()
                self.geometry_panel.render(self._imgui)
                self._imgui.end_tab_item()

            # Gradient Descent tab
            if self._imgui.begin_tab_item("Gradient Descent")[0]:
                if self.active_subwindow != SubwindowType.GRADIENT_DESCENT:
                    self.active_subwindow = SubwindowType.GRADIENT_DESCENT
                    self.gradient_panel.activate()
                self.gradient_panel.render(self._imgui)
                self._imgui.end_tab_item()

            # Chemistry tab
            if self._imgui.begin_tab_item("Chemistry")[0]:
                if self.active_subwindow != SubwindowType.CHEMISTRY:
                    self.active_subwindow = SubwindowType.CHEMISTRY
                    self.chemistry_panel.activate()
                self.chemistry_panel.render(self._imgui)
                self._imgui.end_tab_item()

            self._imgui.end_tab_bar()

        # Global shading control applied to all subwindows
        shading_labels = {
            ShadingModel.NORMAL: "Normal",
            ShadingModel.PHONG: "Phong",
            ShadingModel.GOURAUD: "Gouraud",
            ShadingModel.BLINN_PHONG: "Blinn-Phong",
        }
        # current label
        current_shading = shading_labels.get(self.renderer.shading_model, "Phong")
        if self._imgui.begin_combo("Shading", current_shading):
            for model, label in shading_labels.items():
                is_selected = model is self.renderer.shading_model
                clicked, _ = self._imgui.selectable(label, is_selected)
                if clicked and model is not self.renderer.shading_model:
                    self.renderer.set_shading_model(model)
                if is_selected:
                    self._imgui.set_item_default_focus()
            self._imgui.end_combo()

        self._imgui.end()
