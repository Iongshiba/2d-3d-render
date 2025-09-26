"""Utility context managers for OpenGL resources."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from OpenGL import GL


@contextmanager
def shader_program(program) -> Iterator[None]:
    """Bind a shader program for the lifetime of the context."""

    current = GL.glGetIntegerv(GL.GL_CURRENT_PROGRAM)
    program_id = getattr(program, "program", None)
    activated = current != program_id
    if activated:
        program.activate()
    try:
        yield
    finally:
        if activated:
            program.deactivate()


@contextmanager
def vao_context(vao) -> Iterator[None]:
    """Bind a VAO for the lifetime of the context."""

    current = GL.glGetIntegerv(GL.GL_VERTEX_ARRAY_BINDING)
    vao_id = getattr(vao, "vao", None)
    activated = current != vao_id
    if activated:
        vao.activate()
    try:
        yield
    finally:
        if activated:
            vao.deactivate()


__all__ = ["shader_program", "vao_context"]
