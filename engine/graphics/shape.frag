#version 330 core

out vec4 color;

in vec3 vColor;
in vec2 tCoord;

uniform sampler2D tData;
uniform bool use_texture;

void main()
{
    if (use_texture) {
        color = texture(tData, tCoord);
    } else {
        color = vec4(vColor, 1.0);
    }
}