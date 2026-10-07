import { describe, it, expect } from 'vitest'
import {
  buildFolderTree,
  matchFlowFolder,
  flattenVisibleTree,
  type FolderTreeNode,
} from '../src/utils/folderTree'

describe('Folder Tree Utility (Worktree Hierarchy)', () => {
  it('returns empty tree when flow array is empty', () => {
    const tree = buildFolderTree([])
    expect(tree).toEqual([])
  })

  it('defaults empty, whitespace, or undefined folders to "Geral"', () => {
    const flows = [
      { id: '1', folder: '' },
      { id: '2', folder: undefined },
      { id: '3', folder: '   ' },
      { id: '4', folder: 'Geral' },
    ]
    const tree = buildFolderTree(flows)
    expect(tree.length).toBe(1)
    expect(tree[0].name).toBe('Geral')
    expect(tree[0].fullPath).toBe('Geral')
    expect(tree[0].flowCount).toBe(4)
    expect(tree[0].directCount).toBe(4)
    expect(tree[0].children).toHaveLength(0)
  })

  it('builds flat root folders with correct direct counts', () => {
    const flows = [
      { id: '1', folder: 'Vendas' },
      { id: '2', folder: 'Financeiro' },
      { id: '3', folder: 'Vendas' },
    ]
    const tree = buildFolderTree(flows)
    expect(tree.map(n => n.name)).toEqual(['Financeiro', 'Vendas'])
    expect(tree[0].flowCount).toBe(1)
    expect(tree[1].flowCount).toBe(2)
  })

  it('builds multi-level nested hierarchies from slash-separated paths', () => {
    const flows = [
      { id: '1', folder: 'Financeiro/Cobrança' },
      { id: '2', folder: 'Financeiro/Fiscal' },
      { id: '3', folder: 'Financeiro/Fiscal/Notas' },
      { id: '4', folder: 'Financeiro' },
      { id: '5', folder: 'RH/Admissão' },
    ]

    const tree = buildFolderTree(flows)
    expect(tree.map(n => n.name)).toEqual(['Financeiro', 'RH'])

    const finNode = tree[0]
    expect(finNode.name).toBe('Financeiro')
    expect(finNode.fullPath).toBe('Financeiro')
    expect(finNode.flowCount).toBe(4) // 1 direct + 1 cobrança + 1 fiscal + 1 notas
    expect(finNode.directCount).toBe(1)
    expect(finNode.children.map(c => c.name)).toEqual(['Cobrança', 'Fiscal'])

    const cobrancaNode = finNode.children[0]
    expect(cobrancaNode.name).toBe('Cobrança')
    expect(cobrancaNode.fullPath).toBe('Financeiro/Cobrança')
    expect(cobrancaNode.flowCount).toBe(1)
    expect(cobrancaNode.children).toHaveLength(0)

    const fiscalNode = finNode.children[1]
    expect(fiscalNode.name).toBe('Fiscal')
    expect(fiscalNode.fullPath).toBe('Financeiro/Fiscal')
    expect(fiscalNode.flowCount).toBe(2)
    expect(fiscalNode.directCount).toBe(1)
    expect(fiscalNode.children).toHaveLength(1)

    const notasNode = fiscalNode.children[0]
    expect(notasNode.name).toBe('Notas')
    expect(notasNode.fullPath).toBe('Financeiro/Fiscal/Notas')
    expect(notasNode.flowCount).toBe(1)
  })

  it('cleans leading, trailing, and duplicate slashes cleanly', () => {
    const flows = [
      { id: '1', folder: '/TI///Infraestrutura/' },
      { id: '2', folder: 'TI/Infraestrutura' },
    ]
    const tree = buildFolderTree(flows)
    expect(tree.length).toBe(1)
    expect(tree[0].name).toBe('TI')
    expect(tree[0].children[0].name).toBe('Infraestrutura')
    expect(tree[0].children[0].fullPath).toBe('TI/Infraestrutura')
    expect(tree[0].flowCount).toBe(2)
  })

  describe('matchFlowFolder', () => {
    it('matches all flows when selectedPath is "all"', () => {
      expect(matchFlowFolder('Financeiro/Cobrança', 'all')).toBe(true)
      expect(matchFlowFolder('', 'all')).toBe(true)
      expect(matchFlowFolder(undefined, 'all')).toBe(true)
    })

    it('matches exact folder and nested child paths', () => {
      expect(matchFlowFolder('Financeiro', 'Financeiro')).toBe(true)
      expect(matchFlowFolder('Financeiro/Cobrança', 'Financeiro')).toBe(true)
      expect(matchFlowFolder('Financeiro/Fiscal/Notas', 'Financeiro')).toBe(true)
      expect(matchFlowFolder('Financeiro/Fiscal/Notas', 'Financeiro/Fiscal')).toBe(true)
      expect(matchFlowFolder('Financeiro/Cobrança', 'Financeiro/Fiscal')).toBe(false)
      expect(matchFlowFolder('RH', 'Financeiro')).toBe(false)
    })

    it('matches empty/undefined flow folder when "Geral" is selected', () => {
      expect(matchFlowFolder('', 'Geral')).toBe(true)
      expect(matchFlowFolder(undefined, 'Geral')).toBe(true)
      expect(matchFlowFolder('Geral', 'Geral')).toBe(true)
      expect(matchFlowFolder('Financeiro', 'Geral')).toBe(false)
    })
  })

  describe('flattenVisibleTree', () => {
    const flows = [
      { id: '1', folder: 'Financeiro/Cobrança' },
      { id: '2', folder: 'Financeiro/Fiscal/Notas' },
      { id: '3', folder: 'RH' },
    ]
    const tree = buildFolderTree(flows)

    it('shows only root nodes when expanded set is empty', () => {
      const visible = flattenVisibleTree(tree, new Set())
      expect(visible.map(v => v.name)).toEqual(['Financeiro', 'RH'])
      expect(visible[0].hasChildren).toBe(true)
      expect(visible[0].isExpanded).toBe(false)
      expect(visible[1].hasChildren).toBe(false)
    })

    it('reveals children when parent is in expanded set', () => {
      const expanded = new Set(['Financeiro'])
      const visible = flattenVisibleTree(tree, expanded)
      expect(visible.map(v => v.name)).toEqual(['Financeiro', 'Cobrança', 'Fiscal', 'RH'])
      expect(visible.find(v => v.name === 'Cobrança')?.depth).toBe(1)
      expect(visible.find(v => v.name === 'Fiscal')?.hasChildren).toBe(true)
      expect(visible.find(v => v.name === 'Fiscal')?.isExpanded).toBe(false)
    })

    it('filters nodes and auto-expands matching paths when searchQuery is provided', () => {
      const visible = flattenVisibleTree(tree, new Set(), 'Notas')
      expect(visible.map(v => v.name)).toEqual(['Financeiro', 'Fiscal', 'Notas'])
      expect(visible[0].isExpanded).toBe(true)
      expect(visible[1].isExpanded).toBe(true)
      expect(visible[2].name).toBe('Notas')
      expect(visible.find(v => v.name === 'RH')).toBeUndefined()
    })
  })
})
