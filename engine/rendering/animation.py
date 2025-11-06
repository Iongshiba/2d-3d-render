from __future__ import annotations

import math
import numpy as np
import sympy as sp
from typing import Callable, Iterable, Any
from utils import *
from rendering.world import Rotate, Scale, Translate, Composite
from shape import Equation

AnimationFn = Callable[[object, float], None]


def gradient_descent(
    equation: Equation,
    ball_radius: float,
    optimizer: str = "SGD",
    learning_rate: float = 10.0,
    momentum: float = 0.9,
    min_gradient: float = 0.1,
    max_gradient: float = 0.03,
):
    dx, dy = make_numpy_deri(equation.expression)
    func = make_numpy_func(equation.expression)

    def update(transform: Composite, dt: float) -> None:
        nonlocal max_gradient
        nonlocal min_gradient
        nonlocal momentum

        if isinstance(transform[0], Translate):
            translate = transform[0]
            rotate = transform[1]
        else:
            translate = transform[1]
            rotate = transform[0]

        # translate
        x = translate.x
        y = translate.y

        x_grad = dx(x, y)
        y_grad = dy(x, y)
        xy_grad = np.array([x_grad, y_grad], dtype=np.float32)
        xy_grad_norm = np.linalg.norm(xy_grad)

        # gradient clipping
        max_gradient = 0.03
        if xy_grad_norm > max_gradient:
            xy_grad = xy_grad * (max_gradient / xy_grad_norm)
            xy_grad_norm = max_gradient

        if optimizer == "SGD":
            displacement = -learning_rate * dt * xy_grad

        # Calculate new position
        new_x = translate.x + displacement[0]
        new_y = translate.y + displacement[1]
        new_z = (func(new_x, new_y) - equation.Z_min) / (
            equation.Z_max - equation.Z_min
        ) * 10 + ball_radius

        # Calculate movement vector
        move_direction = np.array(
            [new_x - translate.x, new_y - translate.y, new_z - translate.z]
        )
        move_distance = np.linalg.norm(move_direction)

        # Update position
        # translate.x = new_x
        # translate.y = new_y
        # translate.z = new_z

        # Rotate (only when gradient is significant and ball is moving)
        if xy_grad_norm > min_gradient * 0.01 and move_distance > 1e-6:
            # For rolling motion, rotation axis is perpendicular to movement in XY plane
            move_direction_2d = np.array([move_direction[0], move_direction[1], 0.0])
            move_dist_2d = np.linalg.norm(move_direction_2d)

            if move_dist_2d > 1e-6:
                # Rotation axis: perpendicular to 2D movement (cross with Z-axis)
                rotation_axis = np.cross(
                    move_direction_2d / move_dist_2d, np.array([0.0, 0.0, 1.0])
                )
                axis_norm = np.linalg.norm(rotation_axis)

                if axis_norm > 1e-6:
                    rotation_axis = rotation_axis / axis_norm

                    # Calculate rotation angle: arc length / radius
                    rotation_angle_radians = move_distance / ball_radius
                    rotation_angle_degrees = np.degrees(rotation_angle_radians)

                    # Accumulate rotation
                    rotate.axis = tuple(rotation_axis)
                    rotate.angle -= rotation_angle_degrees

    return update


def infinite_spin(speed: float = 1.0) -> AnimationFn:
    def update(transform: Rotate, dt: float) -> None:
        transform.angle = float((transform.angle + dt * speed) % 360.0)

    return update


def circular_orbit(
    phase: float = 0.0, speed: float = 1.0, radius: float = 1.0, axis: str = "xy"
) -> AnimationFn:
    theta = phase
    axis = axis.lower()
    axes = {
        "xy": (0, 1),
        "xz": (0, 2),
        "yz": (1, 2),
    }

    def update(transform: Translate, dt: float) -> None:
        nonlocal theta
        theta = (theta + dt * speed) % (2 * math.pi)
        coords = [transform.x, transform.y, transform.z]
        first, second = axes[axis]
        coords[first] = math.cos(theta) * radius
        coords[second] = math.sin(theta) * radius
        transform.x, transform.y, transform.z = coords

    return update


def ping_pong_translation(
    axis: str = "y",
    amplitude: float = 1.0,
    speed: float = 1.0,
    center: float = 0.0,
) -> AnimationFn:
    axis = axis.lower()

    offset = 0.0

    def update(transform: Translate, dt: float) -> None:
        nonlocal offset
        offset = (offset + dt * speed) % (2 * math.pi)
        value = center + math.sin(offset) * amplitude
        setattr(transform, axis, value)

    return update


def pulse_scale(
    minimum: float = 0.5,
    maximum: float = 1.5,
    speed: float = 1.0,
) -> AnimationFn:
    if minimum > maximum:
        minimum, maximum = maximum, minimum

    phase = 0.0
    span = maximum - minimum

    def update(transform: Scale, dt: float) -> None:
        nonlocal phase
        phase = (phase + dt * speed) % (2 * math.pi)
        factor = minimum + (math.sin(phase) * 0.5 + 0.5) * span
        transform.x = transform.y = transform.z = factor

    return update


__all__ = [
    "AnimationFn",
    "gradient_descent",
    "infinite_spin",
    "circular_orbit",
    "ping_pong_translation",
    "pulse_scale",
]
