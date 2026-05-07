import { useEffect, useState } from 'react'
import ChatInput from '../components/chat/ChatInput'
import ChatWindow from '../components/chat/ChatWindow'
import GraphPanel from '../components/graph/GraphPanel'
import Sidebar from '../components/layout/Sidebar'
import Layout from '../components/layout/Layout'
import { askQuestion, fetchGraph } from '../api/client'
import type { ChatMessage, GraphData } from '../types/graph'

const initialGraph: GraphData = {
  nodes: [],
  links: [],
}

export default function Dashboard() {
  const [graph, setGraph] = useState<GraphData>(initialGraph)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [answer, setAnswer] = useState('')
  const [cypher, setCypher] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadGraph()
  }, [])

  const loadGraph = async () => {
    try {
      const graphData = await fetchGraph()
      setGraph(graphData)
    } catch (err) {
      console.error(err)
      setError('Unable to load graph data. Check that the backend is running.')
    }
  }

  const handleAsk = async (query: string) => {
    const userMessage: ChatMessage = { role: 'user', text: query }
    setMessages((prev) => [...prev, userMessage])
    setLoading(true)
    setError('')

    try {
      const response = await askQuestion(query)
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        text: response.answer,
      }
      setMessages((prev) => [...prev, assistantMessage])
      setAnswer(response.answer)
      setCypher(response.cypher)
      setGraph(response.graph)
    } catch (err) {
      console.error(err)
      setError('Query failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout>
      <div className="grid gap-6 xl:grid-cols-[320px_1fr]">
        <div className="space-y-6">
          <aside className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h1 className="text-3xl font-semibold text-slate-900">Graph RAG Dashboard</h1>
            <p className="mt-2 max-w-xl text-sm text-slate-600">
              Ask the graph a question, review the generated Cypher, and inspect the node relationship visualization.
            </p>
          </aside>

          <ChatWindow messages={messages} answer={answer} cypher={cypher} loading={loading} />
          <ChatInput onSubmit={handleAsk} disabled={loading} />
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
        </div>

        <div className="space-y-6">
          <Sidebar graph={graph} />
          <GraphPanel data={graph} />
        </div>
      </div>
    </Layout>
  )
}
