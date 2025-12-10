"""Chemistry visualization UI panel."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import imgui

from config import ChemistryMode, ShapeConfig, ShapeType


class ChemistryPanel:
    """UI panel for chemistry visualization."""

    MOLECULES = [
        ("Water (H₂O)", "water"),
        ("Carbon Dioxide (CO₂)", "carbon_dioxide"),
        ("Ammonia (NH₃)", "ammonia"),
        ("Methane (CH₄)", "methane"),
        ("Oxygen (O₂)", "oxygen"),
        ("Hydrogen (H₂)", "hydrogen"),
        ("Nitrogen (N₂)", "nitrogen"),
        ("Carbon Monoxide (CO)", "carbon_monoxide"),
        ("Nitric Oxide (NO)", "nitric_oxide"),
        ("Ethane (C₂H₆)", "ethane"),
        ("Ethylene (C₂H₄)", "ethylene"),
        ("Benzene (C₆H₆)", "benzene"),
        ("Generic Molecule", "molecule"),
    ]

    # Full periodic table (118 elements)
    PERIODIC_TABLE = [
        # Period 1
        ("H", "Hydrogen", 1),
        ("He", "Helium", 2),
        # Period 2
        ("Li", "Lithium", 3),
        ("Be", "Beryllium", 4),
        ("B", "Boron", 5),
        ("C", "Carbon", 6),
        ("N", "Nitrogen", 7),
        ("O", "Oxygen", 8),
        ("F", "Fluorine", 9),
        ("Ne", "Neon", 10),
        # Period 3
        ("Na", "Sodium", 11),
        ("Mg", "Magnesium", 12),
        ("Al", "Aluminum", 13),
        ("Si", "Silicon", 14),
        ("P", "Phosphorus", 15),
        ("S", "Sulfur", 16),
        ("Cl", "Chlorine", 17),
        ("Ar", "Argon", 18),
        # Period 4
        ("K", "Potassium", 19),
        ("Ca", "Calcium", 20),
        ("Sc", "Scandium", 21),
        ("Ti", "Titanium", 22),
        ("V", "Vanadium", 23),
        ("Cr", "Chromium", 24),
        ("Mn", "Manganese", 25),
        ("Fe", "Iron", 26),
        ("Co", "Cobalt", 27),
        ("Ni", "Nickel", 28),
        ("Cu", "Copper", 29),
        ("Zn", "Zinc", 30),
        ("Ga", "Gallium", 31),
        ("Ge", "Germanium", 32),
        ("As", "Arsenic", 33),
        ("Se", "Selenium", 34),
        ("Br", "Bromine", 35),
        ("Kr", "Krypton", 36),
        # Period 5
        ("Rb", "Rubidium", 37),
        ("Sr", "Strontium", 38),
        ("Y", "Yttrium", 39),
        ("Zr", "Zirconium", 40),
        ("Nb", "Niobium", 41),
        ("Mo", "Molybdenum", 42),
        ("Tc", "Technetium", 43),
        ("Ru", "Ruthenium", 44),
        ("Rh", "Rhodium", 45),
        ("Pd", "Palladium", 46),
        ("Ag", "Silver", 47),
        ("Cd", "Cadmium", 48),
        ("In", "Indium", 49),
        ("Sn", "Tin", 50),
        ("Sb", "Antimony", 51),
        ("Te", "Tellurium", 52),
        ("I", "Iodine", 53),
        ("Xe", "Xenon", 54),
        # Period 6
        ("Cs", "Cesium", 55),
        ("Ba", "Barium", 56),
        ("La", "Lanthanum", 57),
        ("Ce", "Cerium", 58),
        ("Pr", "Praseodymium", 59),
        ("Nd", "Neodymium", 60),
        ("Pm", "Promethium", 61),
        ("Sm", "Samarium", 62),
        ("Eu", "Europium", 63),
        ("Gd", "Gadolinium", 64),
        ("Tb", "Terbium", 65),
        ("Dy", "Dysprosium", 66),
        ("Ho", "Holmium", 67),
        ("Er", "Erbium", 68),
        ("Tm", "Thulium", 69),
        ("Yb", "Ytterbium", 70),
        ("Lu", "Lutetium", 71),
        ("Hf", "Hafnium", 72),
        ("Ta", "Tantalum", 73),
        ("W", "Tungsten", 74),
        ("Re", "Rhenium", 75),
        ("Os", "Osmium", 76),
        ("Ir", "Iridium", 77),
        ("Pt", "Platinum", 78),
        ("Au", "Gold", 79),
        ("Hg", "Mercury", 80),
        ("Tl", "Thallium", 81),
        ("Pb", "Lead", 82),
        ("Bi", "Bismuth", 83),
        ("Po", "Polonium", 84),
        ("At", "Astatine", 85),
        ("Rn", "Radon", 86),
        # Period 7
        ("Fr", "Francium", 87),
        ("Ra", "Radium", 88),
        ("Ac", "Actinium", 89),
        ("Th", "Thorium", 90),
        ("Pa", "Protactinium", 91),
        ("U", "Uranium", 92),
        ("Np", "Neptunium", 93),
        ("Pu", "Plutonium", 94),
        ("Am", "Americium", 95),
        ("Cm", "Curium", 96),
        ("Bk", "Berkelium", 97),
        ("Cf", "Californium", 98),
        ("Es", "Einsteinium", 99),
        ("Fm", "Fermium", 100),
        ("Md", "Mendelevium", 101),
        ("No", "Nobelium", 102),
        ("Lr", "Lawrencium", 103),
        ("Rf", "Rutherfordium", 104),
        ("Db", "Dubnium", 105),
        ("Sg", "Seaborgium", 106),
        ("Bh", "Bohrium", 107),
        ("Hs", "Hassium", 108),
        ("Mt", "Meitnerium", 109),
        ("Ds", "Darmstadtium", 110),
        ("Rg", "Roentgenium", 111),
        ("Cn", "Copernicium", 112),
        ("Nh", "Nihonium", 113),
        ("Fl", "Flerovium", 114),
        ("Mc", "Moscovium", 115),
        ("Lv", "Livermorium", 116),
        ("Ts", "Tennessine", 117),
        ("Og", "Oganesson", 118),
    ]

    def __init__(self, renderer):
        self.renderer = renderer
        self.mode = ChemistryMode.MOLECULES
        self.selected_molecule_idx = 0
        self.selected_element_idx = 0
        self.electron_layers = 3  # Default to 3 layers for visualization
        self.app = None  # Will be set by the overlay

    def set_app(self, app):
        """Set reference to the app for rendering overlays."""
        self.app = app

    def render(self, imgui_module) -> None:
        """Render the chemistry panel."""
        imgui = imgui_module

        imgui.text("Chemistry Visualizer")
        imgui.separator()
        imgui.spacing()

        # Mode selection
        mode_names = ["Periodic Table", "Molecules", "Bohr Model"]
        mode_values = [
            ChemistryMode.PERIODIC_TABLE,
            ChemistryMode.MOLECULES,
            ChemistryMode.BOHR_MODEL,
        ]

        current_mode_idx = mode_values.index(self.mode)
        mode_label = mode_names[current_mode_idx]

        if imgui.begin_combo("Mode", mode_label):
            for idx, (name, mode_val) in enumerate(zip(mode_names, mode_values)):
                is_selected = mode_val == self.mode
                clicked, _ = imgui.selectable(name, is_selected)
                if clicked and mode_val != self.mode:
                    self.mode = mode_val
                    self._update_scene()
                if is_selected:
                    imgui.set_item_default_focus()
            imgui.end_combo()

        imgui.spacing()
        imgui.separator()
        imgui.spacing()

        # Render mode-specific UI
        if self.mode == ChemistryMode.PERIODIC_TABLE:
            self._render_periodic_table(imgui)
        elif self.mode == ChemistryMode.MOLECULES:
            self._render_molecules(imgui)
        elif self.mode == ChemistryMode.BOHR_MODEL:
            self._render_bohr_model(imgui)

    def _render_periodic_table(self, imgui) -> None:
        """Render periodic table UI - just show instructions in panel."""
        imgui.text("Periodic Table Mode")
        imgui.spacing()
        imgui.text_wrapped(
            "The periodic table is displayed at the top-left of the screen. "
            "Click any element to view its Bohr model with electron shells."
        )
        imgui.spacing()

        symbol, name, atomic_num = self.PERIODIC_TABLE[self.selected_element_idx]
        imgui.separator()
        imgui.text(f"Selected Element:")
        imgui.text(f"{name} ({symbol})")
        imgui.text(f"Atomic Number: {atomic_num}")
        imgui.text(f"Electron Layers: {self.electron_layers}")

    def render_periodic_table_overlay(self, imgui_module) -> None:
        """Render periodic table as an overlay on the main viewport (top-left)."""
        if self.mode != ChemistryMode.PERIODIC_TABLE:
            return

        imgui = imgui_module

        # Create overlay window at top-left
        flags = (
            imgui.WINDOW_NO_TITLE_BAR
            | imgui.WINDOW_NO_RESIZE
            | imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_COLLAPSE
            | imgui.WINDOW_ALWAYS_AUTO_RESIZE
        )

        imgui.set_next_window_position(10, 10, condition=imgui.ALWAYS)
        imgui.set_next_window_bg_alpha(0.85)  # Semi-transparent background

        imgui.begin("PeriodicTableOverlay", flags=flags)
        imgui.text("Periodic Table of Elements")
        imgui.separator()

        # Render elements in standard periodic table layout (18 columns)
        button_size = 40
        spacing = 2

        # Standard periodic table positions (period, group) for first 54 elements
        # Format: atomic_num -> (row, col) where row is 0-indexed, col is 0-17
        element_positions = {
            1: (0, 0),
            2: (0, 17),  # Period 1
            3: (1, 0),
            4: (1, 1),
            5: (1, 12),
            6: (1, 13),
            7: (1, 14),
            8: (1, 15),
            9: (1, 16),
            10: (1, 17),  # Period 2
            11: (2, 0),
            12: (2, 1),
            13: (2, 12),
            14: (2, 13),
            15: (2, 14),
            16: (2, 15),
            17: (2, 16),
            18: (2, 17),  # Period 3
            19: (3, 0),
            20: (3, 1),
            21: (3, 2),
            22: (3, 3),
            23: (3, 4),
            24: (3, 5),
            25: (3, 6),
            26: (3, 7),
            27: (3, 8),
            28: (3, 9),
            29: (3, 10),
            30: (3, 11),
            31: (3, 12),
            32: (3, 13),
            33: (3, 14),
            34: (3, 15),
            35: (3, 16),
            36: (3, 17),  # Period 4
            37: (4, 0),
            38: (4, 1),
            39: (4, 2),
            40: (4, 3),
            41: (4, 4),
            42: (4, 5),
            43: (4, 6),
            44: (4, 7),
            45: (4, 8),
            46: (4, 9),
            47: (4, 10),
            48: (4, 11),
            49: (4, 12),
            50: (4, 13),
            51: (4, 14),
            52: (4, 15),
            53: (4, 16),
            54: (4, 17),  # Period 5
        }

        # Display first 54 elements in proper periodic table format
        display_elements = self.PERIODIC_TABLE[:54]

        # Create grid layout
        for row in range(5):  # 5 periods
            for col in range(18):  # 18 groups
                # Find element at this position
                element_idx = None
                for idx, (symbol, name, atomic_num) in enumerate(display_elements):
                    if element_positions.get(atomic_num) == (row, col):
                        element_idx = idx
                        break

                if element_idx is not None:
                    symbol, name, atomic_num = display_elements[element_idx]
                    is_selected = element_idx == self.selected_element_idx
                    if is_selected:
                        imgui.push_style_color(imgui.COLOR_BUTTON, 0.2, 0.7, 0.9, 1.0)

                    if imgui.button(
                        f"{symbol}##{element_idx}", button_size, button_size
                    ):
                        self.selected_element_idx = element_idx
                        # Calculate electron layers
                        if atomic_num <= 2:
                            self.electron_layers = 1
                        elif atomic_num <= 10:
                            self.electron_layers = 2
                        elif atomic_num <= 18:
                            self.electron_layers = 3
                        elif atomic_num <= 36:
                            self.electron_layers = 4
                        elif atomic_num <= 54:
                            self.electron_layers = 5
                        elif atomic_num <= 86:
                            self.electron_layers = 6
                        else:
                            self.electron_layers = 7
                        # Limit to 4 for performance
                        self.electron_layers = min(self.electron_layers, 4)
                        self._update_scene()

                    if is_selected:
                        imgui.pop_style_color()

                    # Tooltip on hover
                    if imgui.is_item_hovered():
                        imgui.begin_tooltip()
                        imgui.text(f"{name} ({symbol})")
                        imgui.text(f"Atomic #: {atomic_num}")
                        imgui.end_tooltip()
                else:
                    # Empty cell - add invisible button for spacing
                    imgui.invisible_button(
                        f"empty_{row}_{col}", button_size, button_size
                    )

                # Same line for all but last column
                if col < 17:
                    imgui.same_line(spacing=spacing)

        imgui.end()

    def _render_molecules(self, imgui) -> None:
        """Render molecule selection UI."""
        imgui.text("3D Molecular Models")
        imgui.spacing()

        molecule_name = self.MOLECULES[self.selected_molecule_idx][0]
        if imgui.begin_combo("Molecule", molecule_name):
            for idx, (name, _) in enumerate(self.MOLECULES):
                is_selected = idx == self.selected_molecule_idx
                clicked, _ = imgui.selectable(name, is_selected)
                if clicked and idx != self.selected_molecule_idx:
                    self.selected_molecule_idx = idx
                    self._update_scene()
                if is_selected:
                    imgui.set_item_default_focus()
            imgui.end_combo()

        imgui.spacing()
        imgui.text_wrapped("Ball-and-stick model showing atoms and bonds")

    def _render_bohr_model(self, imgui) -> None:
        """Render Bohr model UI."""
        imgui.text("Interactive Bohr Model")
        imgui.spacing()

        # Electron layer slider
        imgui.text("Electron Layers:")
        changed, new_layers = imgui.slider_int("##layers", self.electron_layers, 1, 4)
        if changed:
            self.electron_layers = new_layers
            self._update_scene()

        imgui.spacing()
        imgui.text(f"Displaying {self.electron_layers} electron layer(s)")
        imgui.text_wrapped(
            "Note: Limited to 4 layers (32 electrons max) for performance. "
            "Use the slider to adjust the number of visible electron shells."
        )

    def _update_scene(self):
        """Update the scene based on current mode and selection."""
        from template import get_scene

        try:
            if (
                self.mode == ChemistryMode.PERIODIC_TABLE
                or self.mode == ChemistryMode.BOHR_MODEL
            ):
                # Load Bohr model (atom scene) with specific electron layers
                scene = get_scene("atom")

                # Rebuild atom scene with custom electron layers
                from template.atom import (
                    _generate_nucleus,
                    _generate_electron,
                    _generate_orbit_ring,
                )
                from graphics.scene import Node, TransformNode, LightNode
                from rendering.world import Translate
                from shape.factory import ShapeFactory
                from config import ShapeConfig, ShapeType
                import numpy as np

                root = Node("atom_root")
                root.add(_generate_nucleus(0, 0, 0, 1, 7, 4))

                # Calculate electrons for each layer using formula: 2 * n^2
                # Layer 1: 2 * 1^2 = 2, Layer 2: 2 * 2^2 = 8, Layer 3: 2 * 3^2 = 18, Layer 4: 2 * 4^2 = 32
                radii = [4.0, 8.0, 12.0, 16.0]
                speeds = [0.5, 0.6, 0.7, 0.8]

                for layer_idx in range(self.electron_layers):
                    n = layer_idx + 1  # Shell number (1-indexed)
                    num_electrons = 2 * (n**2)
                    radius = radii[layer_idx]
                    speed = speeds[layer_idx]

                    for phase in np.linspace(
                        0, np.pi * 2, num_electrons, endpoint=False
                    ):
                        ring = _generate_orbit_ring(radius)
                        electron = _generate_electron(phase, radius, speed)
                        root.add(ring)
                        root.add(electron)

                # Add light
                shape_cfg = ShapeConfig()
                light = ShapeFactory.create_shape(ShapeType.LIGHT_SOURCE, shape_cfg)
                root.add(
                    TransformNode(
                        "light_parent",
                        Translate(30.0, 30.0, 30.0),
                        [LightNode("light", light)],
                    )
                )

                self.renderer.set_scene(root)

            elif self.mode == ChemistryMode.MOLECULES:
                # Load selected molecule scene
                _, scene_name = self.MOLECULES[self.selected_molecule_idx]
                scene = get_scene(scene_name)
                root = scene.rebuild()
                self.renderer.set_scene(root)

        except Exception as e:
            print(f"Failed to update chemistry scene: {e}")
            import traceback

            traceback.print_exc()

    def activate(self):
        """Activate this panel and load its default scene."""
        self._update_scene()


__all__ = ["ChemistryPanel"]
