import { useMemo, useState } from 'react'

const groupByCategory = (shapes) =>
  shapes.reduce((acc, shape) => {
    if (!acc[shape.category]) {
      acc[shape.category] = []
    }
    acc[shape.category].push(shape)
    return acc
  }, {})

const ObjectLibrary = ({ shapes, groups, onAddShape, onAddGroup }) => {
  const [query, setQuery] = useState('')
  const filteredShapes = useMemo(() => {
    if (!query) return shapes
    const term = query.toLowerCase()
    return shapes.filter(
      (shape) =>
        shape.label.toLowerCase().includes(term) ||
        shape.description.toLowerCase().includes(term) ||
        shape.id.toLowerCase().includes(term),
    )
  }, [query, shapes])

  const categoryMap = useMemo(() => groupByCategory(filteredShapes), [filteredShapes])

  return (
    <section className="object-library">
      <header className="object-library__header">
        <div>
          <h2>Object library</h2>
          <p>Add individual shapes or drop in ready-made templates.</p>
        </div>
        <input
          type="search"
          placeholder="Search shapes"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          className="object-library__search"
        />
      </header>
      <div className="object-library__content">
        <div className="object-library__section">
          <h3>Shapes</h3>
          {filteredShapes.length === 0 ? (
            <p className="object-library__empty">No matching shapes.</p>
          ) : (
            Object.entries(categoryMap).map(([category, items]) => (
              <div key={category} className="object-library__category">
                <h4>{category}</h4>
                <div className="object-library__grid">
                  {items.map((shape) => (
                    <button
                      key={shape.id}
                      type="button"
                      className="object-library__item"
                      onClick={() => onAddShape(shape.id)}
                    >
                      <span className="object-library__item-title">{shape.label}</span>
                      <span className="object-library__item-sub">{shape.id}</span>
                      <p>{shape.description}</p>
                    </button>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
        <div className="object-library__section">
          <h3>Templates</h3>
          {groups.length === 0 ? (
            <p className="object-library__empty">No templates registered.</p>
          ) : (
            <div className="object-library__grid">
              {groups.map((group) => (
                <button
                  key={group.id}
                  type="button"
                  className="object-library__item"
                  onClick={() => onAddGroup(group.id)}
                >
                  <span className="object-library__item-title">{group.label}</span>
                  <span className="object-library__item-sub">{group.id}</span>
                  <p>{group.description}</p>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}

export default ObjectLibrary
