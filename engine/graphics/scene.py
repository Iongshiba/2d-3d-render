import numpy as np
from shape.base import Shape, Part


class Node:
    def __init__(
        self,
        name: str = "Node",
        children: list["Node"] = [],
    ):
        self.name: str = name
        self.children: list["Node"] = children

    def add(self, child):
        self.children.append(child)

    def draw(self, parent_matrix, view, proj):
        for child in self.children:
            child.draw(parent_matrix, view, proj)


class TransformNode(Node):
    def __init__(
        self,
        name: str = "TransformNode",
        matrix: np.array = np.identity(),
    ):
        super().__init__(name)
        self.matrix: np.array = matrix

    def draw(self, parent_matrix, view, proj):
        current = np.dot(parent_matrix, self.matrix)
        for child in self.children:
            child.draw(current, view, proj)


class GeometryNode(Node):
    def __init__(
        self,
        name: str = "GeometryNode",
        shape: Shape = None,
    ):
        super().__init__(name)
        self.shape = shape

    def draw(self, parent_matrix, view, proj):
        
