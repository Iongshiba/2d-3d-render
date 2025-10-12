from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from graphics.scene import Node


@dataclass(slots=True)
class Scene:
    name: str
    root: Node

    def get_root(self) -> Node:
        return self.root


class SceneController:
    def __init__(self, scenes: Iterable[Scene] | None = None):
        self.scenes: dict[str, Scene] = {}
        self.current: str | None = None

        if scenes:
            for scene in scenes:
                self.add_scene(scene)

    def add_scene(self, scene: Scene) -> Scene:
        self.scenes[scene.name] = scene
        if self.current is None:
            self.current = scene.name
        return scene

    def get_scene(self, name: str) -> Scene | None:
        return self.scenes.get(name)

    def set_current(self, name: str) -> Scene:
        self.current = name
        return self.scenes[name]

    def get_current_scene(self) -> Scene | None:
        if self.current is None:
            return None
        return self.scenes.get(self.current)

    def get_current_root(self) -> Node | None:
        scene = self.get_current_scene()
        return scene.get_root() if scene else None

    def listscenes(self) -> list[str]:
        return list(self.scenes.keys())

    def remove_scene(self, name: str) -> None:
        if name in self.scenes:
            del self.scenes[name]
            if self.current == name:
                self.current = next(iter(self.scenes), None)
