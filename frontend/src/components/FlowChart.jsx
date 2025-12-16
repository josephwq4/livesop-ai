import { useCallback, useMemo, useEffect, useState, forwardRef, useImperativeHandle } from 'react';
import ReactFlow, {
    MiniMap,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    MarkerType,
    addEdge,
} from 'reactflow';
import 'reactflow/dist/style.css';

import SOPNode from './SOPNode';

const nodeTypes = { sopNode: SOPNode };

const FlowChart = forwardRef(({ workflow, isEditing = false, onNodeSelect }, ref) => {
    // Convert workflow nodes to ReactFlow format
    const createInitialNodes = (wf) => {
        if (!wf || !wf.nodes) return [];
        return wf.nodes.map((node, index) => ({
            id: node.id,
            type: 'sopNode', // Use Custom Node
            data: {
                label: node.label || node.step,
                owner: node.owner,
                auto_run_enabled: node.auto_run_enabled,
                ...node.metadata,
                originalData: node
            },
            position: node.metadata?.position || {
                x: (index % 3) * 300 + 50,
                y: Math.floor(index / 3) * 150 + 50
            },
            // We only need basic dimensions or selection styles here
            style: isEditing ? { cursor: 'grab' } : {},
            draggable: isEditing,
        }));
    };

    const createInitialEdges = (wf) => {
        if (!wf || !wf.edges) return [];
        return wf.edges.map((edge, index) => ({
            id: `edge-${index}`,
            source: edge.source,
            target: edge.target,
            label: edge.label,
            type: 'smoothstep',
            animated: true,
            style: { stroke: '#8b5cf6', strokeWidth: 2 },
            markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' },
        }));
    };

    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    // Resync when workflow changes, only if NOT editing (to prevent overwrites during edit)
    useEffect(() => {
        if (!isEditing && workflow) {
            setNodes(createInitialNodes(workflow));
            setEdges(createInitialEdges(workflow));
        }
    }, [workflow, isEditing]);

    // Expose methods to parent
    useImperativeHandle(ref, () => ({
        getNodes: () => nodes,
        getEdges: () => edges,
        setNodes: setNodes,
        updateNodeData: (id, newData) => {
            setNodes((nds) => nds.map((n) => {
                if (n.id === id) {
                    // Start: Update style background if auto_run changed
                    let style = { ...n.style };
                    if (newData.auto_run_enabled !== undefined) {
                        style.background = newData.auto_run_enabled
                            ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                            : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                    }
                    // End: style update type
                    return { ...n, style, data: { ...n.data, ...newData } };
                }
                return n;
            }));
        },
        removeNode: (id) => {
            setNodes((nds) => nds.filter((n) => n.id !== id));
            setEdges((eds) => eds.filter((e) => e.source !== id && e.target !== id));
        },
        addNode: (nodeType) => {
            const id = `step_${Date.now()}`;
            const newNode = {
                id,
                position: { x: 250, y: 250 },
                data: { label: 'New Action', owner: 'AI Agent', description: 'Describe action...' },
                type: 'default',
                style: {
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    border: '2px dashed #a78bfa',
                    padding: '10px',
                    borderRadius: '12px',
                    minWidth: '200px',
                    cursor: 'grab'
                },
                draggable: true
            };
            setNodes((nds) => [...nds, newNode]);
        }
    }));

    const onConnect = useCallback(
        (params) => setEdges((eds) => addEdge(params, eds)),
        [setEdges]
    );

    const onNodeClick = useCallback((event, node) => {
        if (onNodeSelect) onNodeSelect(node);
    }, [onNodeSelect]);

    if ((!workflow || !workflow.nodes || workflow.nodes.length === 0) && nodes.length === 0) {
        return (
            <div className="w-full h-96 flex items-center justify-center bg-gray-50 dark:bg-gray-900 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-700">
                <p className="text-gray-500 dark:text-gray-400 text-lg">
                    No workflow data available.
                </p>
            </div>
        );
    }

    return (
        <div className={`w-full h-[600px] bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden ${isEditing ? 'ring-2 ring-blue-400' : ''}`}>
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={isEditing ? onConnect : undefined}
                onNodeClick={onNodeClick}
                nodesDraggable={isEditing}
                nodesConnectable={isEditing}
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
                <Background variant="dots" gap={16} size={1} color="#9ca3af" />
            </ReactFlow>
        </div>
    );
});

export default FlowChart;
