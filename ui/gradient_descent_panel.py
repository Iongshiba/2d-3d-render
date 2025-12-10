"""Gradient Descent visualization UI panel."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import imgui

from config import ShapeConfig, ShapeType
from template.gradient_descent import build_gradient_descent


class GradientDescentPanel:
    """UI panel for gradient descent visualization."""

    SURFACES_FILE = "surface_equations.json"

    # Default surfaces
    DEFAULT_SURFACES = [
        ("Himmelblau", "(x^2 + y - 11)^2 + (x + y^2 - 7)^2"),
        ("Rosenbrock", "(1 - x)^2 + 100 * (y - x^2)^2"),
        ("Sphere", "x^2 + y^2"),
        ("Rastrigin", "20 + x^2 + y^2 - 10*(cos(2*3.14159*x) + cos(2*3.14159*y))"),
        ("Beale", "(1.5 - x + x*y)^2 + (2.25 - x + x*y^2)^2 + (2.625 - x + x*y^3)^2"),
    ]

    # Gradient descent techniques
    TECHNIQUES = ["SGD", "momentum", "adagrad", "rmsdrop", "adam", "adamw", "adarpop"]

    def __init__(self, renderer):
        self.renderer = renderer
        self.surfaces = self._load_surfaces()
        self.selected_surface_idx = 0
        self.selected_technique_idx = 4  # adam by default
        self.custom_equation = ""
        self.show_add_surface = False
        self.context_menu_idx = -1

        # Grid size parameter
        self.grid_size = 15  # Default mesh size (larger = bigger grid)

        # Hyperparameters for gradient descent algorithms
        self.learning_rate = 5.0
        self.momentum_alpha = 1.0  # momentum coefficient
        self.epsilon = 1e-4  # for adagrad/rmsdrop/adam
        self.decay_rate = 0.99  # for rmsdrop
        self.beta1 = 0.99  # for adam/adamw
        self.beta2 = 0.999  # for adam/adamw
        self.weight_decay = 0.01  # for adamw

    def _load_surfaces(self) -> list[tuple[str, str]]:
        """Load surfaces from JSON file or use defaults."""
        surfaces_path = Path(self.SURFACES_FILE)
        if surfaces_path.exists():
            try:
                with open(surfaces_path, "r") as f:
                    loaded = json.load(f)
                    if loaded:
                        return [(s["name"], s["equation"]) for s in loaded]
            except Exception:
                pass
        return list(self.DEFAULT_SURFACES)

    def _save_surfaces(self):
        """Save surfaces to JSON file."""
        try:
            data = [{"name": name, "equation": eq} for name, eq in self.surfaces]
            with open(self.SURFACES_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save surfaces: {e}")

    def render(self, imgui_module) -> None:
        """Render the gradient descent panel."""
        imgui = imgui_module

        imgui.text("Gradient Descent Visualizer")
        imgui.separator()
        imgui.spacing()

        # Surface selection
        if imgui.tree_node("Surfaces", imgui.TREE_NODE_DEFAULT_OPEN):
            current_surface_name = self.surfaces[self.selected_surface_idx][0]
            if imgui.begin_combo("##surface_select", current_surface_name):
                for idx, (name, _) in enumerate(self.surfaces):
                    is_selected = idx == self.selected_surface_idx
                    clicked, _ = imgui.selectable(name, is_selected)
                    if clicked:
                        self.selected_surface_idx = idx
                        self._update_scene()

                    # Right-click context menu
                    if imgui.begin_popup_context_item(f"##ctx_{idx}"):
                        if imgui.selectable("Remove##remove")[0]:
                            if len(self.surfaces) > 1:  # Keep at least one
                                self.surfaces.pop(idx)
                                self.selected_surface_idx = min(
                                    self.selected_surface_idx, len(self.surfaces) - 1
                                )
                                self._save_surfaces()
                                self._update_scene()
                        imgui.end_popup()

                    if is_selected:
                        imgui.set_item_default_focus()
                imgui.end_combo()

            # Show equation
            _, equation = self.surfaces[self.selected_surface_idx]
            imgui.text_wrapped(f"Equation: {equation}")
            imgui.spacing()

            # Add custom surface
            if imgui.button("Add Custom Surface"):
                self.show_add_surface = not self.show_add_surface

            if self.show_add_surface:
                imgui.spacing()
                imgui.text("Enter equation (use x and y):")
                changed, self.custom_equation = imgui.input_text(
                    "##custom_eq", self.custom_equation, 256
                )
                if imgui.button("Add to List"):
                    if self.custom_equation.strip():
                        name = f"Custom {len(self.surfaces) + 1}"
                        self.surfaces.append((name, self.custom_equation.strip()))
                        self._save_surfaces()
                        self.custom_equation = ""
                        self.show_add_surface = False

            imgui.tree_pop()

        imgui.spacing()

        # Grid Size Control
        if imgui.tree_node("Grid Settings", imgui.TREE_NODE_DEFAULT_OPEN):
            imgui.text("Grid Size (XY plane):")
            changed, new_size = imgui.slider_int("##grid_size", self.grid_size, 8, 25)
            if changed:
                self.grid_size = new_size
                self._update_scene()
            imgui.text_wrapped(
                f"Current: {self.grid_size} (larger = bigger visualization)"
            )
            imgui.tree_pop()

        imgui.spacing()

        # Gradient Descent Technique
        if imgui.tree_node("Gradient Descent Technique", imgui.TREE_NODE_DEFAULT_OPEN):
            technique_name = self.TECHNIQUES[self.selected_technique_idx]
            if imgui.begin_combo("##technique", technique_name):
                for idx, tech in enumerate(self.TECHNIQUES):
                    is_selected = idx == self.selected_technique_idx
                    clicked, _ = imgui.selectable(tech, is_selected)
                    if clicked and idx != self.selected_technique_idx:
                        self.selected_technique_idx = idx
                        self._update_scene()
                    if is_selected:
                        imgui.set_item_default_focus()
                imgui.end_combo()

            imgui.tree_pop()

        imgui.spacing()

        # Hyperparameters section
        if imgui.tree_node("Hyperparameters", imgui.TREE_NODE_DEFAULT_OPEN):
            technique = self.TECHNIQUES[self.selected_technique_idx]

            # Common: Learning Rate
            changed, new_lr = imgui.slider_float(
                "Learning Rate##lr", self.learning_rate, 0.1, 20.0
            )
            if changed:
                self.learning_rate = new_lr
                self._update_scene()

            # Technique-specific parameters
            if technique == "momentum":
                changed, new_alpha = imgui.slider_float(
                    "Momentum (α)##alpha", self.momentum_alpha, 0.0, 1.5
                )
                if changed:
                    self.momentum_alpha = new_alpha
                    self._update_scene()

            elif technique in ["adagrad", "rmsdrop", "adam", "adamw", "adarpop"]:
                changed, new_eps = imgui.input_float(
                    "Epsilon (ε)##eps", self.epsilon, format="%.1e"
                )
                if changed:
                    self.epsilon = max(1e-8, new_eps)
                    self._update_scene()

            if technique == "rmsdrop":
                changed, new_decay = imgui.slider_float(
                    "Decay Rate##decay", self.decay_rate, 0.8, 0.999
                )
                if changed:
                    self.decay_rate = new_decay
                    self._update_scene()

            if technique in ["adam", "adamw", "adarpop"]:
                changed, new_b1 = imgui.slider_float(
                    "Beta1 (β₁)##beta1", self.beta1, 0.5, 0.999
                )
                if changed:
                    self.beta1 = new_b1
                    self._update_scene()

                changed, new_b2 = imgui.slider_float(
                    "Beta2 (β₂)##beta2", self.beta2, 0.9, 0.9999
                )
                if changed:
                    self.beta2 = new_b2
                    self._update_scene()

            if technique == "adamw":
                changed, new_wd = imgui.slider_float(
                    "Weight Decay##wd", self.weight_decay, 0.0, 0.1
                )
                if changed:
                    self.weight_decay = new_wd
                    self._update_scene()

            imgui.tree_pop()

        imgui.spacing()
        imgui.separator()
        imgui.text_wrapped(
            "The ball starts at a random edge and rolls down using the selected optimization technique."
        )

    def _update_scene(self):
        """Update the scene with current surface and technique."""
        from graphics.scene import Node, TransformNode, LightNode
        from rendering.world import Translate
        from shape.factory import ShapeFactory
        from config import ShapeConfig, ShapeType

        # Get current surface equation
        _, equation = self.surfaces[self.selected_surface_idx]
        technique = self.TECHNIQUES[self.selected_technique_idx]

        # Build scene
        root = Node("root")

        # Update equation in gradient descent builder
        from template import gradient_descent as gd_module

        # Store equation temporarily
        old_expr = None
        try:
            # Build gradient descent scene with current equation and technique
            # We need to modify the build function to accept equation
            import numpy as np
            from graphics.scene import GeometryNode
            from rendering.world import Rotate, Composite
            from rendering.animation import gradient_descent
            from config import GradientMode

            ball_radius = 0.2
            ball_color = (0.698, 0.745, 0.710)

            equation_cfg = ShapeConfig()
            equation_cfg.equation_expression = equation
            equation_cfg.equation_mesh_size = (
                self.grid_size
            )  # Use configurable grid size
            equation_cfg.base_color = (0.8, 0.8, 0.9)
            equation_shape = ShapeFactory.create_shape(ShapeType.EQUATION, equation_cfg)
            equation_node = GeometryNode("surface", equation_shape)
            root.add(equation_node)

            X, Y, Z = equation_shape.surface
            normals = equation_shape.normals
            rows, cols = X.shape

            # Random starting position
            edge = np.random.randint(0, 4)
            if edge == 0:
                i, j = 0, np.random.randint(0, cols)
            elif edge == 1:
                i, j = rows - 1, np.random.randint(0, cols)
            elif edge == 2:
                i, j = np.random.randint(0, rows), 0
            else:
                i, j = np.random.randint(0, rows), cols - 1

            pos = np.array([X[i, j], Y[i, j], Z[i, j]], dtype=np.float32)
            norm = normals[i, j]
            ball_initial_location = pos + ball_radius * norm

            # Create animation with hyperparameters
            gd_animation = gradient_descent(
                equation=equation_shape,
                start_pos=ball_initial_location,
                ball_radius=ball_radius,
                optimizer=technique,
                learning_rate=self.learning_rate,
                momentum=self.momentum_alpha,
                epsilon=self.epsilon,
                decay_rate=self.decay_rate,
                beta1=self.beta1,
                beta2=self.beta2,
                weight_decay=self.weight_decay,
            )

            ball_cfg = ShapeConfig()
            ball_cfg.sphere_radius = ball_radius
            ball_cfg.base_color = ball_color
            ball_cfg.gradient_end_color = (0.73, 0.25, 0.23)
            ball_cfg.gradient_start_color = (0.25, 0.25, 0.97)
            ball_cfg.gradient_mode = GradientMode.LINEAR_X
            ball_shape = ShapeFactory.create_shape(ShapeType.SPHERE, ball_cfg)
            ball_node = GeometryNode("ball", ball_shape)
            ball_spawn = TransformNode(
                "ball_transform",
                Composite(
                    [Translate(*ball_initial_location), Rotate()], animate=gd_animation
                ),
                [ball_node],
            )
            root.add(ball_spawn)

            # Add light
            light_cfg = ShapeConfig()
            light_shape = ShapeFactory.create_shape(ShapeType.LIGHT_SOURCE, light_cfg)
            light_node = LightNode("gd_light", light_shape)
            light_transform = TransformNode(
                "light_transform", Translate(0.0, 30.0, 30.0), [light_node]
            )
            root.add(light_transform)

            self.renderer.set_scene(root)

        except Exception as e:
            print(f"Failed to update gradient descent scene: {e}")
            import traceback

            traceback.print_exc()

    def activate(self):
        """Activate this panel and load its default scene."""
        self._update_scene()


__all__ = ["GradientDescentPanel"]
