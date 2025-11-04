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
    learning_rate: float = 0.001,
    momentum: float = 0.9,
    min_gradient: float = 0.1,
):
    dx, dy = make_numpy_deri(equation.expression)
    func = make_numpy_func(equation.expression)

    def update(transform: Translate, dt: float) -> None:
        x = transform.x
        y = transform.y

        x_grad = dx(x, y)
        y_grad = dy(x, y)
        gradient = np.array([x_grad, y_grad], dtype=np.float32)
        max_grad_norm = 0.03
        grad_norm = np.linalg.norm(gradient)
        if grad_norm > max_grad_norm:
            gradient = gradient * (max_grad_norm / grad_norm)

        if optimizer == "SGD":
            displacement = -learning_rate * dt * gradient

        x = transform.x + displacement[0] - gradient[0] * ball_radius
        y = transform.y + displacement[1] - gradient[1] * ball_radius
        z = (func(x, y) - equation.Z_min) / (
            equation.Z_max - equation.Z_min
        ) * 10 + ball_radius

        transform.x = x
        transform.y = y
        transform.z = z

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
