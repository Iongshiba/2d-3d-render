#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;

out vec3 vColor;

uniform mat4 transform;
uniform mat4 camera;
uniform mat4 project;

void main()
{
    vColor = color;
    gl_Position = project * camera * transform * vec4(position, 1.0);
}