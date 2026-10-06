export interface InputDefinition {
  name: string
  type: string
  label: string
  required?: boolean
  default?: any
  placeholder?: string
  is_handle?: boolean
  description?: string
  options?: string[]
  language?: string
}

export interface OutputDefinition {
  name: string
  label: string
  type: string
  method: string
  description?: string
}

export interface ComponentDefinition {
  name: string
  displayName: string
  category: string
  description: string
  icon: string
  inputs: InputDefinition[]
  outputs: OutputDefinition[]
}

export interface FlowPosition {
  x: number
  y: number
}

export interface NodeData {
  inputs: Record<string, any>
  label?: string
}

export interface FlowNode {
  id: string
  type: string
  position: FlowPosition
  data: NodeData
}

export interface FlowEdge {
  id: string
  source: string
  sourceHandle?: string
  target: string
  targetHandle?: string
}

export interface FlowModel {
  id: string
  name: string
  description?: string
  nodes: FlowNode[]
  edges: FlowEdge[]
}

export type ExecutionStatus = 'idle' | 'running' | 'completed' | 'failed'

export interface NodeExecutionState {
  status: ExecutionStatus
  output?: any
  error?: string
  durationMs?: number
}

export interface FlowLogEntry {
  id: string
  timestamp: string
  nodeId?: string
  nodeName?: string
  level: 'info' | 'success' | 'error' | 'warn'
  message: string
  durationMs?: number
  output?: any
}

export interface ExecutionEvent {
  event: string
  flow_id?: string
  node_id?: string
  type?: string
  output?: any
  error?: string
  status?: string
  summary?: any
}

export interface FlowTemplate {
  id: string
  name: string
  description: string
  flow: FlowModel
}
