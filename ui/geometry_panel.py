"""Geometry shapes visualization UI panel."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    import imgui

from config import ShapeConfig, ShapeType, ShadingModel, MODEL_TEXTURE_MAP
from config.palette import COLOR_PRESETS, ColorPreset
from shape.factory import ShapeFactory
from template.shape_gallery import build_shape_scene, is_2d_shape


@dataclass(slots=True)
class MenuOption:
    label: str
    kind: str  # 'shape' or 'model'
    value: str | ShapeType


class GeometryPanel:
    """UI panel for geometry shapes visualization."""

    def __init__(self, renderer):
        self.renderer = renderer
        self._shape_config = ShapeConfig()
        self._color_presets: Sequence[ColorPreset] = COLOR_PRESETS
        self._color_index = 0
        self._shape_config.base_color = self._color_presets[self._color_index].rgb

        self._shape_options_2d, self._shape_options_3d, self._model_options = (
            self._build_options()
        )

        self._current_option: MenuOption | None = None
        self.shading_model = ShadingModel.PHONG

        self._shading_labels: dict[ShadingModel, str] = {
            ShadingModel.NORMAL: "Normal",
            ShadingModel.PHONG: "Phong",
            ShadingModel.GOURAUD: "Gouraud",
        }

        # Activate first 3D shape
        if self._shape_options_3d:
            self._apply_selection(self._shape_options_3d[0])

    def _build_options(
        self,
    ) -> tuple[List[MenuOption], List[MenuOption], List[MenuOption]]:
        shape_options_2d: List[MenuOption] = []
        shape_options_3d: List[MenuOption] = []
        model_options: List[MenuOption] = []

        for shape_type in sorted(
            ShapeFactory.list_registered_shapes(), key=lambda item: item.name
        ):
            if shape_type in {
                ShapeType.LIGHT_SOURCE,
                ShapeType.MODEL,
                ShapeType.EQUATION,
            }:
                continue
            label = f"{self._format_name(shape_type.name)}"
            option = MenuOption(label=label, kind="shape", value=shape_type)
            if is_2d_shape(shape_type):
                shape_options_2d.append(option)
            else:
                shape_options_3d.append(option)

        # Scan assets folder for 3D models
        assets_path = Path("assets")
        # Scan both top-level assets and assets/models for model files
        paths_to_scan = [assets_path]
        models_sub = assets_path / "models"
        if models_sub.exists():
            paths_to_scan.append(models_sub)

        for p in paths_to_scan:
            if p.exists():
                for model_file in sorted(p.iterdir()):
                    if model_file.suffix.lower() in [".obj", ".ply"]:
                        label = model_file.stem.replace("_", " ").title()
                        # store relative path under assets
                        rel = model_file.relative_to(assets_path)
                        model_options.append(
                            MenuOption(
                                label=label,
                                kind="model",
                                value=str(rel).replace("\\\\", "/"),
                            )
                        )

        return shape_options_2d, shape_options_3d, model_options

    def render(self, imgui_module) -> None:
        """Render the geometry panel."""
        imgui = imgui_module

        # Geometry: use the Shapes / Models inner tabs below
        imgui.separator()
        imgui.spacing()

        # Shapes vs Models sub-tabs
        if imgui.begin_tab_bar("GeometryInnerTabs"):
            # Shapes tab (2D & 3D)
            if imgui.begin_tab_item("Shapes")[0]:
                if self._shape_options_2d:
                    self._render_combo(imgui, "2D Shapes", self._shape_options_2d)
                if self._shape_options_3d:
                    self._render_combo(imgui, "3D Shapes", self._shape_options_3d)

                # Color preset selection (Shapes only)
                color_label = self._color_presets[self._color_index].name
                if imgui.begin_combo("Color Preset##shapes", color_label):
                    for idx, preset in enumerate(self._color_presets):
                        is_selected = idx == self._color_index
                        clicked, _ = imgui.selectable(preset.name, is_selected)
                        if clicked and idx != self._color_index:
                            self._color_index = idx
                            self._shape_config.base_color = preset.rgb
                            self._shape_config.gradient_mode = None
                            if (
                                self._current_option
                                and self._current_option.kind == "shape"
                            ):
                                self._apply_selection(self._current_option)
                        if is_selected:
                            imgui.set_item_default_focus()
                    imgui.end_combo()

                # Texture selection for shapes
                textures = [
                    p.name
                    for p in Path("textures").glob("*")
                    if p.suffix.lower() in [".png", ".jpg", ".jpeg"]
                ]
                current_texture = self._shape_config.texture_file or "None"
                imgui.text("Texture:")
                if imgui.begin_combo("Texture", current_texture):
                    # None option
                    clicked_none, _ = imgui.selectable(
                        "None", self._shape_config.texture_file is None
                    )
                    if clicked_none:
                        self._shape_config.texture_file = None
                        if (
                            self._current_option
                            and self._current_option.kind == "shape"
                        ):
                            self._apply_selection(self._current_option)
                    for tex in textures:
                        tex_path = f"textures/{tex}"
                        is_selected = self._shape_config.texture_file == tex_path
                        clicked, _ = imgui.selectable(tex, is_selected)
                        if clicked:
                            self._shape_config.texture_file = tex_path
                            if (
                                self._current_option
                                and self._current_option.kind == "shape"
                            ):
                                self._apply_selection(self._current_option)
                        if is_selected:
                            imgui.set_item_default_focus()
                    imgui.end_combo()

                imgui.end_tab_item()

            # Models tab
            if imgui.begin_tab_item("Models")[0]:
                if self._model_options:
                    self._render_combo(imgui, "Preloaded Models", self._model_options)

                imgui.separator()
                imgui.text("Load Custom Model")
                # File browser for OBJ and texture
                if not hasattr(self, "_custom_obj_path"):
                    self._custom_obj_path = ""
                if not hasattr(self, "_custom_tex_path"):
                    self._custom_tex_path = ""

                # OBJ file selection
                imgui.text(
                    f"OBJ: {self._custom_obj_path if self._custom_obj_path else 'None selected'}"
                )
                if imgui.button("Browse OBJ File..."):
                    try:
                        import tkinter as tk
                        from tkinter import filedialog

                        root = tk.Tk()
                        root.withdraw()
                        root.attributes("-topmost", True)
                        file_path = filedialog.askopenfilename(
                            title="Select OBJ File",
                            filetypes=[("OBJ files", "*.obj"), ("All files", "*.*")],
                        )
                        root.destroy()
                        if file_path:
                            self._custom_obj_path = file_path
                    except Exception as e:
                        print(f"File dialog error: {e}")

                # Texture file selection
                imgui.text(
                    f"Texture: {self._custom_tex_path if self._custom_tex_path else 'None selected'}"
                )
                imgui.same_line()
                if imgui.button("Browse Texture..."):
                    try:
                        import tkinter as tk
                        from tkinter import filedialog

                        root = tk.Tk()
                        root.withdraw()
                        root.attributes("-topmost", True)
                        file_path = filedialog.askopenfilename(
                            title="Select Texture File (Optional)",
                            filetypes=[
                                ("Image files", "*.png *.jpg *.jpeg"),
                                ("All files", "*.*"),
                            ],
                        )
                        root.destroy()
                        if file_path:
                            self._custom_tex_path = file_path
                    except Exception as e:
                        print(f"File dialog error: {e}")

                if imgui.button("Add to Assets"):
                    try:
                        from shutil import copyfile
                        from pathlib import Path as _P

                        src_obj = _P(self._custom_obj_path)
                        if not src_obj.exists():
                            raise FileNotFoundError(f"OBJ not found: {src_obj}")
                        assets_models = _P("assets/models")
                        assets_models.mkdir(parents=True, exist_ok=True)
                        dst_obj = assets_models / src_obj.name
                        copyfile(str(src_obj), str(dst_obj))
                        # Copy texture if provided
                        if self._custom_tex_path:
                            src_tex = _P(self._custom_tex_path)
                            if src_tex.exists():
                                textures_dir = _P("textures")
                                textures_dir.mkdir(parents=True, exist_ok=True)
                                dst_tex = textures_dir / src_tex.name
                                copyfile(str(src_tex), str(dst_tex))
                        # Refresh model options and select the newly added model
                        (
                            self._shape_options_2d,
                            self._shape_options_3d,
                            self._model_options,
                        ) = self._build_options()
                        # find the newly added model by name
                        dst_name = dst_obj.name
                        rel_name = str(dst_obj.relative_to(_P("assets"))).replace(
                            "\\\\", "/"
                        )
                        for opt in self._model_options:
                            if opt.value == rel_name or opt.value.endswith(dst_name):
                                self._apply_selection(opt)
                                break
                        imgui.open_popup("ModelAdded")
                    except Exception as e:
                        imgui.open_popup("ModelAddError")

                if imgui.begin_popup("ModelAdded"):
                    imgui.text(
                        "Model added to assets/models and textures (if provided)"
                    )
                    if imgui.button("OK"):
                        imgui.close_current_popup()
                    imgui.end_popup()

                if imgui.begin_popup("ModelAddError"):
                    imgui.text("Failed to add model. Check paths and try again.")
                    if imgui.button("OK"):
                        imgui.close_current_popup()
                    imgui.end_popup()

                imgui.end_tab_item()

            imgui.end_tab_bar()

        imgui.spacing()
        imgui.separator()
        imgui.text_wrapped(
            "Visualize 2D and 3D geometric shapes with different shading and textures."
        )

    def _render_combo(self, imgui, label: str, options: Sequence[MenuOption]) -> None:
        active_label = (
            self._current_option.label if self._current_option in options else "Select"
        )
        if imgui.begin_combo(label, active_label):
            for option in options:
                is_selected = option is self._current_option
                display_label = option.label
                clicked, _ = imgui.selectable(display_label, is_selected)
                if clicked:
                    self._apply_selection(option)
                if is_selected:
                    imgui.set_item_default_focus()
            imgui.end_combo()

    def _apply_selection(self, option: MenuOption) -> None:
        if option.kind == "model":
            # Load model with optional texture mapping
            model_filename = option.value
            self._shape_config.model_file = f"assets/{model_filename}"

            # Set texture from mapping if available
            texture_filename = MODEL_TEXTURE_MAP.get(model_filename)
            if texture_filename:
                self._shape_config.texture_file = f"textures/{texture_filename}"
            else:
                # Try matching texture by model stem in textures folder
                from pathlib import Path as _P

                model_stem = Path(model_filename).stem
                matched = None
                for p in _P("textures").glob("*"):
                    if p.stem == model_stem and p.suffix.lower() in [
                        ".png",
                        ".jpg",
                        ".jpeg",
                    ]:
                        matched = p.name
                        break
                if matched:
                    self._shape_config.texture_file = f"textures/{matched}"
                else:
                    self._shape_config.texture_file = None

            root = build_shape_scene(ShapeType.MODEL, self._shape_config)
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

    def activate(self):
        """Activate this panel and load its default scene."""
        if self._current_option:
            self._apply_selection(self._current_option)

    @staticmethod
    def _format_name(value: str) -> str:
        return value.replace("_", " ").title()


__all__ = ["GeometryPanel"]
