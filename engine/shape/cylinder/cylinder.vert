#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;

out vec3 vColor;

uniform mat4 transform;
uniform int uColorMode; // 0=FLAT, 1=VERTEX
uniform vec3 uFlatColor;

void main()
{
    gl_Position = transform * vec4(position, 1.0);
    vColor = (uColorMode == 0) ? uFlatColor : color;
}