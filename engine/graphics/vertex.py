import numpy as np
from typing import ClassVar, Tuple


class Vertex:
    _global_color: ClassVar[Tuple[float | None, float | None, float | None] | None] = None

    @classmethod
    def set_global_color(
        cls, color: Tuple[float | None, float | None, float | None] | None
    ) -> None:
        cls._global_color = color

    @classmethod
    def get_global_color(
        cls,
    ) -> Tuple[float | None, float | None, float | None] | None:
        return cls._global_color

    def __init__(self, x, y, z, r=None, g=None, b=None):
        self.vertex = np.array([x, y, z], dtype=np.float32)
        r = np.random.uniform(0.5, 0.7) if r is None else r  # small red
        g = np.random.uniform(0.5, 0.7) if g is None else g  # small green
        b = np.random.uniform(0.5, 0.8) if b is None else b  # strong blue

        override = self._global_color
        if override:
            if override[0] is not None:
                r = override[0]
            if override[1] is not None:
                g = override[1]
            if override[2] is not None:
                b = override[2]

        self.color = np.array([r, g, b], dtype=np.float32)
