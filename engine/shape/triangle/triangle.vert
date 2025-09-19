#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;

out vec3 flat_color;

uniform mat4 transform;

void main()
{
    flat_color = color;
    gl_Position = transform * vec4(position, 1.0f);
}