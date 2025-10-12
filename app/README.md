# Scene Composer UI

The web client now provides a scene-composition workspace for the OpenGL engine.

## Features

- **Scene tabs** – Switch between multiple scenes, add new tabs, or close existing ones (similar to a browser).
- **Object library** – Add any primitive from `engine/shape` or drop in predefined templates based on `engine/scenes`, such as the atom or solar system.
- **Scene graph tree** – Inspect the hierarchy, hide/show nodes, or delete them individually. Bulk actions let you hide/show/delete everything in the active scene.
- **Workspace panel** – Placeholder canvas area ready for future hookup to the Python renderer.

## Running locally

```
npm install
npm run dev
```

> **Note:** The UI relies on Vite. If `npm install` fails due to network restrictions, retry or install from a network that can reach `https://registry.npmjs.org`.

To produce a production build:

```
npm run build
```

The React application lives under `app/src`. Key entry points:

- `App.jsx` – top-level layout and state management
- `components/SceneTree.jsx` – hierarchical graph view and controls
- `components/ObjectLibrary.jsx` – shape/template palette
- `data/sceneTemplates.js` – predefined assemblies mirroring Python scene builders
