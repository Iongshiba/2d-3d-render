# Documentation Index

Welcome to the 2D/3D Rendering Engine documentation! This index will guide you to the right documentation based on what you're looking for.

## 📚 Documentation Files

### 1. **README.md** - Start Here!
**Best for:** First-time setup, running the application, basic controls

**Contents:**
- Installation instructions
- Dependencies setup
- How to run the application
- Keyboard and mouse controls
- Feature overview
- Project directory structure

👉 **Read this first if you're new to the project**

---

### 2. **ARCHITECTURE.md** - Deep Dive
**Best for:** Understanding how the system works, design patterns, component relationships

**Contents:**
- Complete architecture overview with ASCII diagrams
- Scene Graph system explained in detail
- Rendering pipeline step-by-step walkthrough
- Class interaction diagrams
- Data flow from vertex to pixel
- Detailed explanation of each major component:
  - Node hierarchy (Node, TransformNode, GeometryNode, LightNode)
  - Shape and rendering system
  - Transform system
  - Camera and Trackball
  - Lighting system (Phong eye-space)
  - Shader pipeline
  - Template system

**Sections:**
1. Core Architecture
2. Scene Graph System
3. Rendering Pipeline
4. Class Interactions
5. Data Flow
6. Key Components (Camera, Transform, Lighting, Shaders, Templates)

👉 **Read this to understand the "why" and "how" of the architecture**

---

### 3. **DIAGRAMS.md** - Visual Learning
**Best for:** Visual learners, understanding relationships at a glance

**Contents:**
- Mermaid diagrams showing:
  - Scene graph structure and node hierarchy
  - Class diagrams with relationships
  - Rendering pipeline sequence diagrams
  - Data flow from vertex to pixel
  - Component relationships
  - Lighting system data flow
  - Matrix transformation chains
  - Animation system flow
  - Memory/resource management

**How to view:**
- GitHub (renders automatically)
- VS Code with Mermaid extension
- https://mermaid.live/
- Generate images with mermaid-cli

👉 **Read this alongside ARCHITECTURE.md for visual understanding**

---

### 4. **QUICK_REFERENCE.md** - Cheat Sheet
**Best for:** Day-to-day development, looking up syntax, troubleshooting

**Contents:**
- Quick start guide with code examples
- Scene graph cheat sheet
- Common patterns (static objects, rotation, orbiting, grouping)
- Shader uniforms reference table
- Transformation reference (Translate, Rotate, Scale, Composite)
- Animation function examples
- Camera & view control commands
- Shape creation guide
- Rendering pipeline summary
- Troubleshooting guide with solutions
- Performance tips
- Debugging helpers
- Command reference

👉 **Keep this open while coding for quick lookups**

---

## 🎯 Find What You Need

### "I want to..."

#### Get Started
- **Run the application** → `README.md`
- **Understand basic controls** → `README.md` → Controls section

#### Learn the System
- **Understand the architecture** → `ARCHITECTURE.md`
- **See visual diagrams** → `DIAGRAMS.md`
- **Learn scene graph concepts** → `ARCHITECTURE.md` → Scene Graph System

#### Build Something
- **Create a simple scene** → `QUICK_REFERENCE.md` → Quick Start
- **Add transformations** → `QUICK_REFERENCE.md` → Transformation Reference
- **Create animations** → `QUICK_REFERENCE.md` → Animation Functions
- **Add lighting** → `QUICK_REFERENCE.md` → Quick Start → Adding a Light

#### Understand Components
- **How does the scene graph work?** → `ARCHITECTURE.md` → Scene Graph System
- **How does rendering work?** → `ARCHITECTURE.md` → Rendering Pipeline
- **How do transformations propagate?** → `ARCHITECTURE.md` → Scene Graph System + `DIAGRAMS.md`
- **How does lighting work?** → `ARCHITECTURE.md` → Lighting System

#### Debug & Optimize
- **Troubleshoot issues** → `QUICK_REFERENCE.md` → Troubleshooting
- **Improve performance** → `QUICK_REFERENCE.md` → Performance Tips
- **Debug scene graph** → `QUICK_REFERENCE.md` → Debugging Helpers

#### Reference
- **Look up shader uniforms** → `QUICK_REFERENCE.md` → Shader Uniforms
- **Find transform syntax** → `QUICK_REFERENCE.md` → Transformation Reference
- **Common code patterns** → `QUICK_REFERENCE.md` → Common Patterns

---

## 📖 Reading Path by Goal

### Path 1: New User
1. `README.md` - Setup and run
2. Play with UI, explore templates
3. `QUICK_REFERENCE.md` - Quick Start section
4. Try modifying template code
5. `ARCHITECTURE.md` - Understand what you modified

