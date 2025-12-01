# Quick Reference Guide

A concise reference for understanding and working with the 2D/3D rendering engine.

## Table of Contents
- [Quick Start](#quick-start)
- [Scene Graph Cheat Sheet](#scene-graph-cheat-sheet)
- [Common Patterns](#common-patterns)
- [Shader Uniforms](#shader-uniforms)
- [Transformation Reference](#transformation-reference)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Creating a Simple Scene

```python
from graphics.scene import Node, TransformNode, GeometryNode
from rendering.world import Translate, Rotate, Scale
from shape.sphere import Sphere

# 1. Create shapes
sphere = Sphere(radius=2.0, sector=40, stack=40)

# 2. Build scene graph
root = Node("my_scene")

transform = TransformNode(
    "sphere_transform",
    Translate(0, 0, -5),  # Move back 5 units
    [GeometryNode("sphere_geom", sphere)]
)

root.add(transform)

# 3. Set scene in renderer
renderer.set_scene(root)
```

### Adding a Light

```python
from shape.light_source import LightSource

light = LightSource(color=(1.0, 1.0, 1.0))

light_transform = TransformNode(
    "light_position",
    Translate(10, 10, 10),
    [LightNode("main_light", light)]
)

root.add(light_transform)
```

---

## Scene Graph Cheat Sheet

### Node Types Quick Reference

| Node Type | Purpose | Key Method | Contains |
|-----------|---------|------------|----------|
| `Node` | Container | Passes matrix unchanged | Children nodes |
| `TransformNode` | Apply transform | Multiplies matrix | Transform + Children |
| `GeometryNode` | Render shape | Draws geometry | Shape |
| `LightNode` | Light source | Draws + provides light data | LightSource |

### Scene Graph Rules

✅ **DO:**
- Use `TransformNode` for positioning/rotation/scaling
- Nest `TransformNode` for hierarchical transformations
- Put `GeometryNode` as leaf or near-leaf nodes
- Include at least one `LightNode` for Phong shading

❌ **DON'T:**
- Put `GeometryNode` as parent of `TransformNode` (won't work as expected)
- Forget to add nodes to the root with `root.add(child)`
- Modify matrices directly (use Transform objects)

---

## Common Patterns

### Pattern 1: Static Object

```python
# Single object at fixed position
root = Node("scene")
root.add(TransformNode(
    "position",
    Translate(x, y, z),
    [GeometryNode("object", shape)]
))
```

### Pattern 2: Rotating Object

```python
def spin(transform, dt):
    transform.angle += 90 * dt  # 90 degrees/sec

root.add(TransformNode(
    "rotation",
    Rotate(axis=(0, 1, 0), angle=0, animate=spin),
    [GeometryNode("object", shape)]
))
```

### Pattern 3: Orbiting Objects

```python
# Parent rotates (orbit), child translates (distance), grandchild spins
orbit = TransformNode("orbit", Rotate((0,1,0), 0, animate=orbit_spin))
distance = TransformNode("distance", Translate(5, 0, 0))
local_spin = TransformNode("spin", Rotate((0,1,0), 0, animate=self_spin))

orbit.add(distance)
distance.add(local_spin)
local_spin.add(GeometryNode("planet", sphere))

root.add(orbit)
```

### Pattern 4: Grouped Objects

```python
# Multiple objects sharing a transform
group = TransformNode("group", Scale(2.0))

group.add(GeometryNode("obj1", shape1))
group.add(GeometryNode("obj2", shape2))
group.add(GeometryNode("obj3", shape3))

root.add(group)
```

### Pattern 5: Composite Transform

```python
from rendering.world import Composite

# Combine multiple transformations
combined = Composite([
    Translate(5, 0, 0),
    Rotate((0, 1, 0), 45),
    Scale(2.0, 2.0, 2.0)
])

root.add(TransformNode("object", combined, [GeometryNode(...)]))
```

---

## Shader Uniforms

### Transformation Matrices

| Uniform | Type | Purpose | Set By |
|---------|------|---------|--------|
| `transform` | mat4 | Model matrix | `shape.transform()` |
| `camera` | mat4 | View matrix | `shape.transform()` |
| `project` | mat4 | Projection matrix | `shape.transform()` |

**Usage in shader:**
```glsl
gl_Position = project * camera * transform * vec4(position, 1.0);
```

### Lighting (Phong Eye-Space)

| Uniform | Type | Purpose | Set By |
|---------|------|---------|--------|
| `lightCoord` | vec3 | Light position (eye-space) | `shape.lighting()` |
| `I_lights` | mat3 | Light intensities [diffuse\|specular\|unused] | `shape.lighting()` |
| `K_materials` | mat3 | Material coefficients [Kd\|Ks\|unused] | `shape.lighting()` |
| `shininess` | float | Specular exponent | `shape.lighting()` |
| `shadingMode` | int | 0=Normal, 1=Phong | `shape.set_shading_mode()` |

**Matrix structure:**
```python
I_lights = [
    [I_r_diffuse,  I_r_specular,  0],  # Red channel
    [I_g_diffuse,  I_g_specular,  0],  # Green channel
    [I_b_diffuse,  I_b_specular,  0]   # Blue channel
]

K_materials = [
    [Kd_r,  Ks_r,  0],  # Red reflectance
    [Kd_g,  Ks_g,  0],  # Green reflectance
    [Kd_b,  Ks_b,  0]   # Blue reflectance
]
```

### Texture

| Uniform | Type | Purpose | Set By |
|---------|------|---------|--------|
| `use_texture` | bool | Enable texture mapping | `shape.draw()` |
| `textureData` | sampler2D | Texture sampler | Constructor |

---

## Transformation Reference

### Transform Types

#### Translate
```python
Translate(x, y, z)
Translate(x=5.0, y=0.0, z=-3.0)
```

#### Rotate
```python
Rotate(axis=(0, 1, 0), angle=45)           # Degrees
Rotate(axis=(1, 0, 0), radians=math.pi/4)  # Radians
```

#### Scale
```python
Scale(2.0)              # Uniform: x=y=z=2.0
Scale(2.0, 3.0, 1.0)    # Non-uniform
```

#### Composite
```python
Composite([
    Translate(5, 0, 0),
    Rotate((0, 1, 0), 45),
    Scale(2.0)
])
# Result: T × R × S (applied right-to-left)
```

### Animation Functions

```python
# Rotation animation
def spin_y(transform, dt):
    transform.angle += 90 * dt  # 90°/sec

# Oscillation animation
def oscillate(transform, dt):
    transform.x = 5 * math.sin(glfw.get_time())

# Complex animation
import glfw
def orbit(transform, dt):
    t = glfw.get_time()
    transform.angle = t * 30  # 30°/sec
```

**Usage:**
```python
Rotate(axis=(0,1,0), angle=0, animate=spin_y)
Translate(x=0, y=0, z=0, animate=oscillate)
```

---

## Camera & View Control

### Camera (FPS Style)

```python
# In renderer
renderer.camera.position = np.array([0, 5, 10])
renderer.camera.fov = 60.0

# Movement (typically bound to keys)
renderer.move_camera(CameraMovement.FORWARD, delta_time)
renderer.move_camera(CameraMovement.BACKWARD, delta_time)
renderer.move_camera(CameraMovement.LEFT, delta_time)
renderer.move_camera(CameraMovement.RIGHT, delta_time)

# Rotation (typically mouse callback)
renderer.rotate_camera(old_pos, new_pos)
```

### Trackball (Orbital View)

```python
# Enable trackball mode
renderer.use_trackball = True

# Rotation (left mouse drag)
renderer.rotate_trackball(old_pos, new_pos, winsize)

# Pan (right mouse drag)
renderer.move_trackball(old_pos, new_pos)

# Zoom (scroll wheel)
renderer.zoom_trackball(delta_y, winsize[1])
```

---

## Shape Creation

### Using ShapeFactory

```python
from shape.factory import ShapeFactory
from config import ShapeType, ShapeConfig

config = ShapeConfig()
config.sphere_radius = 3.0
config.sphere_sectors = 50
config.sphere_stacks = 50
config.base_color = (1.0, 0.0, 0.0)  # Red

sphere = ShapeFactory.create_shape(ShapeType.SPHERE, config)
```

### Available Shape Types

**3D Shapes:**
- `SPHERE`, `CUBE`, `CYLINDER`, `CONE`, `TRUNCATED_CONE`
- `TETRAHEDRON`, `TORUS`, `HEART`

**2D Shapes:**
- `TRIANGLE`, `RECTANGLE`, `PENTAGON`, `HEXAGON`
- `CIRCLE`, `ELLIPSE`, `STAR`, `TRAPEZOID`, `ARROW`

**Special:**
- `LIGHT_SOURCE`, `MODEL`, `EQUATION`

### Direct Construction

```python
from shape.sphere import Sphere

sphere = Sphere(
    radius=2.0,
    sector=40,
    stack=40,
    color=(1.0, 0.5, 0.0),        # Optional: override color
    texture_file="path/to/tex.png", # Optional: texture
    gradient_mode=GradientMode.RADIAL  # Optional: gradient
)
```

---

## Rendering Pipeline Summary

### Initialization Phase
1. Create `App` (GLFW window)
2. Create `Renderer` with config
3. Build scene graph (`Node` tree)
4. `renderer.set_scene(root)`
5. `app.add_renderer(renderer)`

### Frame Loop
1. **Input**: Poll events, update camera
2. **Update**: Animation transforms, calculate view/projection
3. **Collect**: Traverse scene graph, collect nodes by type
4. **Apply**: Set shading, lighting, animations
5. **Draw**: Recursive `root.draw()` traversal
   - `TransformNode`: multiply matrices
   - `GeometryNode`: `shape.transform()` + `shape.draw()`
6. **Present**: Swap buffers

---

## Troubleshooting

### Common Issues

#### Objects Not Visible

**Symptoms:** Black screen, nothing renders

**Solutions:**
- ✅ Check camera position: `renderer.camera.position`
- ✅ Check object is within view frustum (try moving camera back)
- ✅ Verify scene graph: `renderer.set_scene(root)` called?
- ✅ Check light position: too far or behind objects?
- ✅ Enable trackball mode for easier navigation: `renderer.use_trackball = True`

#### Objects Too Dark

**Symptoms:** Objects visible but barely lit

**Solutions:**
- ✅ Check light color: `LightSource(color=(1.0, 1.0, 1.0))`
- ✅ Check light position: should be near objects
- ✅ Verify shading mode: `renderer.set_shading_model(ShadingModel.PHONG)`
- ✅ Check material properties in `shape.lighting()`

#### Objects Flickering

**Symptoms:** Z-fighting, depth issues

**Solutions:**
- ✅ Enable depth test: `GL.glEnable(GL.GL_DEPTH_TEST)` (done in Renderer)
- ✅ Clear depth buffer: `GL.glClear(GL.GL_DEPTH_BUFFER_BIT)` (done in App)
- ✅ Check near/far planes in camera config
- ✅ Avoid overlapping geometry at same depth

#### Transformations Not Working

**Symptoms:** Objects at wrong position/rotation

**Solutions:**
- ✅ Check transformation order in `Composite`: right-to-left application
- ✅ Verify node hierarchy: parent → child relationship
- ✅ Check if using degrees vs radians: `Rotate(axis, angle)` uses degrees by default
- ✅ Ensure `TransformNode` is parent of `GeometryNode`, not vice versa

#### Animation Not Running

**Symptoms:** Objects static despite animation function

**Solutions:**
- ✅ Check `animate` parameter passed to Transform constructor
- ✅ Verify `renderer.render(delta_time)` called each frame with non-zero `dt`
- ✅ Ensure `_apply_animation()` called in renderer
- ✅ Check animation function modifies transform properties correctly

#### Shader Compilation Errors

**Symptoms:** RuntimeError with GLSL error log

**Solutions:**
- ✅ Check shader file paths in config
- ✅ Verify OpenGL version compatibility (requires 3.3+)
- ✅ Check for typos in uniform names between CPU and shader code
- ✅ Ensure vertex attribute locations match VBO setup

---

## Performance Tips

### Optimization Checklist

1. **Geometry:**
   - ✅ Use appropriate sector/stack counts (don't over-tessellate)
   - ✅ Share shapes between multiple `GeometryNode` instances
   - ✅ Use indexed drawing (EBO) when possible

2. **Shaders:**
   - ✅ Avoid uploading uniforms every frame if unchanged
   - ✅ Compute expensive operations (inverse matrices) on CPU
   - ✅ Use uniform buffers for shared data across shapes

3. **Scene Graph:**
   - ✅ Flatten unnecessary nested `TransformNode` when possible
   - ✅ Avoid deep hierarchies (combine transforms with `Composite`)
   - ✅ Don't create new nodes every frame

4. **Rendering:**
   - ✅ Enable face culling for closed objects: `GL.glEnable(GL.GL_CULL_FACE)`
   - ✅ Use VSync to prevent excessive frame rates
   - ✅ Batch similar objects when possible

---

## Debugging Helpers

### Print Scene Graph Structure

```python
def print_tree(node, depth=0):
    indent = "  " * depth
    name = node.name if hasattr(node, 'name') else type(node).__name__
    print(f"{indent}{name}")
    if hasattr(node, 'children'):
        for child in node.children:
            print_tree(child, depth + 1)

print_tree(root)
```

### Check Current Camera Position

```python
print(f"Camera position: {renderer.camera.position}")
print(f"Camera front: {renderer.camera.front}")
print(f"Camera FOV: {renderer.camera.fov}")
```

### Count Scene Objects

```python
renderer._collect_node(root)
print(f"Geometry nodes: {len(renderer.shape_nodes)}")
print(f"Light nodes: {len(renderer.light_nodes)}")
print(f"Transform nodes: {len(renderer.transform_nodes)}")
```

### Wireframe Mode

```python
renderer.toggle_wireframe()  # Shows mesh structure
```

### Normal Visualization

```python
renderer.set_shading_model(ShadingModel.NORMAL)
# Objects display surface normals as RGB colors
```

---

## Quick Command Reference

### Run Application

```powershell
python run.py
```

### Controls (Default)

| Key/Mouse | Action |
|-----------|--------|
| W/A/S/D | Move camera (FPS mode) |
| Left Mouse Drag | Rotate view (trackball) |
| Right Mouse Drag | Pan view (trackball) |
| Scroll Wheel | Zoom in/out |
| F | Toggle wireframe |
| Q / ESC | Quit |

### Template Selection (UI)

- Use ImGui panel on the right side
- Dropdown menus for:
  - **Templates**: Pre-built scenes (atom, molecule, etc.)
  - **2D Shapes**: Flat geometric primitives
  - **3D Shapes**: Volumetric objects
  - **Shading**: Normal or Phong
  - **Color Preset**: Pre-defined color schemes
  - **Gradient**: Color gradient modes

---

## Additional Resources

- **Main Documentation**: `ARCHITECTURE.md` - Detailed architecture explanation
- **Visual Diagrams**: `DIAGRAMS.md` - Mermaid diagrams of system components
- **Project README**: `README.md` - Setup and feature overview
- **Code Examples**: `template/` directory - Pre-built scene examples

---

## Examples from Codebase

### Atom Scene (template/atom.py)

```python
def create_atom_scene():
    root = Node("atom")
    
    # Nucleus
    nucleus = Sphere(radius=2.0, ...)
    root.add(GeometryNode("nucleus", nucleus))
    
    # Electrons orbiting
    for i in range(3):
        orbit_angle = i * 120  # 120° apart
        
        orbit = TransformNode(
            f"orbit_{i}",
            Rotate((0,0,1), orbit_angle, animate=spin),
            [TransformNode(
                "electron_offset",
                Translate(5, 0, 0),
                [GeometryNode(f"electron_{i}", Sphere(radius=0.5, ...))]
            )]
        )
        root.add(orbit)
    
    # Light
    light = LightSource()
    root.add(TransformNode("light", Translate(10,10,10), [LightNode("light", light)]))
    
    return root
```

### Molecule Scene (template/molecule.py)

Creates a more complex hierarchical structure with multiple atoms connected by bonds, demonstrating nested transforms and multiple geometry nodes.

---

This quick reference provides the essential information needed to work with the rendering engine. For deeper understanding, refer to the detailed architecture documentation.
