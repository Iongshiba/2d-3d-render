import { shapeLabelMap } from '../data/shapeLibrary'

const NODE_KIND_LABEL = {
  'scene-group': 'Scene Group',
  transform: 'Transform',
  geometry: 'Geometry',
  group: 'Group',
  shape: 'Shape',
}

const NODE_KIND_SYMBOL = {
  'scene-group': '◇',
  transform: '⤾',
  geometry: '⬚',
  group: '⬢',
  shape: '⬤',
}

const TreeNode = ({ node, depth, onToggleVisibility, onDeleteNode }) => {
  const label = NODE_KIND_LABEL[node.nodeKind] ?? 'Node'
  const symbol = NODE_KIND_SYMBOL[node.nodeKind] ?? '●'
  const indent = depth * 16
  const shapeLabel = node.meta?.label ?? shapeLabelMap[node.shapeType]
  const extra = []
  if (node.shapeType) {
    extra.push(shapeLabel ?? node.shapeType)
  }
  if (node.meta?.transform) {
    extra.push(node.meta.transform)
  }

  return (
    <div className={`scene-tree__node ${node.hidden ? 'is-hidden' : ''}`}>
      <div className="scene-tree__node-row" style={{ paddingLeft: `${indent}px` }}>
        <div className="scene-tree__node-main">
          <span className="scene-tree__symbol" title={label} aria-hidden="true">
            {symbol}
          </span>
          <div className="scene-tree__text">
            <span className="scene-tree__name">{node.name}</span>
            {extra.length > 0 && <span className="scene-tree__meta">{extra.join(' • ')}</span>}
          </div>
        </div>
        <div className="scene-tree__actions">
          <button type="button" onClick={() => onToggleVisibility(node.id)} className="scene-tree__action-btn">
            {node.hidden ? 'Show' : 'Hide'}
          </button>
          <button type="button" onClick={() => onDeleteNode(node.id)} className="scene-tree__action-btn danger">
            Delete
          </button>
        </div>
      </div>
      {node.children && node.children.length > 0 && (
        <div className="scene-tree__children">
          {node.children.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              depth={depth + 1}
              onToggleVisibility={onToggleVisibility}
              onDeleteNode={onDeleteNode}
            />
          ))}
        </div>
      )}
    </div>
  )
}

const SceneTree = ({
  sceneName,
  nodes,
  totalCount,
  visibleCount,
  onToggleVisibility,
  onDeleteNode,
  onHideAll,
  onShowAll,
  onDeleteAll,
}) => {
  return (
    <section className="scene-tree">
      <header className="scene-tree__header">
        <div>
          <h2>{sceneName} graph</h2>
          <p>{visibleCount} of {totalCount} nodes visible</p>
        </div>
        <div className="scene-tree__header-actions">
          <button type="button" onClick={onHideAll} className="scene-tree__action-btn">
            Hide all
          </button>
          <button type="button" onClick={onShowAll} className="scene-tree__action-btn">
            Show all
          </button>
          <button type="button" onClick={onDeleteAll} className="scene-tree__action-btn danger">
            Delete all
          </button>
        </div>
      </header>
      <div className="scene-tree__body">
        {nodes.length === 0 ? (
          <p className="scene-tree__empty">No shapes yet. Use the library to add one.</p>
        ) : (
          nodes.map((node) => (
            <TreeNode
              key={node.id}
              node={node}
              depth={0}
              onToggleVisibility={onToggleVisibility}
              onDeleteNode={onDeleteNode}
            />
          ))
        )}
      </div>
    </section>
  )
}

export default SceneTree
