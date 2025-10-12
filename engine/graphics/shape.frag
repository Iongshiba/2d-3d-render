#version 330 core

out vec4 color;

in vec3 vertexColor;
in vec3 vertexNorm;
in vec3 vertexCoord;
in vec2 textureCoord;

uniform sampler2D textureData;
uniform bool use_texture;
uniform vec3 lightColor;
uniform vec3 lightCoord;
uniform vec3 cameraCoord;
uniform int shadingMode; // 0 = normal visualization, 1 = Phong

void main()
{
    vec3 baseColor = use_texture
        ? texture(textureData, textureCoord).rgb
        : vertexColor;

    if (shadingMode == 0) {
        vec3 normalColor = normalize(vertexNorm) * 0.5 + 0.5;
        color = vec4(normalColor, 1.0);
        return;
    }

    float ambientStrength = 0.3;
    vec3 lightDirection = normalize(lightCoord - vertexCoord);
    vec3 vectorNorm = normalize(vertexNorm);
    float diff = max(dot(vectorNorm, lightDirection), 0.0);
    vec3 cameraDirection = normalize(cameraCoord - vertexCoord);
    vec3 reflectDirection = reflect(-lightDirection, vectorNorm);
    float spec = pow(max(dot(reflectDirection, cameraDirection), 0.0), 32);
    float specularStrength = 0.25;

    vec3 ambient = lightColor * ambientStrength * baseColor;
    vec3 diffuse = lightColor * diff * baseColor;
    vec3 specular = lightColor * specularStrength * spec;

    vec3 finalColor = ambient + diffuse + specular;
    color = vec4(finalColor, 1.0);
}