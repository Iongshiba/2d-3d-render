import numpy as np
from rendering.world import Scale, Rotate, Transform
from utils.transform import *


# convert to homogeneous
def to_homogeneous(points):
    ones = np.ones((points.shape[0], 1))
    return np.hstack([points, ones])


vertices = np.array(
    [
        [0, -1, 0],  # 0 bottom center Ob
        [1, -1, 0],  # 1 A
        [-1, -1, 1],  # 2 B
        [-1, -1, -1],  # 3 C
        [0, 1, 0],  # 4 top center Ot
        [1, 1, 0],  # 5 D
        [-1, 1, 1],  # 6 E
        [-1, 1, -1],  # 7 F
    ],
    dtype=float,
)
colors = np.array(
    [
        [0, 0, 0],  # Ob (black)
        [1, 0, 0],  # A (red)
        [0, 1, 0],  # B (green)
        [0, 0, 1],  # C (blue)
        [1, 1, 1],  # Ot (white)
        [1, 1, 0],  # D (yellow)
        [1, 0, 1],  # E (magenta)
        [0, 1, 1],  # F (cyan)
    ]
)
normals = np.copy(vertices)
normals[:, 1] = 0
normals = normals / np.linalg.norm(normals)

homo_coords = to_homogeneous(vertices)

result = homo_coords

# 1.2.1 Task 1: Model Matrix Calculation

scale_matrix = scale(0.5, 0.5, 0.5)
rotate_matrix = rotate((0, 1, 0), 45)
translate_matrix = translate(0, 0.5, 0)
model_matrix = translate_matrix @ rotate_matrix @ scale_matrix
result = (model_matrix @ result.T).T
print("Model Matrix:")
print(model_matrix)
print("=" * 80)

# 1.2.2 Task 2: View Matrix Calculation

eye = np.array([5, 5, 5])
center = np.array([0, 0, 0])
up = np.array([0, 1, 0])

forward = center - eye
forward_norm = forward / np.linalg.norm(forward)

right = np.cross(forward_norm, up)
right_norm = right / np.linalg.norm(right)

up_ = np.cross(right_norm, forward)
up_norm = up_ / np.linalg.norm(up_)

view_matrix = lookat(   , center, up)
result = (view_matrix @ result.T).T
print("View Matrix")
print(view_matrix)
print("=" * 80)

# 1.2.3 Task 3: Model-View Matrix

model_view_matrix = view_matrix @ model_matrix
print("Model View Matrix")
print(model_view_matrix)
print("=" * 80)

# 1.2.4 Task 4: Point Transformations
