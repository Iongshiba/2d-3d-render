# Visual Diagrams

This document contains visual diagrams that illustrate the architecture and data flow of the rendering engine. These diagrams use Mermaid syntax and can be viewed in any Markdown viewer that supports Mermaid (GitHub, VS Code with Mermaid extension, etc.).

## Table of Contents
- [Scene Graph Structure](#scene-graph-structure)
- [Class Hierarchy](#class-hierarchy)
- [Rendering Pipeline Flow](#rendering-pipeline-flow)
- [Data Flow: Vertex to Pixel](#data-flow-vertex-to-pixel)
- [Component Relationships](#component-relationships)

---

## Scene Graph Structure

### Basic Node Types

```mermaid
classDiagram
    class Node {
        +string name
        +list~Node~ children
        +draw(parent_matrix, view, proj)
        +add(child)
    }
    
    class TransformNode {
        +Transform transform
        +draw(parent_matrix, view, proj)
    }
    
    class GeometryNode {
        +Shape shape
        +draw(parent_matrix, view, proj)
    }
    
    class LightNode {
        +Shape shape
        +draw(parent_matrix, view, proj)
    }
    
    Node <|-- TransformNode
    Node <|-- GeometryNode
    Node <|-- LightNode
    
    TransformNode --> Transform : contains
    GeometryNode --> Shape : contains
    LightNode --> Shape : contains
```

### Example Scene Graph Tree

```mermaid
graph TD
    A[Root Node] --> B[SunTransform]
    A --> C[EarthOrbit]
    A --> D[LightTransform]
    
    B --> E[SunGeometry]
    E --> F[Sphere Shape]
    
    C --> G[EarthTransform]
    G --> H[EarthGeometry]
    H --> I[Sphere Shape]
    
    D --> J[LightNode]
    J --> K[LightSource Shape]
    
    style A fill:#e1f5ff
    style B fill:#ffe1e1
    style C fill:#ffe1e1
    style D fill:#ffe1e1
    style E fill:#e1ffe1
    style H fill:#e1ffe1
    style J fill:#fff3e1
```

**Legend:**
- 🔵 Blue: Container Nodes
- 🔴 Red: Transform Nodes
- 🟢 Green: Geometry Nodes
- 🟡 Yellow: Light Nodes

---

## Class Hierarchy

### Complete Class Structure

```mermaid
classDiagram
    class App {
        +Renderer renderer
        +UI ui
        +Window window
        +run()
        +cleanup()
    }
    
    class Renderer {
        +Camera camera
        +Trackball trackball
        +Node root
        +list~GeometryNode~ shape_nodes
        +list~LightNode~ light_nodes
        +render(delta_time)
        +_collect_node(node)
        +_apply_lighting()
        +_apply_shading()
    }
    
    class Camera {
        +vec3 position
        +vec3 front, up, right
        +float fov, pitch, yaw
        +get_view_matrix()
        +get_projection_matrix()
        +move(direction)
        +look(old, new)
    }
    
    class Trackball {
        +quaternion rotation
        +float distance
        +vec2 pos2d
        +get_view_matrix()
        +get_projection_matrix()
        +drag(old, new)
        +zoom(delta)
        +pan(old, new)
    }
    
    class Shape {
        +ShaderProgram shader_program
        +list~Part~ shapes
        +Texture2D texture
        +transform(proj, view, model)
        +lighting(color, pos, camera)
        +draw()
    }
    
    class Part {
        +VAO vao
        +int draw_mode
        +int vertex_num
        +int index_num
    }
    
    class VAO {
        +dict vbos
        +ebo
        +add_vbo(location, data)
        +add_ebo(data)
        +activate()
        +deactivate()
    }
    
    class ShaderProgram {
        +int program
        +dict shaders
        +add_shader(shader)
        +build()
        +activate()
        +deactivate()
    }
    
    class Transform {
        +matrix4x4 matrix
        +get_matrix()
        +update_matrix(dt)
    }
    
    class Translate {
        +float x, y, z
        +get_matrix()
    }
    
    class Rotate {
        +vec3 axis
        +float angle
        +get_matrix()
    }
    
    class Scale {
        +float x, y, z
        +get_matrix()
    }
    
    class Composite {
        +list~Transform~ transforms
        +get_matrix()
    }
    
    App --> Renderer : owns
    App --> UI : owns
    Renderer --> Camera : uses
    Renderer --> Trackball : uses
    Renderer --> Node : root
    
    GeometryNode --> Shape : contains
    Shape --> ShaderProgram : uses
    Shape --> Part : contains
    Part --> VAO : contains
    
    Transform <|-- Translate
    Transform <|-- Rotate
    Transform <|-- Scale
    Transform <|-- Composite
    TransformNode --> Transform : uses
```

---

## Rendering Pipeline Flow

### Frame Processing Sequence

```mermaid
sequenceDiagram
    participant App
    participant Renderer
    participant SceneGraph
    participant Shape
    participant GPU
    
    App->>App: Poll GLFW events
    App->>App: Update camera input
    App->>Renderer: render(delta_time)
    
    Renderer->>Renderer: Calculate view matrix
    Renderer->>Renderer: Calculate projection matrix
    Renderer->>Renderer: Set viewport
    
    Renderer->>SceneGraph: _collect_node(root)
    SceneGraph-->>Renderer: shape_nodes, light_nodes, transform_nodes
    
    Renderer->>Renderer: _apply_shading()
    Renderer->>Renderer: _apply_animation(dt)
    Renderer->>Renderer: _apply_lighting()
    
    loop For each shape
        Renderer->>Shape: lighting(color, pos, camera_pos)
        Shape->>Shape: Upload I_lights, K_materials, shininess
    end
    
    Renderer->>SceneGraph: root.draw(identity, view, proj)
    
    SceneGraph->>SceneGraph: Traverse tree recursively
    
    loop For each GeometryNode
        SceneGraph->>Shape: transform(proj, view, model)
        Shape->>GPU: Upload MVP matrices as uniforms
        
        SceneGraph->>Shape: draw()
        Shape->>GPU: Bind VAO
        Shape->>GPU: glDrawElements / glDrawArrays
        GPU->>GPU: Process vertices
        GPU->>GPU: Rasterize fragments
        GPU->>GPU: Phong lighting calculation
        GPU-->>Shape: Rendered pixels
    end
    
    Renderer-->>App: Frame complete
```

---

## Data Flow: Vertex to Pixel

### Complete Transformation Pipeline

```mermaid
flowchart TD
    A[Vertex Definition] --> B[CPU: Generate Geometry]
    B --> C[CPU: Create Vertex Arrays]
    C --> D[CPU: Upload to GPU via VAO/VBO]
    
    D --> E[GPU: Vertex Shader Input]
    E --> F[GPU: Apply Model Transform]
    F --> G[GPU: Apply View Transform]
    G --> H[GPU: Apply Projection Transform]
    H --> I[GPU: gl_Position in Clip Space]
    
    I --> J[GPU: Perspective Divide]
    J --> K[GPU: Viewport Transform]
    K --> L[GPU: Rasterization]
    
    L --> M[GPU: Fragment Shader Input]
    M --> N{Shading Mode?}
    N -->|Normal| O[Output Normal Colors]
    N -->|Phong| P[Calculate Lighting]
    
    P --> Q[Compute Diffuse]
    P --> R[Compute Specular]
    Q --> S[Combine Components]
    R --> S
    S --> T[Output Final Color]
    O --> T
    
    T --> U[Framebuffer]
    U --> V[Display on Screen]
    
    style A fill:#e1f5ff
    style D fill:#ffe1e1
    style E fill:#e1ffe1
    style M fill:#e1ffe1
    style T fill:#fff3e1
    style V fill:#f0f0f0
```

### Vertex Attribute Flow

```mermaid
graph LR
    A[Vertex Object] --> B[Position xyz]
    A --> C[Color RGB]
    A --> D[Normal xyz]
    A --> E[TexCoord uv]
    
    B --> F[VBO Location 0]
    C --> G[VBO Location 1]
    D --> H[VBO Location 2]
    E --> I[VBO Location 3]
    
    F --> J[layout location=0 in vec3 position]
    G --> K[layout location=1 in vec3 color]
    H --> L[layout location=2 in vec3 norm]
    I --> M[layout location=3 in vec2 texture]
    
    J --> N[Vertex Shader Processing]
    K --> N
    L --> N
    M --> N
    
    N --> O[out vertexColor]
    N --> P[out vertexNorm]
    N --> Q[out vertexCoord]
    N --> R[out textureCoord]
    
    O --> S[Fragment Shader]
    P --> S
    Q --> S
    R --> S
    
    style A fill:#e1f5ff
    style N fill:#ffe1e1
    style S fill:#e1ffe1
```

---

## Component Relationships

### System Architecture Overview

```mermaid
graph TB
    subgraph Application Layer
        A1[App GLFW Window]
        A2[ImGui UI]
        A3[SceneController]
    end
    
    subgraph Rendering Layer
        R1[Renderer]
        R2[Camera]
        R3[Trackball]
    end
    
    subgraph Scene Graph Layer
        S1[Node Tree]
        S2[TransformNode]
        S3[GeometryNode]
        S4[LightNode]
    end
    
    subgraph Graphics Layer
        G1[Shape]
        G2[ShaderProgram]
        G3[VAO/VBO/EBO]
        G4[Texture]
    end
    
    subgraph GPU Layer
        GPU1[Vertex Shader]
        GPU2[Fragment Shader]
        GPU3[Framebuffer]
    end
    
    A1 --> R1
    A2 --> R1
    A3 --> S1
    
    R1 --> R2
    R1 --> R3
    R1 --> S1
    
    S2 --> S1
    S3 --> S1
    S4 --> S1
    
    S3 --> G1
    S4 --> G1
    
    G1 --> G2
    G1 --> G3
    G1 --> G4
    
    G2 --> GPU1
    G2 --> GPU2
    G3 --> GPU1
    
    GPU1 --> GPU2
    GPU2 --> GPU3
    
    style A1 fill:#e1f5ff
    style R1 fill:#ffe1e1
    style S1 fill:#e1ffe1
    style G1 fill:#fff3e1
    style GPU1 fill:#f0e1ff
```

### Lighting System Data Flow

```mermaid
flowchart LR
    subgraph CPU Side
        L1[LightSource Shape] --> L2[Light Position]
        L1 --> L3[Light Color]
        
        L2 --> L4[Transform to Eye-Space]
        L4 --> L5[view × model × pos]
        
        L5 --> L6[Upload to Shader]
        L3 --> L7[Build I_lights Matrix]
        L7 --> L6
        
        M1[Material Properties] --> M2[Build K_materials Matrix]
        M2 --> L6
        
        L6 --> U1[Uniform: lightCoord]
        L6 --> U2[Uniform: I_lights]
        L6 --> U3[Uniform: K_materials]
        L6 --> U4[Uniform: shininess]
    end
    
    subgraph GPU Shader
        U1 --> S1[Fragment Shader]
        U2 --> S1
        U3 --> S1
        U4 --> S1
        
        S1 --> S2[Calculate Light Direction]
        S1 --> S3[Calculate View Direction]
        S1 --> S4[Calculate Reflection]
        
        S2 --> S5[Diffuse = max dot N L]
        S4 --> S6[Specular = pow dot V R]
        
        S5 --> S7[g = diffuse, specular, 0]
        S6 --> S7
        
        S7 --> S8[finalColor = K ⊙ I × g]
        S8 --> S9[Output Color]
    end
    
    style L1 fill:#e1f5ff
    style L6 fill:#ffe1e1
    style S1 fill:#e1ffe1
    style S9 fill:#fff3e1
```

### Scene Graph Traversal

```mermaid
stateDiagram-v2
    [*] --> Root
    
    Root --> CheckNodeType
    
    CheckNodeType --> Node : Is Node
    CheckNodeType --> TransformNode : Is TransformNode
    CheckNodeType --> GeometryNode : Is GeometryNode
    CheckNodeType --> LightNode : Is LightNode
    
    Node --> PassMatrix : Pass parent_matrix unchanged
    TransformNode --> MultiplyMatrix : current = parent × transform
    GeometryNode --> RenderShape : shape.transform() + shape.draw()
    LightNode --> RenderLight : shape.transform() + shape.draw()
    
    PassMatrix --> ProcessChildren
    MultiplyMatrix --> ProcessChildren
    RenderShape --> [*]
    RenderLight --> [*]
    
    ProcessChildren --> CheckNodeType : For each child
    ProcessChildren --> [*] : No more children
```

---

## Matrix Multiplication Chain

### Transformation Sequence

```mermaid
graph LR
    V[Vertex Local Space] -->|Model Matrix| W[World Space]
    W -->|View Matrix| E[Eye Space]
    E -->|Projection Matrix| C[Clip Space]
    C -->|Perspective Divide| N[NDC Space]
    N -->|Viewport Transform| S[Screen Space]
    
    subgraph Scene Graph
        M1[Transform 1] --> M2[Transform 2]
        M2 --> M3[Transform 3]
        M3 --> M4[Final Model = T1 × T2 × T3]
    end
    
    M4 -.->|Accumulated| W
    
    style V fill:#e1f5ff
    style W fill:#ffe1e1
    style E fill:#e1ffe1
    style C fill:#fff3e1
    style N fill:#f0e1ff
    style S fill:#f0f0f0
```

### Example: Rotating Earth Around Sun

```mermaid
graph TD
    A[Identity Matrix] -->|Sun Position| B[Translate 0,0,0]
    A -->|Earth Orbit| C[Rotate Y, angle=t]
    C -->|Earth Position| D[Translate 5,0,0]
    D -->|Earth Spin| E[Rotate Y, angle=2t]
    
    B --> F[Sun Vertex]
    F --> G[Sun World Space]
    
    E --> H[Earth Vertex]
    H --> I[Earth Local Space]
    I -->|Rotate Y, 2t| J[Earth Spinning]
    J -->|Translate 5,0,0| K[Earth Offset]
    K -->|Rotate Y, t| L[Earth Orbiting]
    L --> M[Earth World Space]
    
    style A fill:#e1f5ff
    style G fill:#fff3e1
    style M fill:#e1ffe1
```

---

## Animation System

### Transform Update Flow

```mermaid
sequenceDiagram
    participant Renderer
    participant TransformNode
    participant Transform
    participant AnimationFunc
    
    Renderer->>Renderer: render(delta_time)
    Renderer->>TransformNode: _apply_animation(dt)
    
    loop For each TransformNode
        TransformNode->>Transform: update_matrix(dt)
        
        alt Has animation function
            Transform->>AnimationFunc: animate(self, dt)
            AnimationFunc->>Transform: Modify transform properties
            Note over Transform: e.g., angle += 90 * dt
        end
        
        Transform->>Transform: Recalculate matrix
        Transform-->>TransformNode: Updated matrix
    end
    
    TransformNode-->>Renderer: All animations applied
```

### Animation Example

```mermaid
flowchart TD
    A[Create Rotate Transform] --> B[angle=0, animate=spin_func]
    B --> C[Add to TransformNode]
    C --> D[Renderer calls update_matrix dt]
    
    D --> E{Has animate?}
    E -->|Yes| F[Call animate self, dt]
    F --> G[spin_func: angle += 90*dt]
    G --> H[get_matrix returns rotate Y, angle]
    
    E -->|No| H
    
    H --> I[TransformNode uses matrix]
    I --> J[Children inherit rotation]
    
    style A fill:#e1f5ff
    style F fill:#ffe1e1
    style H fill:#e1ffe1
```

---

## Memory and Resource Management

### OpenGL Resource Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Create : Application Start
    
    Create --> Upload : Generate VAO/VBO/Shader
    Upload --> Bound : glBind*
    Bound --> InUse : Drawing
    InUse --> Bound : Continue using
    Bound --> Unbound : glBind* 0
    Unbound --> Bound : Reactivate
    Unbound --> Delete : Cleanup
    Delete --> [*] : glDelete*
    
    note right of Create
        GL.glGenBuffers
        GL.glGenVertexArrays
        GL.glCreateProgram
    end note
    
    note right of Delete
        GL.glDeleteBuffers
        GL.glDeleteVertexArrays
        GL.glDeleteProgram
    end note
```

### Cleanup Sequence

```mermaid
sequenceDiagram
    participant App
    participant Renderer
    participant Shape
    participant VAO
    participant ShaderProgram
    
    App->>App: User closes window
    App->>Renderer: cleanup()
    
    loop For each node in scene
        Renderer->>Shape: cleanup()
        
        loop For each Part
            Shape->>VAO: cleanup()
            VAO->>VAO: glDeleteVertexArrays
            VAO->>VAO: glDeleteBuffers (VBOs)
            VAO->>VAO: glDeleteBuffers (EBO)
        end
        
        Shape->>ShaderProgram: cleanup()
        ShaderProgram->>ShaderProgram: glDeleteProgram
        
        alt Has Texture
            Shape->>Shape: texture.cleanup()
        end
    end
    
    Renderer->>Renderer: Clear node lists
    Renderer-->>App: Cleanup complete
    App->>App: glfw.terminate()
```

---

## View the Diagrams

To view these diagrams:

1. **GitHub**: Push to GitHub and view the file - Mermaid renders automatically
2. **VS Code**: Install "Markdown Preview Mermaid Support" extension
3. **Online**: Copy diagram code to https://mermaid.live/
4. **Command line**: Use `mmdc` (mermaid-cli) to generate PNG/SVG files

```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Generate diagram images
mmdc -i DIAGRAMS.md -o diagrams.png
```

These diagrams complement the detailed text explanations in `ARCHITECTURE.md` and provide visual understanding of how the rendering engine components interact.
