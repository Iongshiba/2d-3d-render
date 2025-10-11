#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;
layout (location = 2) in vec3 norm;
layout (location = 3) in vec2 texture;

out vec3 vColor;
out vec3 vNorm;
out vec3 vCoord;
out vec2 tCoord;

uniform mat4 transform;
uniform mat4 camera;
uniform mat4 project;

void main()
{
    gl_Position = project * camera * transform * vec4(position, 1.0);
    vColor = color;
    vNorm = mat3(transpose(inverse(transform))) * norm;
    vCoord = vec3(transform * vec4(position, 1.0));
    tCoord = texture;
}