#version 330 core

out vec4 color;

in vec3 vColor;
in vec2 tCoord;

uniform sampler2D tData;

void main()
{
    // color = vec4(vColor, 1.0);
    color = texture(tData, tCoord);
}