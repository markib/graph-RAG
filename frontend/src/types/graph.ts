export type GraphNode = {
  id: string
  group?: string
}

export type GraphLink = {
  source: string
  target: string
  label?: string
}

export type GraphData = {
  nodes: GraphNode[]
  links: GraphLink[]
}

export type ChatMessage = {
  role: 'user' | 'assistant'
  text: string
}
