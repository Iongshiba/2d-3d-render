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

### 2. Install Dependencies

```bash
pip install numpy PyOpenGL glfw imgui[glfw] Pillow
```

### 3. Run the Application

Run the `run.py` script:

```bash
python run.py
```

## Controls

- **W/A/S/D** - Move camera (needs to modify the code a bit)
- **Mouse drag (left button)** - Rotate view
- **Mouse drag (right button)** - Pan view
- **Mouse scroll** - Zoom in/out
- **F** - Toggle wireframe mode
- **T** - Toggle texture mapping (for shapes with texture support)
- **B** - Toggle bounding box visualization (3D models)
- **N** - Toggle depth map visualization (3D models)
- **M** - Toggle segmentation mask visualization (3D models)
- **V** - Export dataset (COCO and YOLO formats)
- **Q / ESC** - Quit application

## Features

- 20+ 3D shapes (sphere, cube, cylinder, cone, torus, heart, etc.)
- 2D shapes (triangle, rectangle, pentagon, hexagon, circle, etc.)
- Phong shading and normal visualization
- Pre-built molecular structures (atoms, molecules, water, CO₂)
- Gradient descent visualizer (adam, adagrad, rmsdrop)
- Custom scene builder with orbiting objects
- **Dataset export** - Export rendered models with bounding boxes, depth maps, and segmentation masks in COCO and YOLO formats

## Project Structure

```
root/
├── run.py              # Main entry point
├── app.py              # Application window and UI
├── config/             # Configuration and enums
├── graphics/           # Shaders, buffers, textures
├── rendering/          # Camera, renderer, animations
├── shape/              # 3D/2D shape implementations
├── template/           # Pre-built scenes (atom, molecule, etc.)
└── textures/           # Texture image files
```

## Documentation

📚 **Comprehensive documentation is available:**

- **[INDEX.md](INDEX.md)** - Documentation index and navigation guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture and design explanation
- **[DIAGRAMS.md](DIAGRAMS.md)** - Visual diagrams (Mermaid) showing system components
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Cheat sheet for common tasks and troubleshooting
- **[DATASET_EXPORT.md](DATASET_EXPORT.md)** - Dataset export feature documentation (COCO and YOLO formats)

**Quick Links:**
- [How the Scene Graph works](ARCHITECTURE.md#scene-graph-system)
- [Rendering pipeline explained](ARCHITECTURE.md#rendering-pipeline)
- [Visual component diagrams](DIAGRAMS.md#class-hierarchy)
- [Common code patterns](QUICK_REFERENCE.md#common-patterns)
- [Troubleshooting guide](QUICK_REFERENCE.md#troubleshooting)
- [Dataset export guide](DATASET_EXPORT.md)

## Troubleshooting

**Linux users:** If you encounter display issues, set the OpenGL platform:
```bash
export PYOPENGL_PLATFORM=egl
```

**Import errors:** Make sure you're running from the `engine` directory where all modules are located.

**OpenGL errors:** Update your graphics drivers to the latest version.

**More help:** See [QUICK_REFERENCE.md - Troubleshooting](QUICK_REFERENCE.md#troubleshooting) for detailed solutions.
