from __future__ import annotations

import math
from typing import Callable

from rendering.world import Rotate, Scale, Translate

AnimationFn = Callable[[object, float], None]


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
    "infinite_spin",
    "circular_orbit",
    "ping_pong_translation",
    "pulse_scale",
]
