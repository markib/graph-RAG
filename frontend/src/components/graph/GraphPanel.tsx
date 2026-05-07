import { useEffect, useRef } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import type { GraphData } from '../../types/graph'

type Props = {
    data: GraphData
}

export default function GraphPanel({ data }: Props) {
    const graphRef = useRef<any>(null)
    const containerRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        graphRef.current?.d3ReheatSimulation()
    }, [data])

    return (
        <div className="flex h-full flex-col rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-4">
                <h2 className="text-lg font-semibold text-slate-900">Graph visualization</h2>
                <p className="text-sm text-slate-500">
                    Explore nodes and relationships in the knowledge graph.
                </p>
            </div>

            {/* 🔥 RESPONSIVE CONTAINER */}
            <div
                ref={containerRef}
                className="h-[560px] w-full overflow-hidden rounded-3xl bg-slate-950"
            >
                <ForceGraph2D
                    ref={graphRef}
                    graphData={data}

                    // 🎯 responsive sizing
                    width={containerRef.current?.clientWidth || 800}
                    height={containerRef.current?.clientHeight || 560}

                    cooldownTicks={120}
                    d3AlphaDecay={0.04}
                    d3VelocityDecay={0.35}

                    nodeRelSize={6}
                    nodeColor={() => "#38bdf8"}

                    linkColor={() => "rgba(148, 163, 184, 0.5)"}
                    linkWidth={1}
                    linkDirectionalParticles={0}

                    nodeLabel={(node: any) =>
                        `${node.id}${node.group ? ` (${node.group})` : ''}`
                    }

                    nodeCanvasObject={(node: any, ctx, globalScale) => {
                        const label = node.id
                        const fontSize = 12 / globalScale

                        const x = node.x || 0
                        const y = node.y || 0

                        ctx.beginPath()
                        ctx.arc(x, y, 5, 0, 2 * Math.PI)
                        ctx.fillStyle = "#38bdf8"
                        ctx.fill()

                        ctx.font = `${fontSize}px Sans-Serif`
                        const textWidth = ctx.measureText(label).width

                        ctx.fillStyle = "rgba(15, 23, 42, 0.85)"
                        ctx.fillRect(x + 8, y - fontSize, textWidth + 8, fontSize + 6)

                        ctx.fillStyle = "#ffffff"
                        ctx.fillText(label, x + 10, y)
                    }}

                    backgroundColor="#0f172a"
                />
            </div>
        </div>
    )
}