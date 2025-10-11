#version 330 core

out vec4 color;

in vec3 vColor;
in vec3 vNorm;
in vec3 vCoord;
in vec2 tCoord;

uniform sampler2D tData;
uniform bool use_texture;
uniform vec3 light;
uniform vec3 lCoord;

void main()
{
    vec3 lightDirection = normalize(lCoord - vCoord); // Why lCoord - vCoord but not reverse?
    vec3 vectorNorm = normalize(vNorm);

    float ambientStrength = 0.1;
    float diffStrength = max(dot(vectorNorm, lightDirection), 0.0);

    vec3 ambient = light * ambientStrength;
    vec3 diffuse = light * diffStrength;

    if (use_texture) {
        color = vec4(ambient + diffuse, 1.0) * texture(tData, tCoord);
    } else {
        color = vec4(ambient + diffuse, 1.0) * vec4(vColor, 1.0);
    }
}