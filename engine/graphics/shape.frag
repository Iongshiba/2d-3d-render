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

void main()
{
    // Step 1: Ambient Light
    float ambientStrength = 0.3;
    vec3 ambient = lightColor * ambientStrength;

    // Step 2: Diffuse Light
    vec3 lightDirection = normalize(lightCoord - vertexCoord);
    vec3 vectorNorm = normalize(vertexNorm);
    float diff = max(dot(vectorNorm, lightDirection), 0.0);
    vec3 diffuse = lightColor * diff;

    // Step 3: Specular Light
    float specularStrength = 0.25;
    vec3 cameraDirection = normalize(cameraCoord - vertexCoord);
    vec3 reflectDirection = reflect(-lightDirection, vectorNorm);
    float spec = pow(max(dot(reflectDirection, cameraDirection), 0.0), 32);
    vec3 specular = lightColor * specularStrength * spec;


    if (use_texture) {
        color = vec4(specular + ambient + diffuse, 1.0) * texture(textureData, textureCoord);
    } else {
        color = vec4(specular + ambient + diffuse, 1.0) * vec4(vertexColor, 1.0);
    }
}