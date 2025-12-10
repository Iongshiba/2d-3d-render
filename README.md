# 2D/3D Rendering Engine

A Python-based OpenGL rendering engine for 2D and 3D shapes with molecular visualization support.

![](https://github.com/Iongshiba/2d-3d-render/blob/4e4a5649a3dc5ce15eaecc13a67afb31ca24bef8/demo/view.gif)

## Requirements

- Python 3.11
- OpenGL-capable graphics card

## Setup

### 1. Install Python 3.11

Make sure you have Python 3.11 installed:

```bash
python3.11 --version
```

### 2. Clone the Repository

```bash
git clone https://github.com/Iongshiba/2d-3d-render.git
cd 2d-3d-render
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies include:**
- `numpy` - Numerical computations
- `scipy` - Scientific computing
- `pillow` - Image processing
- `opencv-python` - Computer vision (for segmentation masks)
- `PyOpenGL` - OpenGL bindings
- `glfw` - Window and input management
- `imgui[glfw]` - UI rendering
- `pyassimp` - 3D model loading (GLTF, FBX, etc.)
- `plyfile` - PLY format support

### 4. Install Assimp Library (Windows)

For loading OBJ and other 3D formats, you need the Assimp native library:

**Windows:**
1. Download `assimp-vc143-mt.dll` from [Assimp releases](https://github.com/assimp/assimp/releases)
2. Place the DLL file in the **root project directory** (same folder as `data_synthesis_app.py`)

**Linux/macOS:**
```bash
# Ubuntu/Debian
sudo apt-get install libassimp-dev

# macOS
brew install assimp
```

### 5. Run the Application

Run the `run.py` script:

```bash
python run.py
```

## Controls

### Camera & Navigation
- **W/A/S/D** - Move camera forward/left/backward/right
- **Mouse drag (left button)** - Rotate view / Orbit camera
- **Mouse drag (right button)** - Pan view (trackball mode)
- **Mouse scroll** - Zoom in/out

### Rendering Modes
- **F** - Toggle wireframe mode

### Texture Modes
- **T** - Toggle texture

### Application
- **Q / ESC** - Quit application

## Features

### Shape Library
- **20+ 3D shapes**: sphere, cube, cylinder, cone, torus, heart, tetrahedron, truncated cone, and more
- **2D shapes**: triangle, rectangle, pentagon, hexagon, circle, ellipse, star, arrow, trapezoid
- **3D model loading**: Load .obj and .ply files with texture support

### Rendering & Shading
- **Phong shading**: Realistic lighting with specular highlights
- **Gouraud shading**: Per-vertex lighting interpolation
- **Normal visualization**: Debug mode showing surface normals as colors
- **Wireframe mode**: Toggle between solid and wireframe rendering

### Pre-built Scenes
- **Molecular structures**: Atom models, water (H₂O), carbon dioxide (CO₂)
- **Gradient descent visualizer**: Animated optimization paths (Adam, Adagrad, RMSprop)
- **Custom templates**: Heart orbit, shape gallery, and more

## Project Structure

```
root/
├── run.py              # Main entry point
├── app.py              # Application window and UI
├── config/             # Configuration and enums
│   ├── enums.py        # ModelVisualizationMode, ShadingModel, etc.
│   └── palette.py      # Color presets
├── graphics/           # Shaders, buffers, textures
│   ├── shader.py       # GLSL shader compilation
│   ├── buffer.py       # VAO/VBO management
│   └── *.vert/*.frag   # Vertex and fragment shaders
├── rendering/          # Camera, renderer, animations
│   ├── renderer.py     # Main rendering pipeline
│   └── camera.py       # Camera and trackball controls
├── shape/              # 3D/2D shape implementations
│   ├── model.py        # 3D model loader with visualization modes
│   ├── sphere.py       # Parametric sphere
│   └── ...             # Other shape primitives
├── template/           # Pre-built scenes (atom, molecule, etc.)
├── utils/              # Utility modules
│   ├── dataset_export.py  # COCO/YOLO dataset exporter                         (not used anymore)
│   ├── misc.py         # Model/texture loading utilities
│   └── transform.py    # Matrix transformations
├── textures/           # Texture image files
├── assets/             # 3D model files (.obj, .ply)
└── dataset/            # Generated dataset exports (created on first export)   (not used anymore)
    ├── coco/           # COCO format: images, depth, masks, annotations.json   (not used anymore)
    └── yolo/           # YOLO format: images, labels, depth, masks, data.yaml  (not used anymore)
```

## Troubleshooting

**Linux users:** If you encounter display issues, set the OpenGL platform:
```bash
export PYOPENGL_PLATFORM=egl
```

**Import errors:** Make sure you're running from the `engine` directory where all modules are located.

**OpenGL errors:** Update your graphics drivers to the latest version.
