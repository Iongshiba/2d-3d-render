#version 330 core

in vec3 flat_color;

out vec4 color;

void main()
{
    color = vec4(flat_color, 1.0f);
}