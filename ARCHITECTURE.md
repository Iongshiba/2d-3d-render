# Architecture Documentation

## Overview

This is a hierarchical 3D rendering engine built with OpenGL and Python. The architecture follows a **Scene Graph** pattern, where objects are organized in a tree structure that defines transformations, geometry, and lighting relationships.

## Table of Contents

- [Core Architecture](#core-architecture)
- [Scene Graph System](#scene-graph-system)
- [Rendering Pipeline](#rendering-pipeline)
- [Class Interactions](#class-interactions)
- [Data Flow](#data-flow)
- [Key Components](#key-components)

---

## Core Architecture

The engine is built around five main subsystems:

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  ┌─────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │  App    │  │    UI    │  │  SceneController     │   │
│  │ (GLFW)  │  │ (ImGui)  │  │  (Scene Management)  │   │
│  └─────────┘  └──────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Rendering Layer                       │
│  ┌──────────┐  ┌────────┐  ┌─────────┐  ┌───────────┐ │
│  │ Renderer │◄─┤ Camera │  │Trackball│  │ Transform │ │
│  └──────────┘  └────────┘  └─────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Scene Graph Layer                     │
│  ┌────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Node  │  │TransformNode │  │ GeometryNode │        │
│  └────────┘  └──────────────┘  └──────────────┘        │
│                                      │                   │
│                                 ┌────────┐              │
│                                 │LightNode              │
│                                 └────────┘              │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Graphics Layer                        │
│  ┌───────┐  ┌────────┐  ┌───────┐  ┌────────┐         │
│  │ Shape │  │ Shader │  │  VAO  │  │ Vertex │         │
│  └───────┘  └────────┘  └───────┘  └────────┘         │
└─────────────────────────────────────────────────────────┘
```

---

## Scene Graph System

The scene graph is a **tree structure** where each node represents either a transformation or a renderable object. This allows hierarchical modeling where transformations propagate down the tree.

### Node Hierarchy

```
                    ┌──────────┐
                    │   Node   │ (Base class)
                    └──────────┘
                         △
                         │
         ┌───────────────┼───────────────┬──────────────┐
         │               │               │              │
  ┌──────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐
  │TransformNode│ │GeometryNode│ │ LightNode  │ │   Node   │
  └──────────────┘ └────────────┘ └────────────┘ └──────────┘
         │               │               │         (Container)
    ┌────────┐      ┌────────┐     ┌────────┐
    │Transform│     │ Shape  │     │ Light  │
    └────────┘      └────────┘     └────────┘
```

### Node Types

#### 1. **Node** (Base)
- **Purpose:** Container node that can hold multiple children
- **Data:** `name`, `children[]`
- **Behavior:** Passes parent transformation matrix to all children unchanged

```python
class Node:
    def draw(self, parent_matrix, view, proj):
        if parent_matrix is None:
            parent_matrix = identity(4)
        for child in self.children:
            child.draw(parent_matrix, view, proj)
```

#### 2. **TransformNode**
- **Purpose:** Applies spatial transformations (translate, rotate, scale)
- **Data:** `Transform` object (or `Composite` of transforms)
- **Behavior:** Multiplies parent matrix with its transform, passes result to children

```python
class TransformNode(Node):
    def draw(self, parent_matrix, view, proj):
        current = parent_matrix @ self.transform.get_matrix()
        for child in self.children:
            child.draw(current, view, proj)
```

#### 3. **GeometryNode**
- **Purpose:** Renders a 3D/2D shape at the current transformation
- **Data:** `Shape` object containing geometry, shader, material
- **Behavior:** Applies accumulated transformation and renders the shape

```python
class GeometryNode(Node):
    def draw(self, parent_matrix, view, proj):
        self.shape.transform(proj, view, parent_matrix)
        self.shape.draw()
```

#### 4. **LightNode**
- **Purpose:** Represents a light source in the scene
- **Data:** `LightSource` shape (often a small sphere/marker)
- **Behavior:** Similar to GeometryNode but tagged for lighting calculations

### Example Scene Graph

Here's how a rotating solar system scene might be structured:

```
Root (Node)
  │
  ├─ SunTransform (TransformNode)
  │    └─ SunGeometry (GeometryNode)
  │          └─ Sphere (Shape)
  │
  ├─ EarthOrbit (TransformNode) [rotation animation]
  │    └─ EarthTransform (TransformNode) [position offset]
  │         └─ EarthGeometry (GeometryNode)
  │               └─ Sphere (Shape)
  │
  └─ LightTransform (TransformNode)
       └─ Light (LightNode)
            └─ LightSource (Shape)
```

**Matrix multiplication chain:**
```
Final position = Projection × View × Parent × Transform × Vertex
```

---

## Rendering Pipeline

### Frame Rendering Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. Application Loop (app.run)                           │
│    ├─ Poll GLFW events                                  │
│    ├─ Update UI (ImGui)                                 │
│    ├─ Update camera movement                            │
│    └─ Call renderer.render(delta_time)                  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Renderer Setup                                        │
│    ├─ Calculate projection matrix (camera/trackball)    │
│    ├─ Calculate view matrix (camera/trackball)          │
│    ├─ Set viewport                                      │
│    └─ Clear buffers                                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Scene Graph Traversal                                │
│    ├─ _collect_node(root)                              │
│    │   ├─ Find all GeometryNodes → shape_nodes[]       │
│    │   ├─ Find all LightNodes → light_nodes[]          │
│    │   └─ Find all TransformNodes → transform_nodes[]  │
│    │                                                     │
│    ├─ _apply_shading()                                 │
│    │   └─ Set shading mode for all shapes              │
│    │                                                     │
│    ├─ _apply_animation(dt)                             │
│    │   └─ Update all transform matrices                │
│    │                                                     │
│    └─ _apply_lighting()                                │
│        └─ Send light data to all shapes                │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Scene Draw (root.draw)                               │
│    └─ Recursive tree traversal:                         │
│        ├─ Node: pass matrix unchanged                   │
│        ├─ TransformNode: multiply parent × transform    │
│        └─ GeometryNode: render shape with final matrix  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 5. Shape Rendering                                      │
│    ├─ shape.transform(proj, view, model)               │
│    │   └─ Upload matrices as uniforms to shader        │
│    │                                                     │
│    └─ shape.draw()                                      │
│        ├─ Activate shader program                       │
│        ├─ For each Part:                                │
│        │   ├─ Bind VAO                                  │
│        │   ├─ Bind texture (if present)                │
│        │   ├─ glDrawElements or glDrawArrays           │
│        │   └─ Unbind VAO                                │
│        └─ Deactivate shader                             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 6. GPU Rendering                                        │
│    ├─ Vertex Shader (phong.vert)                       │
│    │   ├─ Transform vertices: proj × camera × transform│
│    │   ├─ Calculate eye-space coords & normals         │
│    │   └─ Pass to fragment shader                      │
│    │                                                     │
│    └─ Fragment Shader (phong.frag)                     │
│        ├─ Phong lighting calculation                    │
│        ├─ Combine diffuse + specular + ambient         │
│        └─ Output final color                            │
└─────────────────────────────────────────────────────────┘
```

---

## Class Interactions

### High-Level Component Interaction

```
┌──────────┐
│   App    │ Creates and manages window, input, main loop
└─────┬────┘
      │ owns
      ▼
┌──────────┐         ┌──────────────┐
│ Renderer │◄────────┤SceneController│ Builds scenes from templates
└─────┬────┘  sets   └──────────────┘
      │ scene
      │
      ▼
┌──────────────────────────────────────┐
│         Scene Graph Tree              │
│                                       │
│  Root (Node)                          │
│    ├─ TransformNode                  │
│    │    └─ GeometryNode              │
│    │         └─ Shape ───┐           │
│    │                     │           │
│    └─ LightNode          │           │
│         └─ LightSource   │           │
│                          │           │
└──────────────────────────┼───────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │  GPU Resources │
                  │  ┌───────┐     │
                  │  │  VAO  │     │
                  │  │  VBO  │     │
                  │  │  EBO  │     │
                  │  │Shader │     │
                  │  │Texture│     │
                  │  └───────┘     │
                  └────────────────┘
```

### Detailed Shape Rendering

```
┌─────────────────────────────────────────────────────────┐
│                      Shape Class                         │
├─────────────────────────────────────────────────────────┤
│ Data:                                                    │
│  • shader_program (ShaderProgram)                       │
│  • shapes[] (list of Part)                              │
│  • texture (Texture2D, optional)                        │
│  • Uniform locations (transform, camera, project, etc)  │
│                                                          │
│ Methods:                                                 │
│  • __init__() - Compile shaders, get uniform locations  │
│  • transform() - Upload MVP matrices to shader          │
│  • lighting() - Upload light data (I_lights, K_materials)│
│  • draw() - Bind VAO, issue draw calls                  │
└─────────────────────────────────────────────────────────┘
                          │
                          │ contains
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      Part Class                          │
├─────────────────────────────────────────────────────────┤
│ Data:                                                    │
│  • vao (VAO) - Vertex Array Object                      │
│  • draw_mode (GL.GL_TRIANGLES, GL.GL_TRIANGLE_STRIP...)│
│  • vertex_num (int)                                      │
│  • index_num (int, optional)                            │
└─────────────────────────────────────────────────────────┘
                          │
                          │ contains
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      VAO Class                           │
├─────────────────────────────────────────────────────────┤
│ Data:                                                    │
│  • vao (OpenGL VAO handle)                              │
│  • vbos{} (dict of VBO handles by location)            │
│  • ebo (Element Buffer Object, optional)                │
│                                                          │
│ Methods:                                                 │
│  • add_vbo() - Create VBO for attribute (pos, color...) │
│  • add_ebo() - Create EBO for indexed drawing           │
│  • activate() - glBindVertexArray(vao)                  │
│  • deactivate() - glBindVertexArray(0)                  │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Vertex Data Flow (CPU → GPU)

```
1. Shape Construction (e.g., Sphere)
   │
   ├─ Generate vertices (positions, colors, normals, texcoords)
   │   └─ Create Vertex objects
   │
   ├─ Convert to numpy arrays
   │   ├─ positions: float32[N, 3]
   │   ├─ colors: float32[N, 3]
   │   ├─ normals: float32[N, 3]
   │   └─ texcoords: float32[N, 2]
   │
   └─ Create VAO + VBOs
       ├─ VAO.add_vbo(location=0, data=positions)
       ├─ VAO.add_vbo(location=1, data=colors)
       ├─ VAO.add_vbo(location=2, data=normals)
       ├─ VAO.add_vbo(location=3, data=texcoords)
       └─ VAO.add_ebo(data=indices)

                    ▼ UPLOAD TO GPU ▼

2. GPU Vertex Attributes (Shader Input)
   layout (location = 0) in vec3 position;
   layout (location = 1) in vec3 color;
   layout (location = 2) in vec3 norm;
   layout (location = 3) in vec2 texture;

3. Vertex Shader Processing (phong.vert)
   │
   ├─ Transform: gl_Position = project × camera × transform × position
   ├─ Eye-space coords: vertexCoord = camera × transform × position
   ├─ Eye-space normals: vertexNorm = normalMatrix × norm
   │
   └─ Output to fragment shader:
       ├─ vertexColor
       ├─ vertexNorm
       ├─ vertexCoord
       └─ textureCoord

4. Fragment Shader Processing (phong.frag)
   │
   ├─ Receive interpolated values from vertex shader
   ├─ Phong lighting calculation:
   │   ├─ Diffuse: max(dot(N, L), 0)
   │   ├─ Specular: pow(max(dot(R, V), 0), shininess)
   │   └─ Combine: finalColor = K_materials × I_lights × [diffuse, specular]
   │
   └─ Output: color = vec4(finalColor, 1.0)
```

### Matrix Transformation Flow

```
Object Space → World Space → Eye Space → Clip Space → Screen Space
    │              │             │           │             │
    │              │             │           │             │
  Vertex      Model Matrix   View Matrix  Projection    Viewport
 Position         (M)            (V)       Matrix (P)  Transform
    │              │             │           │             │
    └──────────────┴─────────────┴───────────┴─────────────┘
                           │
                           ▼
              gl_Position = P × V × M × vertex
```

**Transformation Order in Scene Graph:**

```
Root Transform (Identity)
  │
  ├─ Parent Transform A (e.g., Translate(5, 0, 0))
  │    │
  │    └─ Child Transform B (e.g., Rotate(Y, 45°))
  │         │
  │         └─ Vertex Position
  │
  └─ Final Transform = P × V × A × B × vertex
```

---

## Key Components

### 1. Camera & Trackball

**Camera** provides a traditional FPS-style view:
- **Position**: Eye position in world space
- **Front/Up/Right**: Basis vectors defining orientation
- **View Matrix**: `R × T` (rotation × translation)
- **Projection**: Perspective with FOV

**Trackball** provides orbital viewing:
- **Rotation**: Quaternion-based rotation
- **Distance**: Zoom level from target
- **Position 2D**: Pan offset
- **View Matrix**: `T(-distance) × R(quaternion) × Pan`

### 2. Transform System

```
Transform (Base)
  │
  ├─ Translate(x, y, z)
  ├─ Scale(x, y, z)
  ├─ Rotate(axis, angle)
  └─ Composite([transforms...])
       │
       └─ get_matrix() = T₁ × T₂ × ... × Tₙ
```

**Animation Support:**
```python
def spin_animation(transform, dt):
    transform.angle += 90 * dt  # 90°/sec

Rotate(axis=(0,1,0), angle=0, animate=spin_animation)
```

### 3. Lighting System (Eye-Space Phong)

**Light Position Transformation:**
```python
# In LightSource.transform():
eye_space_pos = view_matrix × model_matrix × light_position
```

**Fragment Shader Calculation:**
```glsl
// All in eye-space:
vec3 N = normalize(vertexNorm);
vec3 L = normalize(lightCoord - vertexCoord);
vec3 V = normalize(-vertexCoord);  // Camera at origin in eye-space
vec3 R = reflect(-L, N);

float diffuse = max(dot(N, L), 0.0);
float specular = pow(max(dot(V, R), 0.0), shininess);

vec3 g = vec3(diffuse, specular, 0.0);
vec3 finalColor = (K_materials ⊙ I_lights) × g;
// ⊙ = component-wise multiply (matrixCompMult)
```

**Material & Light Matrices:**
```
I_lights = [I_diffuse  I_specular  unused]  (3×3, RGB rows)
K_materials = [K_d  K_s  unused]            (3×3, RGB rows)
```

### 4. Shader System

```
┌──────────────┐
│    Shader    │ Compiles GLSL source
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ShaderProgram │ Links vertex + fragment shaders
└──────┬───────┘
       │
       ▼
  Uniform Setup
  ├─ transform (mat4)
  ├─ camera (mat4)
  ├─ project (mat4)
  ├─ I_lights (mat3)
  ├─ K_materials (mat3)
  ├─ shininess (float)
  └─ lightCoord (vec3)
```

### 5. Template System

**SceneController** manages multiple pre-built scenes:

```python
scenes = {
    "atom": Scene(name="atom", builder=create_atom_scene),
    "molecule": Scene(name="molecule", builder=create_molecule_scene),
    "gradient_descent": Scene(...),
}

controller.set_current("atom")
root = controller.get_current_root()
renderer.set_scene(root)
```

Each template's builder function constructs a scene graph:
```python
def create_atom_scene():
    root = Node("atom_scene")
    
    # Create nucleus
    nucleus = TransformNode(
        "nucleus",
        Scale(2.0),
        [GeometryNode("nucleus_geom", Sphere(...))]
    )
    
    # Create orbiting electrons
    for i in range(3):
        orbit = TransformNode(
            f"orbit_{i}",
            Rotate(axis=(0,1,0), angle=0, animate=spin),
            [TransformNode(
                "electron_pos",
                Translate(5, 0, 0),
                [GeometryNode("electron", Sphere(...))]
            )]
        )
        root.add(orbit)
    
    return root
```

---

## Complete Rendering Example

Let's trace a complete frame for a simple rotating cube:

### 1. Scene Setup
```python
# Build scene graph
root = Node("scene")
rotation = TransformNode(
    "rotation",
    Rotate(axis=(0,1,0), angle=45),  # 45° rotation
    [GeometryNode("cube", Cube())]
)
root.add(rotation)

renderer.set_scene(root)
```

### 2. Frame Loop
```python
# app.run() → renderer.render(dt)

# Calculate matrices
view = camera.get_view_matrix()      # Camera transform
proj = camera.get_projection_matrix() # Perspective

# Traverse scene graph
renderer._collect_node(root)
# Found: shape_nodes = [cube_geometry_node]

renderer._apply_lighting()
# cube.lighting(light_color, light_pos_eye_space, camera_pos)

# Draw scene
root.draw(None, view, proj)
```

### 3. Scene Draw (Recursion)
```python
# root.draw(None, view, proj)
parent = Identity(4)

# rotation.draw(parent, view, proj)
current = parent @ Rotate(Y, 45°)
    
    # cube_geometry.draw(current, view, proj)
    cube.transform(proj, view, current)
    # Uploads: proj, view, model=current
    
    cube.draw()
    # Binds VAO, draws triangles
```

### 4. GPU Processing
```glsl
// Vertex Shader
vec4 worldPos = transform × vec4(position, 1.0);
vec4 eyePos = camera × worldPos;
gl_Position = project × eyePos;

// Fragment Shader
vec3 L = normalize(lightCoord - vertexCoord);
vec3 N = normalize(vertexNorm);
float diffuse = max(dot(N, L), 0.0);
// ... specular calculation ...
color = vec4(finalColor, 1.0);
```

---

## Summary

The architecture achieves modularity through:

1. **Scene Graph** - Hierarchical organization with automatic transformation propagation
2. **Node Abstraction** - Uniform interface for containers, transforms, and geometry
3. **Shape Factory** - Centralized creation of different geometric primitives
4. **Renderer** - Decoupled from scene structure, works with any scene graph
5. **Template System** - Reusable scene builders for complex demonstrations

**Key Design Patterns:**
- **Composite Pattern** - Scene graph nodes
- **Visitor Pattern** - Renderer traverses and collects nodes
- **Factory Pattern** - ShapeFactory for shape creation
- **Strategy Pattern** - Different Transform types, Camera vs Trackball

This allows easy construction of complex animated scenes from simple building blocks!
