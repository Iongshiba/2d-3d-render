import os
import sys

# # Set platform hint before importing OpenGL
# if sys.platform.startswith("linux"):
#     os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

import glfw
import ctypes
import numpy as np
from OpenGL import GL


def processInput(window):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)


def compileShader(filename, mode):
    shader_code = ""

    with open(filename, "r") as f:
        shader_code = f.read()
    shader = GL.glCreateShader(mode)
    GL.glShaderSource(shader, shader_code)
    GL.glCompileShader(shader)

    assert GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS), GL.glGetShaderInfoLog(shader)

    return shader


def main():
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    window = glfw.create_window(1280, 720, "Viewer", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    ##################   OPENGL   ##################

    # Vertex coords
    vertex = [
        [-0.5, -0.5, 0.0],
        [0.5, -0.5, 0.0],
        [0.0, 0.5, 0.0],
    ]
    vertex = np.array(vertex, dtype=np.float32)

    # Vertex Array Object
    vao = GL.glGenVertexArrays(1)
    GL.glBindVertexArray(vao)

    # Vertex Buffer Object
    vbo = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, vertex.nbytes, vertex, GL.GL_STATIC_DRAW)

    # Vertex Array
    GL.glVertexAttribPointer(
        0, 3, GL.GL_FLOAT, GL.GL_FALSE, 3 * vertex.itemsize, ctypes.c_void_p(0)
    )
    GL.glEnableVertexAttribArray(0)

    # Compile Shader
    vertex_shader = compileShader("triangle.vert", GL.GL_VERTEX_SHADER)
    fragment_shader = compileShader("triangle.frag", GL.GL_FRAGMENT_SHADER)

    # Create Shader Program
    shader_program = GL.glCreateProgram()
    GL.glAttachShader(shader_program, vertex_shader)
    GL.glAttachShader(shader_program, fragment_shader)
    GL.glLinkProgram(shader_program)

    GL.glDeleteShader(vertex_shader)
    GL.glDeleteShader(fragment_shader)

    # Check Create
    success = GL.glGetProgramiv(shader_program, GL.GL_LINK_STATUS)
    if not success:
        print(GL.glGetProgramInfoLog(shader_program))

    ##################   OPENGL   ##################

    while not glfw.window_should_close(window):
        # Process input
        processInput(window)

        # Render here
        GL.glClearColor(0.2, 0.3, 0.3, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glUseProgram(shader_program)
        GL.glBindVertexArray(vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)

        # Check call event and display buffer
        glfw.poll_events()
        glfw.swap_buffers(window)

    # Cleanup after loop
    glfw.terminate()


if __name__ == "__main__":
    main()
    print(GL.glGetIntegerv(GL.GL_MAX_VERTEX_ATTRIBS))
