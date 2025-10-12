const cloneNode = (node) => ({
  ...node,
  children: node.children?.map(cloneNode) ?? [],
})

const cascadeHidden = (items, hidden) =>
  items.map((child) => ({
    ...child,
    hidden,
    children: cascadeHidden(child.children ?? [], hidden),
  }))

export const toggleNodeHidden = (nodes, targetId) => {
  let mutated = false

  const visit = (items) =>
    items.map((node) => {
      if (node.id === targetId) {
        mutated = true
        const hidden = !node.hidden
        return {
          ...node,
          hidden,
          children: cascadeHidden(node.children ?? [], hidden),
        }
      }
      if (node.children && node.children.length) {
        const nextChildren = visit(node.children)
        if (nextChildren !== node.children) {
          mutated = true
          return {
            ...node,
            children: nextChildren,
          }
        }
      }
      return node
    })

  const result = visit(nodes)
  return mutated ? result : nodes
}

export const deleteNodeFromTree = (nodes, targetId) => {
  let mutated = false

  const filter = (items) => {
    const kept = []
    for (const node of items) {
      if (node.id === targetId) {
        mutated = true
        continue
      }
      let next = node
      if (node.children && node.children.length) {
        const updatedChildren = filter(node.children)
        if (updatedChildren !== node.children) {
          next = { ...node, children: updatedChildren }
          mutated = true
        }
      }
      kept.push(next)
    }
    return kept
  }

  const result = filter(nodes)
  return mutated ? result : nodes
}

export const setAllHidden = (nodes, hidden) =>
  nodes.map((node) => ({
    ...node,
    hidden,
    children: setAllHidden(node.children ?? [], hidden),
  }))

export const removeAllNodes = () => []

export const countVisibleNodes = (nodes) => {
  let count = 0
  const stack = [...nodes]
  while (stack.length) {
    const node = stack.pop()
    count += node.hidden ? 0 : 1
    if (node.children && node.children.length) {
      stack.push(...node.children)
    }
  }
  return count
}

export const countTotalNodes = (nodes) => {
  let count = 0
  const stack = [...nodes]
  while (stack.length) {
    const node = stack.pop()
    count += 1
    if (node.children && node.children.length) {
      stack.push(...node.children)
    }
  }
  return count
}

export const cloneTree = (nodes) => nodes.map(cloneNode)

export const countShapeInstances = (nodes, shapeType) => {
  let count = 0
  const stack = [...nodes]
  while (stack.length) {
    const node = stack.pop()
    if (node.shapeType === shapeType) {
      count += 1
    }
    if (node.children && node.children.length) {
      stack.push(...node.children)
    }
  }
  return count
}
