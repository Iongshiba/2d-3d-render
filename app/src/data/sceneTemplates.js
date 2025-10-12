import { shapeLabelMap } from './shapeLibrary'

const protonColor = '#cc334d'
const neutronColor = '#2eaf56'
const electronColor = '#3549d3'
const ringColor = '#cccccc'
const starColor = '#ffda7c'
const planetColor = '#3f6ad8'
const moonColor = '#e7e7e7'

const makeShapeNode = (createId, name, shapeType, meta = {}) => ({
  id: createId('shape'),
  name,
  nodeKind: 'shape',
  shapeType,
  hidden: false,
  children: [],
  meta: {
    label: shapeLabelMap[shapeType] ?? shapeType,
    ...meta,
  },
})

const makeGroupNode = (createId, name, nodeKind = 'group', children = [], meta = {}) => ({
  id: createId(nodeKind),
  name,
  nodeKind,
  hidden: false,
  meta,
  children,
})

const buildAtomTemplate = (createId) => {
  const nucleusChildren = Array.from({ length: 12 }, (_, idx) =>
    makeShapeNode(createId, `Particle ${idx + 1}`, 'SPHERE', {
      color: idx % 2 === 0 ? protonColor : neutronColor,
    }),
  )

  const nucleus = makeGroupNode(createId, 'Nucleus', 'transform', nucleusChildren, {
    transform: 'Translate',
  })

  const rings = [5, 10, 15].map((radius, index) => {
    const ring = makeShapeNode(createId, `Orbit Ring ${index + 1}`, 'RING', {
      color: ringColor,
      radius,
    })
    const electron = makeShapeNode(createId, `Electron ${index + 1}`, 'SPHERE', {
      color: electronColor,
      orbitRadius: radius,
      orbitSpeed: (1 + index * 0.2).toFixed(2),
    })
    return makeGroupNode(
      createId,
      `Orbit ${index + 1}`,
      'transform',
      [
        makeGroupNode(createId, `Ring ${index + 1}`, 'geometry', [ring], {
          transform: 'Rotate 90°',
        }),
        makeGroupNode(createId, `Electron ${index + 1} Orbit`, 'transform', [electron], {
          transform: 'Translate + Orbit',
        }),
      ],
      {
        orbitRadius: radius,
      },
    )
  })

  const light = makeShapeNode(createId, 'Light Gizmo', 'LIGHT_SOURCE', {
    color: '#ffffff',
  })

  const lightWrapper = makeGroupNode(createId, 'Light', 'transform', [light], {
    transform: 'Translate (15, 15, 15)',
  })

  return [
    makeGroupNode(createId, 'Atom System', 'scene-group', [nucleus, ...rings, lightWrapper]),
  ]
}

const buildSolarTemplate = (createId) => {
  const star = makeShapeNode(createId, 'Star', 'SPHERE', {
    color: starColor,
    radius: 2.5,
  })

  const starRoot = makeGroupNode(createId, 'Star Root', 'transform', [
    makeGroupNode(createId, 'Star Spin', 'transform', [
      makeGroupNode(createId, 'Star Pulse', 'transform', [
        makeGroupNode(createId, 'Star Geometry', 'geometry', [star], {
          transform: 'Pulse Scale',
        }),
      ], {
        transform: 'Pulse Scale',
      }),
    ], {
      transform: 'Infinite Spin',
    }),
  ])

  const makePlanetSystem = (index, orbitRadius, orbitSpeed) => {
    const planet = makeShapeNode(createId, `Planet ${index}`, 'SPHERE', {
      color: planetColor,
      radius: 1,
      orbitRadius,
    })

    const moon = makeShapeNode(createId, `Moon ${index}`, 'SPHERE', {
      color: moonColor,
      radius: 0.3,
      orbitRadius: 2.5,
    })

    const moonOrbit = makeGroupNode(createId, `Moon ${index} Orbit`, 'transform', [
      makeGroupNode(createId, `Moon ${index} Geometry`, 'geometry', [moon], {
        transform: 'Translate + Orbit',
      }),
    ], {
      transform: `Circular orbit speed ${orbitSpeed * 2}`,
    })

    const planetSpin = makeGroupNode(createId, `Planet ${index} Spin`, 'transform', [
      makeGroupNode(createId, `Planet ${index} Geometry`, 'geometry', [planet]),
    ], {
      transform: 'Infinite spin',
    })

    return makeGroupNode(createId, `Planet ${index} System`, 'transform', [
      makeGroupNode(createId, `Planet ${index} Orbit`, 'transform', [planetSpin, moonOrbit], {
        transform: `Orbit radius ${orbitRadius}`,
      }),
    ])
  }

  const planets = [
    makePlanetSystem(1, 7.5, 0.4),
    makePlanetSystem(2, 12, 0.25),
  ]

  const light = makeShapeNode(createId, 'Light Gizmo', 'LIGHT_SOURCE', {
    color: '#ffffff',
  })
  const lightNode = makeGroupNode(createId, 'Scene Light', 'transform', [light], {
    transform: 'Translate (0, 10, 0)',
  })

  return [makeGroupNode(createId, 'Solar System', 'scene-group', [starRoot, ...planets, lightNode])]
}

export const SCENE_TEMPLATES = [
  {
    id: 'atom',
    label: 'Atom System',
    description: 'Multi-orbit atom scene inspired by engine/scenes/atom_scene.py',
    build: buildAtomTemplate,
  },
  {
    id: 'solar',
    label: 'Solar Playground',
    description: 'Star with orbiting planets, based on engine/scenes/shape_scene.py',
    build: buildSolarTemplate,
  },
]
