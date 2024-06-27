import React, { useState, useCallback } from 'react';
import ReactFlow, {
    ReactFlowProvider,
    addEdge,
    MiniMap,
    Controls,
    Background,
    applyEdgeChanges,
    applyNodeChanges,
} from 'reactflow';

const initialNodes = [
    {
        id: '1',
        type: 'default',
        data: { label: 'Block 1' },
        position: { x: 250, y: 5 },
    },
    {
        id: '2',
        type: 'default',
        data: { label: 'Block 2' },
        position: { x: 100, y: 100 },
    },
    {
        id: '3',
        type: 'default',
        data: { label: 'Block 3' },
        position: { x: 400, y: 100 },
    },
];

const initialEdges = [
    { id: 'e1-2', source: '1', target: '2', animated: true },
    { id: 'e2-3', source: '2', target: '3', animated: true },
];

const BlockDiagram = () => {
    const [nodes, setNodes] = useState(initialNodes);
    const [edges, setEdges] = useState(initialEdges);
    const [editingNodeId, setEditingNodeId] = useState(null);
    const [nodeLabel, setNodeLabel] = useState('');

    const onNodesChange = useCallback(
        (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
        []
    );

    const onEdgesChange = useCallback(
        (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
        []
    );

    const onConnect = useCallback(
        (params) => setEdges((eds) => addEdge(params, eds)),
        []
    );

    const addNode = () => {
        const newNode = {
            id: (nodes.length + 1).toString(),
            type: 'default',
            data: { label: `Block ${nodes.length + 1}` },
            position: { x: Math.random() * 400, y: Math.random() * 400 },
        };
        setNodes((nds) => [...nds, newNode]);
    };

    const handleDoubleClick = (event, node) => {
        event.stopPropagation();
        setEditingNodeId(node.id);
        setNodeLabel(node.data.label);
    };

    const handleInputChange = (event) => {
        setNodeLabel(event.target.value);
    };

    const handleInputBlur = () => {
        updateNodeLabel();
    };

    const handleInputKeyDown = (event) => {
        if (event.key === 'Enter') {
            updateNodeLabel();
        }
    };

    const updateNodeLabel = () => {
        setNodes((nds) =>
            nds.map((node) =>
                node.id === editingNodeId
                    ? { ...node, data: { ...node.data, label: nodeLabel } }
                    : node
            )
        );
        setEditingNodeId(null);
    };

    return (
        <div style={{ height: '100vh' }}>
            <ReactFlowProvider>
                <button onClick={addNode} style={{ position: 'absolute', zIndex: 10 }}>
                    Add Block
                </button>
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    fitView
                    onNodeDoubleClick={handleDoubleClick}
                >
                    <MiniMap />
                    <Controls />
                    <Background />
                </ReactFlow>
                {editingNodeId && (
                    <input
                        style={{
                            position: 'absolute',
                            zIndex: 10,
                            top: nodes.find((node) => node.id === editingNodeId).position.y + 100,
                            left: nodes.find((node) => node.id === editingNodeId).position.x,
                        }}
                        value={nodeLabel}
                        onChange={handleInputChange}
                        onBlur={handleInputBlur}
                        onKeyDown={handleInputKeyDown}
                        autoFocus
                    />
                )}
            </ReactFlowProvider>
        </div>
    );
};

export default BlockDiagram;
