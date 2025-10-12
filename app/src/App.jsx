import { useCallback, useMemo, useRef, useState } from 'react'
import './App.css'
import SceneTabs from './components/SceneTabs'
import SceneTree from './components/SceneTree'
import ObjectLibrary from './components/ObjectLibrary'
import SceneWorkspace from './components/SceneWorkspace'
import { SHAPE_LIBRARY } from './data/shapeLibrary'
import { SCENE_TEMPLATES } from './data/sceneTemplates'
import {
  toggleNodeHidden,
  deleteNodeFromTree,
  setAllHidden,
  removeAllNodes,
  countTotalNodes,
  countVisibleNodes,
  countShapeInstances,
} from './utils/tree'

const getShapeDisplayName = (shapeId) => {
  const shape = SHAPE_LIBRARY.find((item) => item.id === shapeId)
  return shape?.label ?? shapeId
}

const App = () => {
  const sceneCounter = useRef(2)
  const nodeCounter = useRef(1)

  const [scenes, setScenes] = useState(() => [
    {
      id: 'scene-1',
      name: 'Scene 1',
      nodes: [],
    },
  ])
  const [activeSceneId, setActiveSceneId] = useState('scene-1')

  const createNodeId = useCallback((prefix = 'node') => {
    const id = `${prefix}-${nodeCounter.current}`
    nodeCounter.current += 1
    return id
  }, [])

  const activeScene = useMemo(() => scenes.find((scene) => scene.id === activeSceneId) ?? scenes[0], [
    scenes,
    activeSceneId,
  ])

  const addScene = useCallback(() => {
    const newScene = {
      id: `scene-${sceneCounter.current}`,
      name: `Scene ${sceneCounter.current}`,
      nodes: [],
    }
    sceneCounter.current += 1
    setScenes((prev) => [...prev, newScene])
    setActiveSceneId(newScene.id)
  }, [])

  const removeScene = useCallback((sceneId) => {
    setScenes((prev) => {
      if (prev.length === 1) {
        return prev
      }
      const nextScenes = prev.filter((scene) => scene.id !== sceneId)
      if (!nextScenes.find((scene) => scene.id === activeSceneId)) {
        setActiveSceneId(nextScenes[0]?.id ?? '')
      }
      return nextScenes
    })
  }, [activeSceneId])

  const updateSceneNodes = useCallback(
    (sceneId, updater) => {
      setScenes((prev) =>
        prev.map((scene) => {
          if (scene.id !== sceneId) {
            return scene
          }
          const nextNodes = updater(scene.nodes)
          if (nextNodes === scene.nodes) {
            return scene
          }
          return {
            ...scene,
            nodes: nextNodes,
          }
        }),
      )
    },
    [],
  )

  const handleAddShape = useCallback(
    (shapeId) => {
      if (!activeScene) return
      const label = getShapeDisplayName(shapeId)
      updateSceneNodes(activeScene.id, (nodes) => {
        const count = countShapeInstances(nodes, shapeId)
        const nodeName = `${label} ${count + 1}`
        const shapeNode = {
          id: createNodeId('shape'),
          name: nodeName,
          nodeKind: 'shape',
          shapeType: shapeId,
          hidden: false,
          meta: {
            label,
          },
          children: [],
        }
        return [...nodes, shapeNode]
      })
    },
    [activeScene, createNodeId, updateSceneNodes],
  )

  const handleAddGroup = useCallback(
    (groupId) => {
      if (!activeScene) return
      const template = SCENE_TEMPLATES.find((item) => item.id === groupId)
      if (!template) return
      const nodes = template.build((prefix) => createNodeId(prefix))
      updateSceneNodes(activeScene.id, (existing) => [...existing, ...nodes])
    },
    [activeScene, updateSceneNodes, createNodeId],
  )

  const handleToggleNode = useCallback(
    (nodeId) => {
      if (!activeScene) return
      updateSceneNodes(activeScene.id, (nodes) => toggleNodeHidden(nodes, nodeId))
    },
    [activeScene, updateSceneNodes],
  )

  const handleDeleteNode = useCallback(
    (nodeId) => {
      if (!activeScene) return
      updateSceneNodes(activeScene.id, (nodes) => deleteNodeFromTree(nodes, nodeId))
    },
    [activeScene, updateSceneNodes],
  )

  const handleHideAll = useCallback(() => {
    if (!activeScene) return
    updateSceneNodes(activeScene.id, (nodes) => setAllHidden(nodes, true))
  }, [activeScene, updateSceneNodes])

  const handleShowAll = useCallback(() => {
    if (!activeScene) return
    updateSceneNodes(activeScene.id, (nodes) => setAllHidden(nodes, false))
  }, [activeScene, updateSceneNodes])

  const handleDeleteAll = useCallback(() => {
    if (!activeScene) return
    updateSceneNodes(activeScene.id, () => removeAllNodes())
  }, [activeScene, updateSceneNodes])

  const totalNodes = useMemo(() => (activeScene ? countTotalNodes(activeScene.nodes) : 0), [activeScene])
  const visibleNodes = useMemo(() => (activeScene ? countVisibleNodes(activeScene.nodes) : 0), [activeScene])

  if (!activeScene) {
    return (
      <div className="app app--empty">
        <SceneTabs
          scenes={scenes}
          activeSceneId={activeSceneId}
          onSelectScene={setActiveSceneId}
          onAddScene={addScene}
          onCloseScene={removeScene}
        />
        <div className="app__empty-state">
          <p>No scenes yet. Add one to get started.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <SceneTabs
        scenes={scenes}
        activeSceneId={activeScene.id}
        onSelectScene={setActiveSceneId}
        onAddScene={addScene}
        onCloseScene={removeScene}
      />
      <div className="app__body">
        <SceneTree
          sceneName={activeScene.name}
          nodes={activeScene.nodes}
          totalCount={totalNodes}
          visibleCount={visibleNodes}
          onToggleVisibility={handleToggleNode}
          onDeleteNode={handleDeleteNode}
          onHideAll={handleHideAll}
          onShowAll={handleShowAll}
          onDeleteAll={handleDeleteAll}
        />
        <SceneWorkspace sceneName={activeScene.name} totalCount={totalNodes} visibleCount={visibleNodes} />
        <ObjectLibrary
          shapes={SHAPE_LIBRARY}
          groups={SCENE_TEMPLATES}
          onAddShape={handleAddShape}
          onAddGroup={handleAddGroup}
        />
      </div>
    </div>
  )
}

export default App
