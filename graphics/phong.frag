#version 330 core

out vec4 color;

in vec3 vertexColor; // this turn into position for fragment, not vertex anymore
in vec3 vertexNorm;
in vec3 vertexCoord;
in vec2 textureCoord;

uniform sampler2D textureData;
uniform bool use_texture;

uniform mat3 I_lights;
uniform mat3 K_materials;

uniform float shininess;

uniform vec3 lightCoord;

uniform int shadingMode; // 0 = normal visualization, 1 = Phong

void main()
{
    vec3 baseColor = use_texture
        ? texture(textureData, textureCoord).rgb
        : vertexColor;

    if (shadingMode == 0) {
        color = vec4(vertexColor, 1.0);
        return;
    }

    // diffuse
    vec3 vectorNorm = normalize(vertexNorm);
    vec3 lightDirection = normalize(lightCoord - vertexCoord);

    // specular
    vec3 cameraDirection = normalize(-vertexCoord);
    vec3 reflectDirection = reflect(-lightDirection, vectorNorm);

    vec3 g = vec3(
        max(dot(lightDirection, vectorNorm), 0.0),
        pow(max(dot(cameraDirection, reflectDirection), 0.0), shininess),
        0.0
    );
    vec3 fragColor = matrixCompMult(K_materials, I_lights) * g;

    
    color = vec4(vertexColor * 0.5 + fragColor * 0.5, 1.0);
}