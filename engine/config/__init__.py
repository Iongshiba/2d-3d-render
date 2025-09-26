"""Engine configuration dataclasses and helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Tuple

from core.enums import (
    ColorMode,
    RenderMode,
    ShadingModel,
    ShapeType,
    TextureMode,
)

RGBColor = Tuple[float, float, float]


@dataclass(slots=True)
class ShapeConfig:
    """Shape specific configuration attributes."""

    cylinder_height: float = 1.0
    cylinder_radius: float = 0.5
    cylinder_sectors: int = 20

    sphere_radius: float = 2.0
    sphere_sectors: int = 160
    sphere_stacks: int = 161


@dataclass(slots=True)
class EngineConfig:
    """Aggregated configuration for the rendering engine."""

    width: int = 1000
    height: int = 1000
    shape: ShapeType = ShapeType.SPHERE
    color_mode: ColorMode = ColorMode.VERTEX
    shading: ShadingModel = ShadingModel.NONE
    texture: TextureMode = TextureMode.NONE
    render_mode: RenderMode = RenderMode.FILL
    flat_color: RGBColor = (0.8, 0.2, 0.9)
    shape_config: ShapeConfig = field(default_factory=ShapeConfig)

    @classmethod
    def from_dict(cls, config_dict: Mapping[str, Any]) -> "EngineConfig":
        """Create a configuration instance from a nested mapping."""

        data: MutableMapping[str, Any] = dict(config_dict)
        shape_values = data.pop("shape_config", {})
        shape_config = (
            shape_values
            if isinstance(shape_values, ShapeConfig)
            else ShapeConfig(**shape_values)
        )
        return cls(shape_config=shape_config, **data)

    def update(self, updates: Mapping[str, Any]) -> None:
        """Update configuration fields from a mapping."""

        for key, value in updates.items():
            if key == "shape_config":
                if isinstance(value, Mapping):
                    for attr, nested_value in value.items():
                        setattr(self.shape_config, attr, nested_value)
                elif isinstance(value, ShapeConfig):
                    self.shape_config = value
                else:
                    raise TypeError("shape_config must be mapping or ShapeConfig")
            elif hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"Unknown configuration field: {key}")

    def __getattr__(self, item: str) -> Any:
        """Provide backward-compatible access to shape configuration fields."""

        if hasattr(self.shape_config, item):
            return getattr(self.shape_config, item)
        raise AttributeError(f"{type(self).__name__!s} has no attribute {item!r}")


__all__ = ["EngineConfig", "ShapeConfig", "RGBColor"]
