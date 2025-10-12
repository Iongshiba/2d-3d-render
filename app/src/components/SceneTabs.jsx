const SceneTabs = ({ scenes, activeSceneId, onSelectScene, onAddScene, onCloseScene }) => {
  return (
    <div className="scene-tabs">
      <div className="scene-tabs__list">
        {scenes.map((scene) => {
          const isActive = scene.id === activeSceneId
          return (
            <button
              key={scene.id}
              type="button"
              className={`scene-tabs__tab ${isActive ? 'is-active' : ''}`}
              onClick={() => onSelectScene(scene.id)}
            >
              <span className="scene-tabs__tab-label">{scene.name}</span>
              {scenes.length > 1 && (
                <span
                  role="button"
                  tabIndex={0}
                  className="scene-tabs__close"
                  onClick={(event) => {
                    event.stopPropagation()
                    onCloseScene(scene.id)
                  }}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault()
                      event.stopPropagation()
                      onCloseScene(scene.id)
                    }
                  }}
                >
                  ×
                </span>
              )}
            </button>
          )
        })}
      </div>
      <button type="button" className="scene-tabs__add" onClick={onAddScene}>
        +
      </button>
    </div>
  )
}

export default SceneTabs
