import type { GraphData } from '../../types/graph'

type Props = {
  graph: GraphData
}

export default function Sidebar({ graph }: Props) {
  return (
    <aside className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-slate-900">Graph summary</h2>
        <p className="mt-2 text-sm text-slate-500">Live node and relationship counts from the API.</p>
      </div>

      <div className="space-y-4 text-sm text-slate-700">
        <div className="rounded-2xl bg-slate-50 p-4">
          <p className="font-medium text-slate-900">Nodes</p>
          <p className="mt-1 text-3xl font-semibold">{graph.nodes.length}</p>
        </div>
        <div className="rounded-2xl bg-slate-50 p-4">
          <p className="font-medium text-slate-900">Relationships</p>
          <p className="mt-1 text-3xl font-semibold">{graph.links.length}</p>
        </div>
      </div>
    </aside>
  )
}
