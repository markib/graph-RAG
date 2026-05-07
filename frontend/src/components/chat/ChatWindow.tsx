import { useEffect, useRef } from 'react'
import type { ChatMessage } from '../../types/graph'
import MessageBubble from './MessageBubble'

type Props = {
  messages: ChatMessage[]
  answer?: string
  cypher?: string
  loading: boolean
}

export default function ChatWindow({ messages, answer, cypher, loading }: Props) {
  const scrollRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, answer, loading])

  return (
    <div className="flex h-full flex-col rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Graph Assistant</h2>
          <p className="text-sm text-slate-500">Ask questions and visualize the Neo4j graph.</p>
        </div>
        {loading && <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">Loading…</span>}
      </div>

      <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto pr-1 pb-2">
        {messages.map((message, index) => (
          <MessageBubble key={`${message.role}-${index}`} message={message} />
        ))}

        {answer ? (
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
            <p className="font-semibold text-slate-900">Generated answer</p>
            <p className="mt-2 whitespace-pre-wrap">{answer}</p>
            {cypher ? (
              <pre className="mt-3 overflow-x-auto rounded-2xl bg-slate-900 p-3 text-xs text-slate-100">
                <code>{cypher}</code>
              </pre>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  )
}
