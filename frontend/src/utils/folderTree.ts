export interface FolderTreeNode {
  id: string
  name: string
  fullPath: string
  depth: number
  children: FolderTreeNode[]
  flowCount: number
  directCount: number
}

/**
 * Sanitizes a folder path by removing leading/trailing slashes,
 * collapsing multiple consecutive slashes, and defaulting empty values to 'Geral'.
 */
export function sanitizeFolderPath(rawPath?: string | null): string {
  if (!rawPath) return 'Geral'
  const trimmed = rawPath.trim()
  if (!trimmed) return 'Geral'
  const cleaned = trimmed
    .split('/')
    .map(s => s.trim())
    .filter(Boolean)
    .join('/')
  return cleaned || 'Geral'
}

/**
 * Builds a hierarchical folder tree structure from a collection of flows.
 */
export function buildFolderTree(flows: Array<{ folder?: string }>): FolderTreeNode[] {
  if (!flows || flows.length === 0) return []

  const directCounts = new Map<string, number>()

  flows.forEach(flow => {
    const clean = sanitizeFolderPath(flow.folder)
    directCounts.set(clean, (directCounts.get(clean) || 0) + 1)
  })

  // Collect all unique paths and their intermediate parent paths
  const allPaths = new Set<string>()
  for (const path of directCounts.keys()) {
    const segments = path.split('/')
    let cumulative = ''
    for (let i = 0; i < segments.length; i++) {
      cumulative = cumulative ? `${cumulative}/${segments[i]}` : segments[i]
      allPaths.add(cumulative)
    }
  }

  // Recursive builder function
  function buildLevel(parentPath: string, depth: number): FolderTreeNode[] {
    const childPaths: string[] = []
    const prefix = parentPath ? `${parentPath}/` : ''

    for (const path of allPaths) {
      if (prefix ? path.startsWith(prefix) : !path.includes('/')) {
        const remaining = prefix ? path.slice(prefix.length) : path
        // Only immediate children (no further '/' in remaining)
        if (!remaining.includes('/') && remaining.length > 0) {
          childPaths.push(path)
        }
      }
    }

    childPaths.sort((a, b) => {
      const nameA = a.split('/').pop() || ''
      const nameB = b.split('/').pop() || ''
      return nameA.localeCompare(nameB, 'pt-BR', { sensitivity: 'base' })
    })

    return childPaths.map(fullPath => {
      const name = fullPath.split('/').pop() || fullPath
      const children = buildLevel(fullPath, depth + 1)
      const direct = directCounts.get(fullPath) || 0
      const flowCount = direct + children.reduce((sum, c) => sum + c.flowCount, 0)

      return {
        id: fullPath,
        name,
        fullPath,
        depth,
        children,
        flowCount,
        directCount: direct,
      }
    })
  }

  return buildLevel('', 0)
}

/**
 * Checks whether a flow's folder matches the active selected folder path in the worktree.
 * - 'all' matches everything.
 * - Matches exact folder or any recursive child path.
 */
export function matchFlowFolder(
  flowFolder: string | undefined | null,
  selectedPath: string
): boolean {
  if (selectedPath === 'all') return true
  const cleanFlow = sanitizeFolderPath(flowFolder)
  const cleanSelected = sanitizeFolderPath(selectedPath)

  if (cleanFlow === cleanSelected) return true
  if (cleanFlow.startsWith(`${cleanSelected}/`)) return true
  return false
}

export interface FlatTreeItem {
  id: string
  name: string
  fullPath: string
  depth: number
  hasChildren: boolean
  isExpanded: boolean
  flowCount: number
  directCount: number
}

/**
 * Flattens a recursive FolderTreeNode array into a linear list of visible items
 * based on expanded state and optional search query filter.
 */
export function flattenVisibleTree(
  tree: FolderTreeNode[],
  expandedFolders: Set<string>,
  searchQuery: string = ''
): FlatTreeItem[] {
  const query = searchQuery.trim().toLowerCase()
  const result: FlatTreeItem[] = []

  function doesNodeMatchQuery(node: FolderTreeNode, q: string): boolean {
    if (node.name.toLowerCase().includes(q) || node.fullPath.toLowerCase().includes(q)) {
      return true
    }
    return node.children.some(child => doesNodeMatchQuery(child, q))
  }

  function walk(nodes: FolderTreeNode[]) {
    for (const node of nodes) {
      const hasChildren = node.children.length > 0
      const matchesQuery = !query || node.fullPath.toLowerCase().includes(query) || node.name.toLowerCase().includes(query)
      const hasMatchingDescendant = query ? doesNodeMatchQuery(node, query) : false

      if (query && !matchesQuery && !hasMatchingDescendant) {
        continue
      }

      const isExpanded = query ? true : expandedFolders.has(node.fullPath)

      result.push({
        id: node.id,
        name: node.name,
        fullPath: node.fullPath,
        depth: node.depth,
        hasChildren,
        isExpanded,
        flowCount: node.flowCount,
        directCount: node.directCount,
      })

      if (hasChildren && isExpanded) {
        walk(node.children)
      }
    }
  }

  walk(tree)
  return result
}