### Path 2: Student/Learner
1. `README.md` - Setup
2. `ARCHITECTURE.md` - Read completely
3. `DIAGRAMS.md` - Study diagrams alongside architecture
4. `QUICK_REFERENCE.md` - Try examples
5. Explore `template/` code with new understanding

### Path 3: Developer/Contributor
1. `README.md` - Setup
2. `ARCHITECTURE.md` - Complete reading
3. `DIAGRAMS.md` - Understand component relationships
4. `QUICK_REFERENCE.md` - Bookmark for reference
5. Read source code in suggested order:
   - `graphics/scene.py` (Node classes)
   - `shape/base.py` (Shape base class)
   - `rendering/renderer.py` (Rendering orchestration)
   - `rendering/world.py` (Transform classes)
   - `app.py` (Application entry point)

### Path 4: Quick Lookup
- Go directly to `QUICK_REFERENCE.md`
- Use Ctrl+F to find what you need

---

## 🗂️ Documentation Structure

```
Documentation/
│
├── README.md ............................ Setup & run guide
├── ARCHITECTURE.md ...................... Detailed system design
├── DIAGRAMS.md .......................... Visual diagrams
├── QUICK_REFERENCE.md ................... Cheat sheet & reference
└── INDEX.md ............................. This file
```

---

## 💡 Key Concepts (Quick Summary)

### Scene Graph
A tree structure where:
- **Nodes** are containers
- **TransformNodes** apply spatial transformations
- **GeometryNodes** render shapes
- **LightNodes** provide lighting

Transformations propagate down the tree: `Final = Parent × Child`

### Rendering Pipeline
```
Input → Update → Collect → Apply → Draw → Present
```

Each frame:
1. Poll input
2. Update animations
3. Collect nodes from scene graph
4. Apply lighting and shading
5. Draw all geometry
6. Swap buffers

### Transformation Chain
```
Local Space → World Space → Eye Space → Clip Space → Screen Space
     ↓              ↓             ↓           ↓            ↓
   Vertex      Model (M)     View (V)    Proj (P)     Viewport
```

### Phong Lighting (Eye-Space)
All calculations in eye-space (camera at origin):
- Light position transformed: `view × model × light_pos`
- Fragment receives eye-space coordinates
- Compute diffuse + specular in fragment shader
- Combine with material properties

---

## 🔗 External Resources

### OpenGL Learning
- [LearnOpenGL.com](https://learnopengl.com/) - Excellent OpenGL tutorial
- [OpenGL Documentation](https://www.opengl.org/documentation/)

### Graphics Fundamentals
- [Scratchapixel](https://www.scratchapixel.com/) - Computer graphics from scratch
- [Real-Time Rendering Resources](http://www.realtimerendering.com/)

### Python Graphics
- [PyOpenGL Documentation](http://pyopengl.sourceforge.net/)
- [GLFW Documentation](https://www.glfw.org/documentation.html)

---

## 📝 Documentation Conventions

Throughout the documentation:

**Code Blocks:**
```python
# Python code examples
```

```glsl
// GLSL shader code
```

```powershell
# PowerShell commands
```

**Symbols:**
- ✅ Recommended / Solution
- ❌ Not recommended / Problem
- 👉 Important note
- 🔵 Container nodes
- 🔴 Transform nodes
- 🟢 Geometry nodes
- 🟡 Light nodes

**File Paths:**
- Relative to project root
- Use forward slashes: `graphics/scene.py`
- Full paths in code use backslashes on Windows

**Diagrams:**
- ASCII art in `ARCHITECTURE.md`
- Mermaid syntax in `DIAGRAMS.md`
- Class names in `PascalCase`
- Method names in `snake_case`

---

## 🤝 Contributing to Documentation

If you find errors or want to improve the documentation:

1. **Typos/Errors:**
   - Fix directly in the relevant `.md` file
   - Keep formatting consistent

2. **New Examples:**
   - Add to `QUICK_REFERENCE.md` → Common Patterns
   - Include complete, runnable code

3. **Architecture Changes:**
   - Update `ARCHITECTURE.md` with detailed explanation
   - Update `DIAGRAMS.md` with new diagrams
   - Update `QUICK_REFERENCE.md` if syntax changed

4. **New Features:**
   - Document in all relevant files
   - Add examples to `QUICK_REFERENCE.md`
   - Update diagrams if architecture changed

---

## 📧 Questions?

If the documentation doesn't answer your question:

1. Check all four documentation files
2. Look at code examples in `template/` directory
3. Read the source code (it's well-structured!)
4. Search for similar patterns in existing code

**Documentation Version:** 1.0  
**Last Updated:** December 2025  
**Project:** 2D/3D Rendering Engine  

---

Happy coding! 🚀
