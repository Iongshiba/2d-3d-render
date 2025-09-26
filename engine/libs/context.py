"""Utility context managers for OpenGL resources."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator


@contextmanager
def shader_program(program) -> Iterator[None]:
    program.activate()
    try:
        yield
    finally:
        program.deactivate()


@contextmanager
def vao_context(vao) -> Iterator[None]:
    vao.activate()
    try:
        yield
    finally:
        vao.deactivate()


__all__ = ["shader_program", "vao_context"]
