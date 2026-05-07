import { useEffect, useRef, useState } from 'react'
import ForceGraph2D, { type ForceGraphMethods, type NodeObject } from 'react-force-graph-2d'
import type { GraphData, GraphNode } from '../../types/graph'

type GraphLinkObject = {
  [others: string]: unknown
  source?: string | number | NodeObject<GraphNode> | undefined
  target?: string | number | NodeObject<GraphNode> | undefined
}

type Props = {
    data: GraphData
}

export default function GraphPanel({ data }: Props) {
    const graphRef = useRef<ForceGraphMethods<NodeObject<GraphNode>, GraphLinkObject> | undefined>(undefined)
    const containerRef = useRef<HTMLDivElement>(null)
    const [dimensions, setDimensions] = useState({ width: 800, height: 560 })

    useEffect(() => {
        const updateDimensions = () => {
            if (containerRef.current) {
                setDimensions({
                    width: containerRef.current.clientWidth,
                    height: containerRef.current.clientHeight
                })
            }
        }
        updateDimensions()
        window.addEventListener('resize', updateDimensions)
        return () => window.removeEventListener('resize', updateDimensions)
    }, [])

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
                    width={dimensions.width}
                    height={dimensions.height}

                    cooldownTicks={120}
                    d3AlphaDecay={0.04}
                    d3VelocityDecay={0.35}

                    nodeRelSize={6}
                    nodeColor={() => "#38bdf8"}

                    linkColor={() => "rgba(148, 163, 184, 0.5)"}
                    linkWidth={1}
                    linkDirectionalParticles={0}

                    nodeLabel={(node: GraphNode) => `${node.id}${node.group ? ` (${node.group})` : ''}`}

                    nodeCanvasObject={(node: NodeObject<GraphNode>, ctx, globalScale) => {
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