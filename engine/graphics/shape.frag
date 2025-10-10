#version 330 core

out vec4 color;

in vec3 vColor;
in vec2 tCoord;

uniform sampler2D tData;
uniform bool use_texture;

uniform vec3 light;

void main()
{
    if (use_texture) {
        color = vec4(light, 1.0) * texture(tData, tCoord);
    } else {
        color = vec4(light, 1.0) * vec4(vColor, 1.0);
    }
}