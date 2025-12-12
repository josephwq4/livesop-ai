import { useCallback, useMemo } from 'react';
import ReactFlow, {
    MiniMap,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

const nodeTypes = {};

export default function FlowChart({ workflow }) {
    // Convert workflow nodes to ReactFlow format
    const initialNodes = useMemo(() => {
        if (!workflow || !workflow.nodes) return [];

        return workflow.nodes.map((node, index) => ({
            id: node.id,
            type: 'default',
            data: {
                label: (
                    <div className="px-4 py-2">
                        <div className="font-bold text-sm mb-1">{node.step}</div>
                        <div className="text-xs text-gray-600">{node.owner}</div>
                    </div>
                )
            },
            position: {
                x: (index % 3) * 300 + 50,
                y: Math.floor(index / 3) * 150 + 50
            },
            style: {
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: '2px solid #4c51bf',
                borderRadius: '12px',
                padding: '10px',
                minWidth: '200px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            },
        }));
    }, [workflow]);

    const initialEdges = useMemo(() => {
        if (!workflow || !workflow.edges) return [];

        return workflow.edges.map((edge, index) => ({
            id: `edge-${index}`,
            source: edge.source,
            target: edge.target,
            label: edge.label,
            type: 'smoothstep',
            animated: true,
            style: { stroke: '#8b5cf6', strokeWidth: 2 },
            markerEnd: {
                type: MarkerType.ArrowClosed,
                color: '#8b5cf6',
            },
            labelStyle: {
                fill: '#6b7280',
                fontWeight: 600,
                fontSize: '12px',
            },
            labelBgStyle: {
                fill: '#f3f4f6',
                fillOpacity: 0.9,
                borderRadius: '4px',
            },
        }));
    }, [workflow]);

    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

    const onConnect = useCallback(
        (params) => setEdges((eds) => [...eds, params]),
        [setEdges]
    );

    if (!workflow || !workflow.nodes || workflow.nodes.length === 0) {
        return (
            <div className="w-full h-96 flex items-center justify-center bg-gray-50 dark:bg-gray-900 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-700">
                <p className="text-gray-500 dark:text-gray-400 text-lg">
                    No workflow data available. Run inference to generate workflow.
                </p>
            </div>
        );
    }

    return (
        <div className="w-full h-[600px] bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                nodeTypes={nodeTypes}
                fitView
                attributionPosition="bottom-left"
            >
                <Controls className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-md" />
                <MiniMap
                    className="bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-md"
                    nodeColor="#8b5cf6"
                    maskColor="rgba(0, 0, 0, 0.1)"
                />
                <Background
                    variant="dots"
                    gap={16}
                    size={1}
                    color="#9ca3af"
                />
            </ReactFlow>
        </div>
    );
}
