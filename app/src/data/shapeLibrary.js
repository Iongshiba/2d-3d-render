export const SHAPE_LIBRARY = [
  {
    id: 'TRIANGLE',
    label: 'Triangle',
    category: '2D primitives',
    description: 'Single face triangle polygon.',
  },
  {
    id: 'RECTANGLE',
    label: 'Rectangle',
    category: '2D primitives',
    description: 'Axis-aligned quad made from two triangles.',
  },
  {
    id: 'PENTAGON',
    label: 'Pentagon',
    category: '2D primitives',
    description: 'Regular five-sided polygon.',
  },
  {
    id: 'HEXAGON',
    label: 'Hexagon',
    category: '2D primitives',
    description: 'Regular six-sided polygon.',
  },
  {
    id: 'CIRCLE',
    label: 'Circle',
    category: '2D primitives',
    description: '2D circle approximated with configurable sectors.',
  },
  {
    id: 'ELLIPSE',
    label: 'Ellipse',
    category: '2D primitives',
    description: 'Ellipse mesh built from configurable axes.',
  },
  {
    id: 'TRAPEZOID',
    label: 'Trapezoid',
    category: '2D primitives',
    description: 'Trapezoid polygon with parallel bases.',
  },
  {
    id: 'STAR',
    label: 'Star',
    category: '2D primitives',
    description: 'Star with adjustable wing count and radii.',
  },
  {
    id: 'ARROW',
    label: 'Arrow',
    category: '2D primitives',
    description: 'Arrow shape composed of quad and triangle.',
  },
  {
    id: 'RING',
    label: 'Ring',
    category: '2D primitives',
    description: '2D ring useful for orbit gizmos.',
  },
  {
    id: 'TETRAHEDRON',
    label: 'Tetrahedron',
    category: '3D polyhedra',
    description: 'Four-face pyramid solid.',
  },
  {
    id: 'CUBE',
    label: 'Cube',
    category: '3D polyhedra',
    description: 'Axis-aligned six-face cube.',
  },
  {
    id: 'CYLINDER',
    label: 'Cylinder',
    category: '3D polyhedra',
    description: 'Cylinder mesh with radial segments.',
  },
  {
    id: 'CONE',
    label: 'Cone',
    category: '3D polyhedra',
    description: 'Cone mesh with configurable radius and height.',
  },
  {
    id: 'TRUNCATED_CONE',
    label: 'Truncated Cone',
    category: '3D polyhedra',
    description: 'Frustum with top/bottom radii.',
  },
  {
    id: 'SPHERE',
    label: 'Sphere',
    category: '3D polyhedra',
    description: 'UV sphere using sectors and stacks.',
  },
  {
    id: 'TORUS',
    label: 'Torus',
    category: '3D polyhedra',
    description: 'Doughnut torus generated from two radii.',
  },
  {
    id: 'EQUATION',
    label: 'Equation Surface',
    category: 'Procedural',
    description: 'Implicit surface generated from an equation.',
  },
  {
    id: 'MODEL',
    label: 'OBJ Model',
    category: 'Procedural',
    description: 'Mesh loaded from external model file.',
  },
  {
    id: 'LIGHT_SOURCE',
    label: 'Light Source',
    category: 'Lighting',
    description: 'Helper geometry for point light gizmo.',
  },
]

export const shapeLabelMap = SHAPE_LIBRARY.reduce((acc, shape) => {
  acc[shape.id] = shape.label
  return acc
}, {})
