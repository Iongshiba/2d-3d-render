#version 330 core

out vec4 color;

in vec3 vertexColor;
in vec2 textureCoord;

uniform sampler2D textureData;
uniform bool use_texture;

void main()
{
    vec3 finalColor = vertexColor;
    
    if (use_texture) {
        vec3 texColor = texture(textureData, textureCoord).rgb;
        finalColor = mix(finalColor, texColor, 0.5);
    }
    
    color = vec4(finalColor, 1.0);
}
