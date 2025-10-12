const SceneWorkspace = ({ sceneName, totalCount, visibleCount }) => {
  return (
    <section className="scene-workspace">
      <header className="scene-workspace__header">
        <h2>{sceneName} workspace</h2>
        <p>
          {visibleCount}/{totalCount} nodes visible • Configure the scene graph using the controls on the
          left and right.
        </p>
      </header>
      <div className="scene-workspace__canvas" role="presentation">
        <div className="scene-workspace__placeholder">
          <p>3D viewport placeholder</p>
          <p>Connect the Python engine to render this scene.</p>
        </div>
      </div>
      <div className="scene-workspace__footer">
        <p>
          Tip: export the graph to JSON or sync with the engine once backend integration is ready. For now, this UI
          lets you plan and organize the scene structure.
        </p>
      </div>
    </section>
  )
}

export default SceneWorkspace
