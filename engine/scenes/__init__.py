from __future__ import annotations

from collections.abc import Callable, Iterable

from graphics.scene import Node

from .base import Scene, SceneController


SceneBuilder = Callable[[], Node]

_REGISTERED_SCENES: dict[str, Scene] = {}


def register_scene(name: str, build_fn: SceneBuilder) -> None:
    """Register a scene builder and create its graph immediately."""

    root = build_fn()
    _REGISTERED_SCENES[name] = Scene(name, root)


def get_scene(name: str) -> Scene:
    return _REGISTERED_SCENES[name]


def list_scenes() -> list[str]:
    return list(_REGISTERED_SCENES.keys())


def iter_scenes() -> Iterable[Scene]:
    return _REGISTERED_SCENES.values()


def create_controller(default_scene: str | None = None) -> SceneController:
    controller = SceneController(iter_scenes())
    if default_scene is not None and default_scene in _REGISTERED_SCENES:
        controller.set_current(default_scene)
    return controller


__all__ = [
    "Scene",
    "SceneController",
    "register_scene",
    "get_scene",
    "list_scenes",
    "iter_scenes",
    "create_controller",
]


# Import default scenes so they self-register when package is loaded.
# Additional scenes can be added alongside these modules.
from . import atom_scene, shape_scene  # noqa: E402,F401
